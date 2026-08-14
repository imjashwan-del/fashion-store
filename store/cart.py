from decimal import Decimal

from .models import Product

SESSION_KEY = 'cart'


class Cart:
    """A simple session-backed cart: {product_id (str): quantity (int)}."""

    def __init__(self, request):
        self.session = request.session
        cart = self.session.get(SESSION_KEY)
        if cart is None:
            cart = self.session[SESSION_KEY] = {}
        self.cart = cart

    def add(self, product, quantity=1):
        pid = str(product.id)
        max_qty = product.stock_quantity
        current = self.cart.get(pid, 0)
        new_qty = min(current + quantity, max_qty) if max_qty else 0
        if new_qty < 1:
            return False
        self.cart[pid] = new_qty
        self.save()
        return True

    def set_quantity(self, product, quantity):
        pid = str(product.id)
        quantity = max(0, min(quantity, product.stock_quantity))
        if quantity == 0:
            self.remove(product)
        else:
            self.cart[pid] = quantity
            self.save()

    def remove(self, product):
        pid = str(product.id)
        if pid in self.cart:
            del self.cart[pid]
            self.save()

    def clear(self):
        self.session[SESSION_KEY] = {}
        self.save()

    def save(self):
        self.session.modified = True

    def __len__(self):
        return sum(self.cart.values())

    def __iter__(self):
        product_ids = self.cart.keys()
        products = Product.objects.filter(id__in=product_ids)
        products_map = {str(p.id): p for p in products}
        for pid, qty in self.cart.items():
            product = products_map.get(pid)
            if not product:
                continue
            yield {
                'product': product,
                'quantity': qty,
                'subtotal': product.price * qty,
            }

    def get_total(self):
        return sum((item['subtotal'] for item in self), Decimal('0'))

    def is_empty(self):
        return len(self.cart) == 0
