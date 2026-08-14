"""
Delivery-radius geolocation utilities.

Design note (see project brief "CRITICAL - DELIVERY AND ADMIN ACCESS RULES"):
The store only delivers within a configurable radius (default 10 km) of its
physical location. We do NOT fake this by trusting a typed PIN code or city
name as a proxy for distance -- PIN codes cover multi-kilometre areas and a
customer could type anything.

Instead, checkout captures the customer's REAL coordinates using the
browser's HTML5 Geolocation API (static/store/js/geolocation.js), and this
module computes the true great-circle distance between those coordinates and
the store's configured coordinates using the Haversine formula. That result
is what the server trusts -- never the client's claim about the result.

Prototype limitation (clearly labeled, not hidden): this project does not
include an address-to-coordinate geocoding service (e.g. Google Geocoding
API), because that requires a paid API key the shop owner would need to
provide. If a customer denies the browser's location permission, we cannot
verify their distance, and the checkout view intentionally refuses to
guess -- it blocks the online order and asks the customer to enable location
or contact the store directly (see store/views.py: checkout()). The
architecture (this function + the lat/lng fields already on Order and
StoreConfig) is ready to plug a real geocoding service in later: swap the
browser-geolocation call for a geocode_address(address, city, pincode) call
that returns (lat, lng), and everything downstream keeps working unchanged.
"""

import math


def haversine_km(lat1, lon1, lat2, lon2):
    """Great-circle distance in kilometres between two lat/lng points."""
    R = 6371.0  # Earth's radius in km
    phi1, phi2 = math.radians(lat1), math.radians(lat2)
    d_phi = math.radians(lat2 - lat1)
    d_lambda = math.radians(lon2 - lon1)

    a = (
        math.sin(d_phi / 2) ** 2
        + math.cos(phi1) * math.cos(phi2) * math.sin(d_lambda / 2) ** 2
    )
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    return R * c


def is_within_delivery_radius(customer_lat, customer_lng, store_config):
    """
    Returns (is_within, distance_km) using the store's configured location
    and radius. Requires real customer_lat/customer_lng -- callers must not
    invoke this with guessed or placeholder coordinates.
    """
    distance = haversine_km(
        store_config.store_latitude,
        store_config.store_longitude,
        customer_lat,
        customer_lng,
    )
    return distance <= store_config.delivery_radius_km, round(distance, 2)
