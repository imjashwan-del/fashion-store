from django.contrib import messages
from django.contrib.auth import login as auth_login
from django.contrib.auth import logout as auth_logout
from django.contrib.auth.forms import AuthenticationForm
from django.db import transaction
from django.db.models import Count, Q, Sum
from django.shortcuts import get_object_or_404, redirect, render
from django.utils.text import slugify
from django.views.decorators.http import require_POST

from .cart import Cart
from .decorators import staff_required
from .forms import CategoryForm, CheckoutForm, ProductForm, StoreConfigForm
from .models import Category, Order, OrderItem, Product, StoreConfig
from .utils import is_within_delivery_radius

# ============================================================================
# PUBLIC STOREFRONT
# ============================================================================


def home(request):
    categories = Category.objects.all()[:5]
    featured_products = Product.objects.filter(is_active=True, is_featured=True)[:12]
    if featured_products.count() < 4:
        featured_products = Product.objects.filter(is_active=True)[:12]
    store = StoreConfig.load()
    return render(request, 'store/home.html', {
        'categories': categories,
        'featured_products': featured_products,
        'store': store,
    })


def shop(request):
    products = Product.objects.filter(is_active=True)
    categories = Category.objects.all()

    category_slug = request.GET.get('category')
    selected_category = None
    if category_slug:
        selected_category = get_object_or_404(Category, slug=category_slug)
        products = products.filter(category=selected_category)

    query = request.GET.get('q')
    if query:
        products = products.filter(Q(name__icontains=query) | Q(description__icontains=query))

    return render(request, 'store/shop.html', {
        'products': products,
        'categories': categories,
        'selected_category': selected_category,
        'query': query or '',
    })


def product_detail(request, slug):
    product = get_object_or_404(Product, slug=slug, is_active=True)
    related = Product.objects.filter(category=product.category, is_active=True).exclude(id=product.id)[:4]
    return render(request, 'store/product_detail.html', {'product': product, 'related': related})


@require_POST
def add_to_cart(request, product_id):
    product = get_object_or_404(Product, id=product_id, is_active=True)
    try:
        quantity = int(request.POST.get('quantity', 1))
    except (TypeError, ValueError):
        quantity = 1
    quantity = max(1, quantity)

    cart = Cart(request)
    if not product.in_stock:
        messages.error(request, f'"{product.name}" is currently unavailable.')
    elif not cart.add(product, quantity):
        messages.error(request, f'Only {product.stock_quantity} unit(s) of "{product.name}" available.')
    else:
        messages.success(request, f'"{product.name}" added to your cart.')

    next_url = request.POST.get('next') or 'store:cart'
    return redirect(next_url)


def cart_view(request):
    cart = Cart(request)
    return render(request, 'store/cart.html', {'cart': cart})


