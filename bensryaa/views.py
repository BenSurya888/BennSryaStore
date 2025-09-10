from django.views.generic import ListView, DetailView
from django.shortcuts import redirect, render,get_object_or_404
from .models import Product,ProductVariant,Order
from django.contrib.auth.decorators import login_required
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib import messages
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login as auth_login, logout as auth_logout
from django.conf import settings
from django.views.decorators.http import require_POST
from django.http import JsonResponse
from .helpers.forms_mapping import CATEGORY_INPUTS, GAME_OVERRIDES
import requests

@login_required
def create_order(request):
    if request.method == "POST":
        variant_code = request.POST.get("variant_code")
        target_id = request.POST.get("target_id")
        server_id = request.POST.get("server_id", "")

        variant = get_object_or_404(ProductVariant, code=variant_code)

        order = Order.objects.create(
            user=request.user,
            product_variant=variant,
            target_id=target_id,
            server_id=server_id if server_id else None,
            amount=variant.price,
            status="pending",
        )
        return redirect("bensryaa:payment_page", order_id=order.id)

    return redirect("bensryaa:index")


@login_required
def payment_page(request, order_id):
    order = get_object_or_404(Order, id=order_id, user=request.user)

    if request.method == "POST":
        proof = request.FILES.get("proof")
        if proof:
            order.payment_proof = proof
            order.status = "pending"  # tetap pending, admin yang konfirmasi
            order.save()
            messages.success(request, "Bukti pembayaran berhasil diupload. Tunggu konfirmasi admin.")
            return redirect("bensryaa:payment_page", order_id=order.id)

    return render(request, "store/payment_page.html", {"order": order})

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

            # bedakan redirect
            if user.is_staff:  # admin
                return redirect("bensryaa:admin_dashboard")
            else:  # user biasa
                return redirect("bensryaa:index")
        else:
            messages.error(request, "Username atau password salah.")
            return redirect("bensryaa:login")

    return render(request, "registration/login.html")

@staff_member_required
def admin_dashboard(request):
    total_users = User.objects.count()
    total_orders = Order.objects.count()
    pending_orders = Order.objects.filter(status="pending").count()
    total_products = Product.objects.count()

    recent_orders = Order.objects.select_related("user", "product_variant").order_by("-created_at")[:10]

    return render(request, "store/admin_dashboard.html", {
        "total_users": total_users,
        "total_orders": total_orders,
        "pending_orders": pending_orders,
        "total_products": total_products,
        "recent_orders": recent_orders,
    })


@staff_member_required
def update_order_status(request, order_id):
    order = get_object_or_404(Order, id=order_id)
    if request.method == "POST":
        status = request.POST.get("status")
        if status in ["paid", "success", "failed"]:
            order.status = status
            order.save()
            messages.success(request, f"Order #{order.id} berhasil diupdate ke {status}.")
    return redirect("bensryaa:admin_dashboard")

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
@login_required
def transaction_history(request):
    orders = Order.objects.filter(user=request.user).order_by("-created_at")
    return render(request, "store/transaction_history.html", {"orders": orders})



