from django.views.generic import ListView, DetailView
from django.shortcuts import redirect, render,get_object_or_404
from .models import Product,ProductVariant,Order
from django.contrib.auth.decorators import login_required
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib import messages
from django.db.models import Q
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login as auth_login, logout as auth_logout
from django.conf import settings
from django.views.decorators.http import require_POST
from django.http import JsonResponse
from .helpers.forms_mapping import BRAND_LOGOS,DEFAULT_LOGO,GAME_OVERRIDES,CATEGORY_INPUTS,FIELD_DEFINITIONS
import requests,uuid,random
from collections import defaultdict

def order_to_digiflazz(order):
    url = "https://api.digiflazz.com/v1/transaction"
    ref_id = str(uuid.uuid4())  # bikin unik
    payload = {
        "username": settings.DIGIFLAZZ_USERNAME,
        "buyer_sku_code": order.product_variant.code,
        "customer_no": order.target_id,
        "ref_id": ref_id,
        "sign": settings.DIGIFLAZZ_SIGN,
    }
    res = requests.post(url, json=payload, timeout=15).json()
    order.ref_id = ref_id
    order.save()
    return res

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

        # --- LOGO MAPPING ---
        brand = self.object.brand.lower()
        logo_url = BRAND_LOGOS.get(brand, DEFAULT_LOGO)

        # --- Input fields ---
        category = variants.first().category if variants.exists() else ""
        if brand in GAME_OVERRIDES:
            field_keys = GAME_OVERRIDES[brand]
        else:
            field_keys = CATEGORY_INPUTS.get(category, ["phone"])

        input_fields = [FIELD_DEFINITIONS[key] for key in field_keys if key in FIELD_DEFINITIONS]

        context["grouped_variants"] = grouped
        context["input_fields"] = input_fields
        context["brand_logo"] = logo_url  # <--- Tambahkan ini
        return context



def index(request):
    category = request.GET.get("category")
    products = Product.objects.all().order_by("brand")

    if category:
        products = products.filter(variants__category__icontains=category).distinct()

    # Tambahkan logo_url & debug log
    for p in products:
        key = p.brand.lower().strip()
        logo = BRAND_LOGOS.get(key, DEFAULT_LOGO)
        print(f"[DEBUG] Brand: '{p.brand}' | Key: '{key}' | Logo: '{logo}'")
        p.logo_url = logo

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
# Tentukan persentase markup per kategori
        CATEGORY_MARKUP = {
        "pulsa": 0.06,      # 6%
            "data": 0.06,
            "paket sms & telpon": 0.06,
            "e-money": 0.07,    # 7%
            "pln": 0.05,        # 5%
            "tv": 0.05,
            "gas": 0.05,
            "game": 0.12,       # 12%
        }

# ambil harga asli dari Digiflazz
        base_price = int(item["price"])

# ambil kategori & tentukan markup
        markup_percent = CATEGORY_MARKUP.get(category, 0.10)  # default 10% kalau tidak ketemu
        markup = int(base_price * markup_percent)

# angka random biar harga beda-beda
        random_extra = random.randint(50, 999)

# hitung harga jual & bulatkan ke kelipatan 100 biar rapi
        sell_price = round((base_price + markup + random_extra) / 100) * 100


        ProductVariant.objects.update_or_create(
            code=item["buyer_sku_code"],
            defaults={
                "product": product,
                "category": category,  # simpan kategori di varian
                "name": item["product_name"],
                "price": sell_price,   # harga jual ke user
                "desc": item.get("desc", ""),
            }
        )

        count += 1

    return JsonResponse({"message": f"{count} produk berhasil diupdate dengan markup otomatis."})



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
        if status == "paid":
            order.status = "paid"
            order.save()
            try:
                result = order_to_digiflazz(order)
                digi_status = result.get("data", {}).get("status")
                if digi_status == "Sukses":
                    order.status = "success"
                elif digi_status == "Gagal":
                    order.status = "failed"
                else:
                    order.status = "paid"  # biar nanti dicek lagi via cron
                order.save()
                messages.success(request, f"Order #{order.id} dikirim ke Digiflazz → {order.status}")
            except Exception as e:
                messages.error(request, f"Gagal order ke Digiflazz: {e}")
        elif status in ["success", "failed"]:
            order.status = status
            order.save()
            messages.success(request, f"Order #{order.id} diupdate ke {status}.")
    return redirect("bensryaa:admin_dashboard")


def logout_view(request):
    auth_logout(request)
    messages.info(request, "Anda telah logout.")
    return redirect("bensryaa:index")


@login_required
def profile(request):
    return render(request, "store/profile.html")

from collections import defaultdict

class IndexView(ListView):
    model = Product
    template_name = "store/index.html"
    context_object_name = "products"

    def get_queryset(self):
        qs = super().get_queryset().order_by("brand")
        category = self.request.GET.get("category")
        query = self.request.GET.get("q")

        if category:
            qs = qs.filter(variants__category__icontains=category).distinct()

        if query:
            qs = qs.filter(
                Q(brand__icontains=query) |
                Q(variants__name__icontains=query)
            ).distinct()

        return qs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        products = context["products"]

        for p in products:
            key = p.brand.lower().strip()
            logo = BRAND_LOGOS.get(key, DEFAULT_LOGO)
            p.logo_url = logo

        # Grouping per kategori + urutkan abjad
        products_by_category = defaultdict(list)
        for p in products:
            first_variant = p.variants.first()
            category = first_variant.category if first_variant else "lainnya"
            products_by_category[category].append(p)

        context["products_by_category"] = dict(sorted(products_by_category.items(), key=lambda x: x[0]))
        context["search_query"] = self.request.GET.get("q", "")
        return context

def search_products_api(request):
    query = request.GET.get("q", "").strip()
    results = []

    if query:
        products = Product.objects.filter(
            Q(brand__icontains=query) | Q(variants__name__icontains=query)
        ).distinct()[:8]  # max 8 hasil biar gak terlalu panjang

        for p in products:
            results.append({
                "id": p.id,
                "brand": p.brand,
                "logo_url": BRAND_LOGOS.get(p.brand.lower().strip(), DEFAULT_LOGO),
                "url": f"/product/{p.id}/",  # pastikan URL ke product detail benar
            })

    return JsonResponse({"results": results})

@login_required
def transaction_history(request):
    orders = Order.objects.filter(user=request.user).order_by("-created_at")
    return render(request, "store/transaction_history.html", {"orders": orders})



