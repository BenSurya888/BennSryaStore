from django.urls import path
from .views import (
    IndexView,ProductDetailView,
    profile,register_view, login_view, logout_view,sync_products_from_api,admin_dashboard,payment_page,create_order,update_order_status,transaction_history
)

app_name = "bensryaa"

urlpatterns = [
    path("sync-products/", sync_products_from_api, name="sync_products_from_api"),

    # 🔑 Auth custom
    path("register/", register_view, name="register"),
    path("login/", login_view, name="login"),
    path("logout/", logout_view, name="logout"),
    path("profile/", profile, name="profile"),
    path("admin-dashboard/", admin_dashboard, name="admin_dashboard"),
    path("transactions/", transaction_history, name="transaction_history"),
    # Produk & order
    path("", IndexView.as_view(), name="index"),
    path("product/<int:pk>/", ProductDetailView.as_view(), name="product_detail"),
    path("order/create/", create_order, name="create_order"),
    path("order/<int:order_id>/update/", update_order_status, name="update_order_status"),
    path("payment/<int:order_id>/", payment_page, name="payment_page"),

]
