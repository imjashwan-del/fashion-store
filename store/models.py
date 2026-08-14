import uuid

from django.conf import settings
from django.core.validators import MinValueValidator
from django.db import models
from django.urls import reverse
from django.utils import timezone


class StoreConfig(models.Model):
    """
    Single-row table holding everything about THIS shop: name, contact
    details, story, images, and delivery settings. Editing this one row
    (via the owner dashboard -> Store Settings) re-skins the entire site.
    This is what makes the project reusable for a different clothing shop
    without touching any template or Python code.
    """

    shop_name = models.CharField(max_length=120, default='Demo Fashion Store')
    tagline = models.CharField(max_length=200, default='Style That Speaks For You')
    hero_subtext = models.CharField(
        max_length=300,
        default='Discover our latest collection of fashion, curated for every occasion.',
    )

    phone = models.CharField(max_length=30, default='+91 90000 00000')
    address = models.CharField(max_length=255, default='Store Address, City, State, PIN')
    instagram_url = models.URLField(default='https://instagram.com/')
    instagram_handle = models.CharField(max_length=60, default='@demofashionstore')

    owner_name = models.CharField(max_length=120, default='Store Owner')
    founded_year = models.PositiveIntegerField(default=2015)
    opening_hours = models.CharField(
        max_length=255, default='Mon - Sat: 10:00 AM - 9:00 PM  |  Sun: 11:00 AM - 7:00 PM'
    )
    about_text = models.TextField(
        default=(
            'Since 2015, Demo Fashion Store has been serving our community with '
            'carefully selected fashion for every occasion. From everyday essentials '
            'to festive collections, we focus on quality, style and personal service.'
        )
    )

    festive_offer_title = models.CharField(max_length=120, default='FESTIVE SPECIAL', blank=True)
    festive_offer_text = models.CharField(
        max_length=255,
        default='Shop for \u20b91,000 or more and receive a complimentary Rakhi & Sweet.',
        blank=True,
    )
    festive_offer_active = models.BooleanField(default=True)

    # Images -- optional uploads. Templates fall back to a styled placeholder
    # block (see base.html {% include %}) if these are empty, so the demo
    # always looks intentional even before real photos are uploaded.
    logo = models.ImageField(upload_to='store_config/', blank=True, null=True)
    hero_image = models.ImageField(upload_to='store_config/', blank=True, null=True)
    owner_image = models.ImageField(upload_to='store_config/', blank=True, null=True)
    store_exterior_image = models.ImageField(upload_to='store_config/', blank=True, null=True)
    store_interior_image = models.ImageField(upload_to='store_config/', blank=True, null=True)
    new_collection_image = models.ImageField(upload_to='store_config/', blank=True, null=True)
    festival_display_image = models.ImageField(upload_to='store_config/', blank=True, null=True)

    # --- Delivery radius configuration (see store/utils.py:haversine_km) ---
    store_latitude = models.FloatField(default=17.2473)
    store_longitude = models.FloatField(default=80.1514)
    delivery_radius_km = models.FloatField(default=10.0)

    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Store configuration'
        verbose_name_plural = 'Store configuration'

    def __str__(self):
        return self.shop_name

    def save(self, *args, **kwargs):
        # Enforce a true singleton: there is only ever one StoreConfig row.
        self.pk = 1
        super().save(*args, **kwargs)

    @classmethod
    def load(cls):
        obj, _ = cls.objects.get_or_create(pk=1)
        return obj


class Category(models.Model):
    name = models.CharField(max_length=100, unique=True)
    slug = models.SlugField(max_length=120, unique=True)
    image = models.ImageField(upload_to='categories/', blank=True, null=True)
    description = models.CharField(max_length=255, blank=True)
    display_order = models.PositiveIntegerField(default=0)

    class Meta:
        verbose_name_plural = 'Categories'
        ordering = ['display_order', 'name']

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse('store:shop') + f'?category={self.slug}'


class Product(models.Model):
    name = models.CharField(max_length=150)
    slug = models.SlugField(max_length=170, unique=True)
    description = models.TextField(blank=True)
    price = models.DecimalField(max_digits=10, decimal_places=2, validators=[MinValueValidator(0)])
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True, related_name='products')
    stock_quantity = models.PositiveIntegerField(default=0)
    image = models.ImageField(upload_to='products/', blank=True, null=True)
    is_featured = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse('store:product_detail', args=[self.slug])

    @property
    def in_stock(self):
        return self.stock_quantity > 0


class Order(models.Model):
    STATUS_NEW = 'new'
    STATUS_CONFIRMED = 'confirmed'
    STATUS_COMPLETED = 'completed'
    STATUS_CHOICES = [
        (STATUS_NEW, 'New'),
        (STATUS_CONFIRMED, 'Confirmed'),
        (STATUS_COMPLETED, 'Completed'),
    ]

    order_number = models.CharField(max_length=20, unique=True, editable=False)

    # Customer / delivery information
    customer_name = models.CharField(max_length=120)
    phone = models.CharField(max_length=20)
    address = models.CharField(max_length=255)
    city = models.CharField(max_length=100)
    pincode = models.CharField(max_length=10)

    # Real, device-reported coordinates captured via the browser Geolocation
    # API on the checkout page (see static/store/js/geolocation.js) and
    # verified server-side against StoreConfig using the Haversine formula
    # (store/utils.py). Nothing here is inferred from a typed address or
    # PIN code -- if these are blank, the distance was never verified.
    customer_latitude = models.FloatField(null=True, blank=True)
    customer_longitude = models.FloatField(null=True, blank=True)
    distance_km = models.FloatField(null=True, blank=True)

    total_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default=STATUS_NEW)

    created_at = models.DateTimeField(default=timezone.now)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return self.order_number

    def save(self, *args, **kwargs):
        if not self.order_number:
            self.order_number = 'ORD-' + uuid.uuid4().hex[:8].upper()
        super().save(*args, **kwargs)


class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='items')
    product = models.ForeignKey(Product, on_delete=models.SET_NULL, null=True)
    product_name = models.CharField(max_length=150)  # snapshot, survives product deletion
    quantity = models.PositiveIntegerField(default=1)
    price = models.DecimalField(max_digits=10, decimal_places=2)  # price snapshot at order time

    @property
    def subtotal(self):
        return self.price * self.quantity

    def __str__(self):
        return f'{self.product_name} x {self.quantity}'
