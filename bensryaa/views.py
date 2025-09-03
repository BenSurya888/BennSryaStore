from django.views.generic import ListView, DetailView
from django.shortcuts import redirect, render
from .models import Product
from django.contrib.auth.decorators import login_required
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib import messages
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login as auth_login, logout as auth_logout
from django.conf import settings
from django.http import JsonResponse
import requests

class ProductDetailView(DetailView):
    model = Product
    slug_field = "code"
    slug_url_kwarg = "code"
    template_name = "store/product_detail.html"


def index(request):
    category = request.GET.get("category")  # baca dari URL (?category=game)
    products = Product.objects.all().order_by("name")

    if category:
        products = products.filter(category__icontains=category)

    return render(request, "store/index.html", {"object_list": products})



@staff_member_required
def sync_products_from_api(request):
    url = "https://api.digiflazz.com/v1/price-list"
    payload = {
        "cmd": "prepaid",
        "username": settings.DIGIFLAZZ_USERNAME,
        "sign": settings.DIGIFLAZZ_SIGN,
    }

    res = requests.post(url, json=payload, timeout=10)
    data = res.json()

    count = 0
    for item in data.get("data", []):
        brand = (item.get("brand") or "").lower()
        category = (item.get("category") or "").strip().lower()
  # <- ambil dari API

        Product.objects.update_or_create(
            code=item["buyer_sku_code"],
            defaults={
                "name": item["product_name"],
                "price": item["price"],
                "desc": item.get("desc", ""),
                "category": category,
                "brand": brand,
                "image_url": "store/img/hero.png",
            }
        )
        count += 1

    return JsonResponse({"message": f"{count} produk berhasil diupdate."})


def register_view(request):
    if request.method == "POST":
        username = request.POST.get("username")
        password = request.POST.get("password")

        if len(password) < 8:
            messages.error(request, "Password minimal 8 karakter.")
            return redirect("bensryaa:register")

        if User.objects.filter(username=username).exists():
            messages.error(request, "Username sudah dipakai.")
            return redirect("bensryaa:register")

        User.objects.create_user(username=username, password=password)
        messages.success(request, "Registrasi berhasil! Silakan login.")
        return redirect("bensryaa:login")

    return render(request, "registration/register.html")


def login_view(request):
    if request.method == "POST":
        username = request.POST.get("username")
        password = request.POST.get("password")

        user = authenticate(request, username=username, password=password)
        if user is not None:
            auth_login(request, user)
            messages.success(request, f"Selamat datang {username}!")
            return redirect("bensryaa:index")
        else:
            messages.error(request, "Username atau password salah.")
            return redirect("bensryaa:login")

    return render(request, "registration/login.html")


def logout_view(request):
    auth_logout(request)
    messages.info(request, "Anda telah logout.")
    return redirect("bensryaa:index")


@login_required
def profile(request):
    return render(request, "store/profile.html")


class IndexView(ListView):
    model = Product
    template_name = "store/index.html"
    context_object_name = "products"

    def get_queryset(self):
        qs = super().get_queryset().order_by("name")
        category = self.request.GET.get("category")
        if category:
            qs = qs.filter(category__icontains=category)
        return qs

