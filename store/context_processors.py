from .cart import Cart
from .models import StoreConfig


def store_config(request):
    """Makes {{ store }} (the single StoreConfig row) available everywhere."""
    return {'store': StoreConfig.load()}


def cart_count(request):
    """Makes {{ cart_count }} available everywhere (navbar cart badge)."""
    return {'cart_count': len(Cart(request))}
