from django.urls import path
from .views import (
    IndexView,ProductDetailView,
    profile,register_view, login_view, logout_view,sync_products_from_api
)

app_name = "bensryaa"

urlpatterns = [
    path("sync-products/", sync_products_from_api, name="sync_products"),

    # 🔑 Auth custom
    path("register/", register_view, name="register"),
    path("login/", login_view, name="login"),
    path("logout/", logout_view, name="logout"),
    path("profile/", profile, name="profile"),

    # Produk & order
    path("", IndexView.as_view(), name="index"),
    path("product/<int:pk>/", ProductDetailView.as_view(), name="product_detail"),

]
