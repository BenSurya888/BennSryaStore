from django.views.generic import ListView, DetailView
from django.shortcuts import redirect, render
from .models import Product,ProductVariant
from django.contrib.auth.decorators import login_required
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib import messages
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login as auth_login, logout as auth_logout
from django.conf import settings
from django.http import JsonResponse
from .helpers.forms_mapping import CATEGORY_INPUTS, GAME_OVERRIDES
import requests

class ProductDetailView(DetailView):
    model = Product
    template_name = "store/product_detail.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        variants = self.object.variants.all().order_by("category", "price")

        grouped = {}
        for v in variants:
            grouped.setdefault(v.category, []).append(v)

        # tentuin input field
        brand = self.object.brand.lower()
        if brand in GAME_OVERRIDES:
            inputs = GAME_OVERRIDES[brand]
        else:
            category = variants.first().category if variants.exists() else ""
            inputs = CATEGORY_INPUTS.get(category, [])

        context["grouped_variants"] = grouped
        context["input_fields"] = inputs
        return context


def index(request):
    category = request.GET.get("category")
    products = Product.objects.all().order_by("brand")

    if category:
        products = products.filter(variants__category__icontains=category).distinct()

    return render(request, "store/index.html", {"object_list": products})

@staff_member_required
def sync_products_from_api(request):
    if request.method != "GET":  # batasi hanya GET
        return JsonResponse({"error": "Method not allowed"}, status=405)
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
        brand = (item.get("brand") or "").strip()
        category = (item.get("category") or "").strip().lower()

        # Simpan brand ke Product
        product, _ = Product.objects.get_or_create(
            brand=brand,
            defaults={"image_url": "store/img/hero.png"}
        )

        ProductVariant.objects.update_or_create(
            code=item["buyer_sku_code"],
            defaults={
                "product": product,
                "category": category,  # simpan kategori di varian
                "name": item["product_name"],
                "price": item["price"],
                "desc": item.get("desc", ""),
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
        qs = super().get_queryset().order_by("brand")
        category = self.request.GET.get("category")
        if category:
            qs = qs.filter(variants__category__icontains=category).distinct()
        return qs



