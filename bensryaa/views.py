from django.views.generic import ListView, DetailView
from .models import Product
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.views import View
from django.views.generic import ListView, DetailView
from .models import Product, ProductVariant, Order
from .forms import CheckoutForm
from django.conf import settings
import requests

def get_product_data():
    url = "https://api.digiflazz.com/v1/product"
    headers = {
        "Authorization": f"Bearer {settings.DIGIFLAZZ_API_KEY}"
    }
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        return response.json()
    else:
        return None


class ProductDetailView(DetailView):
    model = Product
    template_name = "store/product_detail.html"

class CreateOrderView(View):
    def post(self, request, slug):
        product = get_object_or_404(Product, slug=slug)

        variant_id = request.POST.get("variant")
        variant = None
        price = None
        variant_name = ""

        if variant_id:
            variant = ProductVariant.objects.filter(pk=variant_id, product=product).first()
            if variant:
                price = variant.price
                variant_name = variant.name

        if price is None:
            price = product.price or 0

        # simpan input tambahan sesuai tipe produk
        extra_data = {}
        if product.extra_input_type == "game_id_server":
            extra_data["game_user_id"] = request.POST.get("game_user_id", "")
            extra_data["server_id"] = request.POST.get("server_id", "")
        elif product.extra_input_type == "phone_number":
            extra_data["game_user_id"] = request.POST.get("phone_number", "")
        elif product.extra_input_type == "email":
            extra_data["game_user_id"] = request.POST.get("email", "")
        elif product.extra_input_type == "custom":
            extra_data["game_user_id"] = request.POST.get("custom_input", "")

        order = Order.objects.create(
            user=request.user if request.user.is_authenticated else None,
            product=product,
            variant=variant,
            price=price,
            variant_name=variant_name,
            payment_method=request.POST.get("payment_method", ""),
            status="pending",
            **extra_data
        )

        return redirect(reverse("bensryaa:order_detail", kwargs={"pk": order.pk}))

class OrderListView(ListView):
    model = Order
    template_name = "store/order_list.html"

    def get_queryset(self):
        if self.request.user.is_authenticated:
            return Order.objects.filter(user=self.request.user).order_by("-created_at")
        return Order.objects.none()

class OrderDetailView(DetailView):
    model = Order
    template_name = "store/order_detail.html"


class IndexView(ListView):
    model = Product
    template_name = "store/index.html"
    paginate_by = 12

    def get_queryset(self):
        qs = super().get_queryset()
        q = self.request.GET.get("q")
        cat = self.request.GET.get("category","game")
        if q:
            qs = qs.filter(title__icontains=q)
        if cat:
            qs = qs.filter(category=cat)
        return qs

class ProductDetailView(DetailView):
    model = Product
    template_name = "store/product_detail.html"