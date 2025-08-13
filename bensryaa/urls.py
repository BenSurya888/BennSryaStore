from django.urls import path,include
from .views import IndexView, ProductDetailView ,CreateOrderView, OrderListView, OrderDetailView,transaction_history,check_order,add_to_cart,remove_from_cart,profile,register,login,sync_products_dummy

app_name = "bensryaa"

urlpatterns = [
    path("admin/sync-products-dummy/", sync_products_dummy, name="sync_products_dummy"),
    path('accounts/', include('django.contrib.auth.urls')),  # auth bawaan Django
    path("register/", register, name="register"),
    path("login/", login, name="login"),
    path("transaction_history/", transaction_history, name="transaction_history"),
    path("check_order/", check_order, name="check_order"),
    path("add-to-cart/<slug:slug>/", add_to_cart, name="add_to_cart"),
    path("remove-from-cart/<int:pk>/", remove_from_cart, name="remove_from_cart"),
    path("profile/", profile, name="profile"),
    path('', IndexView.as_view(), name='index'),
    path('product/<slug:slug>/', ProductDetailView.as_view(), name='product_detail'),
    path('product/<slug:slug>/buy/', CreateOrderView.as_view(), name='create_order'),
    path('orders/', OrderListView.as_view(), name='order_list'),
    path('order/<int:pk>/', OrderDetailView.as_view(), name='order_detail'),
]
