from django.urls import path
from .views import IndexView, ProductDetailView ,CreateOrderView, OrderListView, OrderDetailView

app_name = "bensryaa"

urlpatterns = [
    path('', IndexView.as_view(), name='index'),
    path('product/<slug:slug>/', ProductDetailView.as_view(), name='product_detail'),
    path('product/<slug:slug>/buy/', CreateOrderView.as_view(), name='create_order'),
    path('orders/', OrderListView.as_view(), name='order_list'),
    path('order/<int:pk>/', OrderDetailView.as_view(), name='order_detail'),
]
