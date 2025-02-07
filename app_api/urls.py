from django.urls import path
from . import views

from rest_framework import routers
router = routers.SimpleRouter()

urlpatterns = [
    path('products/', views.ProductsView.as_view(), name='products'),
    path('products/<slug:category_slug>', views.CategoryProductsView.as_view(), name='category'),
    path('products/<slug:category_slug>/<slug:product_slug>', views.ProductView.as_view(), name='product'),
    path('categories/', views.CategoryView.as_view(), name='categories'),
    path('register/', views.RegisterView.as_view(), name='register'),
    path('add-to-cart/', views.AddToCartView.as_view(), name='add_to_cart'),
    path('remove-from-cart/', views.RemoveFromCartView.as_view(), name='remove_from_cart'),
    path('cart/', views.CartView.as_view(), name='cart'),
    path('checkout/', views.CheckoutView.as_view(), name='checkout'),
    path('profile/', views.ProfileView.as_view(), name='profile'),
    # path('profile/update/', views.ProfileUpdate.as_view(), name="profile_update"),
    # path('profile/change-password/', views.ChangePassword.as_view(), name="profile_change_password"),
    path('profile/addresses/', views.AddressesView.as_view(), name="profile_address"),
    path('profile/orders/', views.OrdersView.as_view(), name="profile_orders"),
    # path('profile/orders/<slug:order_id>', views.OrderDetails.as_view, name="profile_order_detail"),
    path('csrf-token/', views.get_csrf_token, name="csrf_token")
]
