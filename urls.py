from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include, path

urlpatterns = [
    # Django's built-in admin is kept at a separate, non-obvious path and is
    # NOT the store-owner dashboard used in this prototype (see store/urls.py
    # "dashboard" namespace, protected by store.decorators.staff_required).
    path('django-admin/', admin.site.urls),
    path('', include('store.urls')),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
