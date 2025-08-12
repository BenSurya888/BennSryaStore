from django.contrib import admin
from .models import Product, ProductVariant, Order

class ProductVariantInline(admin.TabularInline):
    model = ProductVariant
    extra = 1

@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ("title", "category", "extra_input_type", "created_at")
    list_filter = ("category", "is_premium", "extra_input_type")
    search_fields = ("title", "description")
    prepopulated_fields = {"slug": ("title",)}
    inlines = [ProductVariantInline]
    fieldsets = (
        ("Info Produk", {
            "fields": ("title", "slug", "description", "category", "is_premium", "cover", "price")
        }),
        ("Pengaturan Input Checkout", {
            "fields": ("extra_input_type", "extra_input_label"),
            "description": "Pilih tipe input tambahan yang diminta saat checkout. Gunakan label custom jika memilih tipe 'Custom'."
        }),
    )

@admin.register(ProductVariant)
class ProductVariantAdmin(admin.ModelAdmin):
    list_display = ("product", "name", "price")

@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ("id", "product", "variant_name", "price", "status", "created_at", "user")
    list_filter = ("status", "created_at")
    search_fields = ("id", "product__title", "variant_name", "game_user_id", "payment_ref")
    readonly_fields = ("created_at",)
