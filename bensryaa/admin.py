from django.urls import path
from django.http import HttpResponseRedirect
from django.contrib import admin, messages
from django.urls import reverse
from django.conf import settings
import json, os
from .models import Product, ProductVariant

@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ("title", "category", "extra_input_type", "created_at")
    change_list_template = "admin/product_changelist.html"

    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            path(
                "sync-dummy/",
                self.admin_site.admin_view(self.sync_dummy),
                name="product_sync_dummy",
            ),
        ]
        return custom_urls + urls

    def sync_dummy(self, request):
        dummy_file = os.path.join(settings.BASE_DIR, "digiflazz_dummy.json")
        if not os.path.exists(dummy_file):
            self.message_user(request, "File dummy tidak ditemukan", level=messages.ERROR)
            return HttpResponseRedirect("../")

        with open(dummy_file, "r", encoding="utf-8") as f:
            data = json.load(f)

        count = 0
        for item in data.get("data", []):
            product, _ = Product.objects.get_or_create(
                slug=item["buyer_sku_code"].lower(),
                defaults={
                    "title": item["product_name"],
                    "category": "game",
                    "price": item["price"],
                }
            )
            ProductVariant.objects.get_or_create(
                product=product,
                name=item["desc"],
                price=item["price"]
            )
            count += 1

        self.message_user(request, f"{count} produk berhasil disinkronkan (dummy).", level=messages.SUCCESS)
        return HttpResponseRedirect("../")
