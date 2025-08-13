import json
import os
import uuid
from .services.digiflazz import digiflazz_signature, digiflazz_request
from django.views.generic import ListView, DetailView
from .models import Product
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.views import View
from .models import Order, CartItem, Product,ProductVariant
from django.contrib.auth.decorators import login_required
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib import messages
from .forms import CheckoutForm
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import login
from django.conf import settings
import requests
from django.http import JsonResponse

@staff_member_required
def sync_products_dummy(request):
    """Sinkronisasi produk dari file JSON dummy."""
    dummy_file = os.path.join(settings.BASE_DIR, "digiflazz_dummy.json")
    with open(dummy_file, "r", encoding="utf-8") as f:
        data = json.load(f)

    count = 0
    for item in data.get("data", []):
        product, created = Product.objects.get_or_create(
            title=item["product_name"],
            defaults={
                "slug": item["buyer_sku_code"].lower(),
                "category": "game",
                "price": item["price"],
            }
        )
        # Simpan varian
        ProductVariant.objects.get_or_create(
            product=product,
            name=item["desc"],
            price=item["price"]
        )
        count += 1

    return JsonResponse({"message": f"{count} produk berhasil disinkronkan (dummy)."})

def register(request):
    if request.method == "POST":
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)  # langsung login setelah daftar
            messages.success(request, "Akun berhasil dibuat, selamat datang!")
            return redirect("bensryaa:index")  # redirect ke home
    else:
        form = UserCreationForm()

    return render(request, "registration/register.html", {"form": form})

def home(request):
    products = Product.objects.all()
    return render(request, "index.html", {"object_list": products})

# 📜 Riwayat Transaksi
@login_required
def transaction_history(request):
    transactions = Order.objects.filter(user=request.user).order_by("-created_at")
    return render(request, "store/transaction_history.html", {"transactions": transactions})

# 🔍 Cek Pesanan
def check_order(request):
    order = None
    ref_id = request.GET.get("ref_id")  # ambil ref_id dari input user
    if ref_id:
        order = Order.objects.filter(ref_id=ref_id).first()

    return render(request, "store/check_order.html", {"order": order})

# 📞 Contact
def contact(request):
    return render(request, "store/contact.html")

# 🛒 Cart
@login_required
def cart(request):
    cart_items = CartItem.objects.filter(user=request.user)
    return render(request, "store/cart.html", {"cart_items": cart_items})

@login_required
def add_to_cart(request, slug):
    product = get_object_or_404(Product, slug=slug)
    cart_item, created = CartItem.objects.get_or_create(user=request.user, product=product)
    if not created:
        cart_item.quantity += 1
        cart_item.save()
    messages.success(request, "Produk ditambahkan ke keranjang.")
    return redirect("bensryaa:cart")

@login_required
def remove_from_cart(request, pk):
    cart_item = get_object_or_404(CartItem, pk=pk, user=request.user)
    cart_item.delete()
    messages.success(request, "Produk dihapus dari keranjang.")
    return redirect("bensryaa:cart")

# 👤 Profile
@login_required
def profile(request):
    return render(request, "store/profile.html")
    
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

        # 🔹 Generate ref_id unik
        ref_id = str(uuid.uuid4())[:10]
        signature = digiflazz_signature(ref_id)  # nanti dipakai ke API Digiflazz

        if request.POST.get("payment_method") == "manual":
         status = "pending"
        else:
            status = "paid"  # dummy untuk midtrans

        order = Order.objects.create(
        user=request.user if request.user.is_authenticated else None,
        product=product,
        variant=variant,
        price=price,
        variant_name=variant_name,
        payment_method=request.POST.get("payment_method", ""),
        status=status,
        ref_id=ref_id,
        **extra_data
    )

        # 🔹 Simpan payload dummy dulu
        payload = {
            "username": settings.DIGIFLAZZ_USERNAME,
            "buyer_sku_code": product.slug,
            "customer_no": extra_data.get("game_user_id", ""),
            "ref_id": ref_id,
            "sign": signature
        }
        order.result = json.dumps({"dummy_payload": payload}, indent=2)
        order.save()

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

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        from django.conf import settings
        context["BANK_NAME"] = settings.BANK_NAME
        context["BANK_ACCOUNT_NUMBER"] = settings.BANK_ACCOUNT_NUMBER
        context["BANK_ACCOUNT_NAME"] = settings.BANK_ACCOUNT_NAME
        return context
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