@require_POST
def update_cart(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    cart = Cart(request)
    action = request.POST.get('action')

    if action == 'remove':
        cart.remove(product)
        messages.info(request, f'"{product.name}" removed from cart.')
    else:
        try:
            quantity = int(request.POST.get('quantity', 1))
        except (TypeError, ValueError):
            quantity = 1
        cart.set_quantity(product, quantity)

    return redirect('store:cart')


def checkout(request):
    cart = Cart(request)
    store = StoreConfig.load()

    if cart.is_empty():
        messages.info(request, 'Your cart is empty. Add something you love first!')
        return redirect('store:shop')

    if request.method == 'POST':
        form = CheckoutForm(request.POST)
        if form.is_valid():
            lat = form.cleaned_data.get('latitude')
            lng = form.cleaned_data.get('longitude')

            # --- Real server-side delivery-radius validation ---
            # We only trust coordinates captured by the browser's own
            # Geolocation API (see templates/store/checkout.html +
            # static/store/js/geolocation.js). A typed address/PIN code is
            # never used to infer distance -- see store/utils.py for why.
            if lat is None or lng is None:
                messages.error(
                    request,
                    "We couldn't verify your delivery location. Please allow location "
                    "access in your browser and try again, or call the store directly "
                    "to place your order."
                )
                return render(request, 'store/checkout.html', {
                    'cart': cart, 'form': form, 'store': store,
                })

            within_radius, distance_km = is_within_delivery_radius(lat, lng, store)
            if not within_radius:
                messages.error(
                    request,
                    f'Sorry, online delivery is currently available only within '
                    f'{store.delivery_radius_km:g} km of our store. '
                    f'Your location is about {distance_km} km away.'
                )
                return render(request, 'store/checkout.html', {
                    'cart': cart, 'form': form, 'store': store,
                })

            # --- Re-validate stock server-side right before saving ---
            for item in cart:
                if item['quantity'] > item['product'].stock_quantity:
                    messages.error(
                        request,
                        f'Sorry, only {item["product"].stock_quantity} unit(s) of '
                        f'"{item["product"].name}" are left in stock.'
                    )
                    return render(request, 'store/checkout.html', {
                        'cart': cart, 'form': form, 'store': store,
                    })

            with transaction.atomic():
                order = Order.objects.create(
                    customer_name=form.cleaned_data['full_name'],
                    phone=form.cleaned_data['phone'],
                    address=form.cleaned_data['address'],
                    city=form.cleaned_data['city'],
                    pincode=form.cleaned_data['pincode'],
                    customer_latitude=lat,
                    customer_longitude=lng,
                    distance_km=distance_km,
                    total_amount=cart.get_total(),
                )
                for item in cart:
                    product = item['product']
                    OrderItem.objects.create(
                        order=order,
                        product=product,
                        product_name=product.name,
                        quantity=item['quantity'],
                        price=product.price,
                    )
                    # Prevent negative / over-sold stock at the DB level.
                    product.stock_quantity = max(0, product.stock_quantity - item['quantity'])
                    product.save(update_fields=['stock_quantity'])

            cart.clear()
            return redirect('store:order_confirmation', order_number=order.order_number)
    else:
        form = CheckoutForm()

    return render(request, 'store/checkout.html', {'cart': cart, 'form': form, 'store': store})


def order_confirmation(request, order_number):
    # Intentionally looked up ONLY via the session-created redirect flow.
    # There is no public "enter your order number" lookup page (see
    # security brief section 5: Order Privacy) -- this page is reachable
    # right after checkout via redirect, and does not expose any link or
    # form for browsing other orders.
    order = get_object_or_404(Order, order_number=order_number)
    return render(request, 'store/order_confirmation.html', {'order': order})


def about(request):
    # The full "About the Store" section lives on the homepage (see
    # store/home.html #about) so it sits alongside the gallery and
    # Instagram sections as specified. This route exists for a clean,
    # memorable /about/ link (e.g. from Instagram bio) and just jumps there.
    return redirect('/#about')


# ============================================================================
# OWNER DASHBOARD  (every view below requires staff_required)
# ============================================================================


def dashboard_login(request):
    if request.user.is_authenticated and request.user.is_staff:
        return redirect('dashboard:home')

    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            if not user.is_staff:
                messages.error(request, 'This account does not have store management access.')
            else:
                auth_login(request, user)
                return redirect('dashboard:home')
    else:
        form = AuthenticationForm(request)

    return render(request, 'dashboard/login.html', {'form': form})


def dashboard_logout(request):
    auth_logout(request)
    return redirect('dashboard:login')


@staff_required
def dashboard_home(request):
    orders = Order.objects.all()
    stats = {
        'total_orders': orders.count(),
        'new_orders': orders.filter(status=Order.STATUS_NEW).count(),
        'confirmed_orders': orders.filter(status=Order.STATUS_CONFIRMED).count(),
        'completed_orders': orders.filter(status=Order.STATUS_COMPLETED).count(),
        'total_sales': orders.filter(status=Order.STATUS_COMPLETED).aggregate(s=Sum('total_amount'))['s'] or 0,
        'total_products': Product.objects.count(),
        'low_stock': Product.objects.filter(stock_quantity__lte=3, stock_quantity__gt=0).count(),
        'out_of_stock': Product.objects.filter(stock_quantity=0).count(),
    }
    recent_orders = orders[:8]
    return render(request, 'dashboard/dashboard.html', {'stats': stats, 'recent_orders': recent_orders, 'active': 'home'})


@staff_required
def dashboard_orders(request):
    orders = Order.objects.all().prefetch_related('items')
    status_filter = request.GET.get('status')
    if status_filter in dict(Order.STATUS_CHOICES):
        orders = orders.filter(status=status_filter)
    return render(request, 'dashboard/orders.html', {
        'orders': orders,
        'status_filter': status_filter or '',
        'status_choices': Order.STATUS_CHOICES,
        'active': 'orders',
    })


@staff_required
def dashboard_order_detail(request, order_number):
    order = get_object_or_404(Order, order_number=order_number)
    if request.method == 'POST':
        new_status = request.POST.get('status')
        if new_status in dict(Order.STATUS_CHOICES):
            order.status = new_status
            order.save(update_fields=['status'])
            messages.success(request, f'Order {order.order_number} marked as {order.get_status_display()}.')
            return redirect('dashboard:order_detail', order_number=order.order_number)
    return render(request, 'dashboard/order_detail.html', {'order': order, 'active': 'orders'})


@staff_required
def dashboard_products(request):
    products = Product.objects.all().select_related('category')
    return render(request, 'dashboard/products.html', {'products': products, 'active': 'products'})


@staff_required
def dashboard_product_form(request, product_id=None):
    product = get_object_or_404(Product, id=product_id) if product_id else None
    if request.method == 'POST':
        form = ProductForm(request.POST, request.FILES, instance=product)
        if form.is_valid():
            obj = form.save(commit=False)
            if not obj.slug:
                obj.slug = slugify(obj.name)
            obj.save()
            messages.success(request, f'Product "{obj.name}" saved.')
            return redirect('dashboard:products')
    else:
        initial = {}
        form = ProductForm(instance=product, initial=initial)
    return render(request, 'dashboard/product_form.html', {'form': form, 'product': product, 'active': 'products'})


@staff_required
@require_POST
def dashboard_product_delete(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    name = product.name
    product.delete()
    messages.success(request, f'Product "{name}" deleted.')
    return redirect('dashboard:products')


@staff_required
def dashboard_categories(request):
    categories = Category.objects.annotate(product_count=Count('products'))
    if request.method == 'POST':
        form = CategoryForm(request.POST, request.FILES)
        if form.is_valid():
            cat = form.save(commit=False)
            if not cat.slug:
                cat.slug = slugify(cat.name)
            cat.save()
            messages.success(request, f'Category "{cat.name}" added.')
            return redirect('dashboard:categories')
    else:
        form = CategoryForm()
    return render(request, 'dashboard/categories.html', {'categories': categories, 'form': form, 'active': 'categories'})


@staff_required
@require_POST
def dashboard_category_delete(request, category_id):
    category = get_object_or_404(Category, id=category_id)
    name = category.name
    category.delete()
    messages.success(request, f'Category "{name}" deleted.')
    return redirect('dashboard:categories')


@staff_required
def dashboard_settings(request):
    store = StoreConfig.load()
    if request.method == 'POST':
        form = StoreConfigForm(request.POST, request.FILES, instance=store)
        if form.is_valid():
            form.save()
            messages.success(request, 'Store settings updated.')
            return redirect('dashboard:settings')
    else:
        form = StoreConfigForm(instance=store)
    return render(request, 'dashboard/settings.html', {'form': form, 'store': store, 'active': 'settings'})
