from django.urls import include, path

from . import views

app_name = 'store'

storefront_patterns = [
    path('', views.home, name='home'),
    path('shop/', views.shop, name='shop'),
    path('product/<slug:slug>/', views.product_detail, name='product_detail'),
    path('cart/', views.cart_view, name='cart'),
    path('cart/add/<int:product_id>/', views.add_to_cart, name='add_to_cart'),
    path('cart/update/<int:product_id>/', views.update_cart, name='update_cart'),
    path('checkout/', views.checkout, name='checkout'),
    path('order/<str:order_number>/confirmation/', views.order_confirmation, name='order_confirmation'),
    path('about/', views.about, name='about'),
]

dashboard_patterns = [
    path('login/', views.dashboard_login, name='login'),
    path('logout/', views.dashboard_logout, name='logout'),
    path('', views.dashboard_home, name='home'),
    path('orders/', views.dashboard_orders, name='orders'),
    path('orders/<str:order_number>/', views.dashboard_order_detail, name='order_detail'),
    path('products/', views.dashboard_products, name='products'),
    path('products/add/', views.dashboard_product_form, name='product_add'),
    path('products/<int:product_id>/edit/', views.dashboard_product_form, name='product_edit'),
    path('products/<int:product_id>/delete/', views.dashboard_product_delete, name='product_delete'),
    path('categories/', views.dashboard_categories, name='categories'),
    path('categories/<int:category_id>/delete/', views.dashboard_category_delete, name='category_delete'),
    path('settings/', views.dashboard_settings, name='settings'),
]

urlpatterns = storefront_patterns + [
    path('admin-dashboard/', include((dashboard_patterns, 'dashboard'))),
]
