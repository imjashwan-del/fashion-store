from django.conf import settings
from django.contrib.auth.models import User
from django.core.management.base import BaseCommand
from django.utils.text import slugify

from store.models import Category, Product, StoreConfig


CATEGORIES = ['Men', 'Women', 'Kids', 'New Arrivals', 'Festive Collection']

PRODUCTS = [
    ('Classic Black Shirt', 'Men', 1299, 18, True),
    ('Premium White Shirt', 'Men', 1399, 14, True),
    ('Relaxed Fit Jeans', 'Men', 1899, 20, False),
    ('Denim Jacket', 'Men', 2799, 8, True),
    ('Traditional Kurta', 'Festive Collection', 1699, 12, True),
    ('Festive Kurti', 'Women', 1499, 15, True),
    ('Cotton Saree', 'Women', 2199, 10, False),
    ('Party Wear Dress', 'Women', 2999, 6, True),
    ('Casual T-Shirt', 'New Arrivals', 699, 30, False),
    ('Kids Festive Set', 'Kids', 1199, 0, True),
    ('Kids Casual Co-ord', 'Kids', 999, 16, False),
    ('Embroidered Anarkali', 'Festive Collection', 3299, 5, True),
]


class Command(BaseCommand):
    help = 'Seeds demo categories, products, store settings, and an admin user for local testing.'

    def handle(self, *args, **options):
        store = StoreConfig.load()
        is_first_seed = store.shop_name == StoreConfig._meta.get_field('shop_name').default
        if is_first_seed:
            defaults = settings.STORE_DEFAULTS
            store.shop_name = defaults['SHOP_NAME']
            store.tagline = defaults['TAGLINE']
            store.phone = defaults['PHONE']
            store.address = defaults['ADDRESS']
            store.instagram_url = defaults['INSTAGRAM']
            store.instagram_handle = defaults['INSTAGRAM_HANDLE']
            store.owner_name = defaults['OWNER_NAME']
            store.founded_year = defaults['FOUNDED_YEAR']
            store.opening_hours = defaults['OPENING_HOURS']
            store.about_text = defaults['ABOUT_TEXT'].format(
                year=defaults['FOUNDED_YEAR'], shop=defaults['SHOP_NAME']
            )
            store.store_latitude = defaults['STORE_LATITUDE']
            store.store_longitude = defaults['STORE_LONGITUDE']
            store.delivery_radius_km = defaults['DELIVERY_RADIUS_KM']
            store.save()
            self.stdout.write(self.style.SUCCESS('Applied STORE_DEFAULTS from settings.py.'))
        else:
            self.stdout.write('Store settings already customized, left untouched.')

        cat_objs = {}
        for i, name in enumerate(CATEGORIES):
            cat, _ = Category.objects.get_or_create(
                name=name, defaults={'slug': slugify(name), 'display_order': i}
            )
            cat_objs[name] = cat
        self.stdout.write(self.style.SUCCESS(f'Categories ready: {", ".join(CATEGORIES)}'))

        for name, cat_name, price, stock, featured in PRODUCTS:
            Product.objects.get_or_create(
                name=name,
                defaults={
                    'slug': slugify(name),
                    'description': (
                        f'{name} - a demo product for prototype purposes. '
                        'Crafted with quality fabric and finished for everyday elegance.'
                    ),
                    'price': price,
                    'category': cat_objs[cat_name],
                    'stock_quantity': stock,
                    'is_featured': featured,
                },
            )
        self.stdout.write(self.style.SUCCESS(f'{len(PRODUCTS)} demo products ready.'))

        if not User.objects.filter(username='owner').exists():
            User.objects.create_superuser('owner', 'owner@example.com', 'ChangeThisPassword123')
            self.stdout.write(self.style.SUCCESS(
                'Demo admin user created -> username: owner / password: ChangeThisPassword123 '
                '(CHANGE THIS before showing the demo to anyone).'
            ))
        else:
            self.stdout.write('Admin user "owner" already exists, skipped.')

        self.stdout.write(self.style.SUCCESS('Seed complete.'))
