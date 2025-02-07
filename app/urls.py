from django.urls import path
from django.views.generic import RedirectView, TemplateView
from . import views


urlpatterns = [
    path('', views.home, name="home"),
    path('products/', views.products, name="products"),
    path('products/<slug:category_slug>', views.category, name="category"),
    path('products/<slug:category_slug>/<slug:product_slug>', views.product, name="product"),
    path('about/', TemplateView.as_view(template_name="about.html"), name="about"),
    path('contact/', views.contact, name="contact"),
    path('cart/', views.cart, name="cart"),
    path('checkout/', views.checkout, name="checkout"),
    path('sign-in/', views.sign_in, name="signin"),
    path('sign-up/', views.sign_up, name="signup"),
    path('sign-out/', views.sign_out, name="signout"),
    path('profile/', views.profile, name="profile"),
    path('profile/update/', views.profile_update, name="profile_update"),
    path('profile/change-password/', views.profile_change_password, name="profile_change_password"),
    path('profile/address/', views.profile_address, name="profile_address"),
    path('profile/order/', views.profile_order, name="profile_order"),
    path('profile/order/<slug:order_id>', views.profile_order_detail, name="profile_order_detail"),
]
