from django.core.management.base import BaseCommand
from bensryaa.models import Product, ProductVariant

BRAND_TO_CATEGORY = {
    # Pulsa
    "telkomsel": "pulsa",
    "indosat": "pulsa",
    "xl": "pulsa",
    "axis": "pulsa",
    "tri": "pulsa",
    "smartfren": "pulsa",
    "by.u": "pulsa",

    # E-Money
    "dana": "e-money",
    "ovo": "e-money",
    "gopay": "e-money",
    "shopee pay": "e-money",
    "linkaja": "e-money",

    # PLN
    "pln": "pln",

    # Voucher
    "playstation": "voucher",
    "roblox": "voucher",
    "spotify": "voucher",
    "netflix": "voucher",
    "minecraft": "voucher",
    "google play indonesia": "voucher",
    "bstation": "voucher",
    "nintendo eshop": "voucher",
    "steam wallet (idr)": "voucher",

    # Game
    "mobile legends": "game",
    "free fire": "game",
    "pubg mobile": "game",
    "arena breakout": "game",
    "magic chess": "game",
    "honkai star rail": "game",
    "among us": "game",
    "fc mobile": "game",
    "clash royale": "game",
    "stumble guys": "game",
    "genshin impact": "game",
    "garena": "game",
    "point blank": "game",
    "blood strike": "game",
    "honor of kings": "game",
    "bleach mobile 3d": "game",
}

class Command(BaseCommand):
    help = "Perbaiki kategori produk sesuai brand secara otomatis"

    def handle(self, *args, **options):
        fixed_count = 0
        skipped_count = 0

        for product in Product.objects.all():
            brand_key = product.brand.lower().strip()
            correct_category = BRAND_TO_CATEGORY.get(brand_key)

            if not correct_category:
                self.stdout.write(self.style.WARNING(f"[SKIP] {product.brand} → kategori tidak ditemukan"))
                skipped_count += 1
                continue

            variants = product.variants.all()
            if not variants.exists():
                self.stdout.write(self.style.WARNING(f"[SKIP] {product.brand} → tidak ada variant"))
                skipped_count += 1
                continue

            for v in variants:
                if v.category != correct_category:
                    v.category = correct_category
                    v.save()
                    fixed_count += 1
                    self.stdout.write(self.style.SUCCESS(f"[FIX] {v.name} ({product.brand}) → kategori diperbaiki jadi '{correct_category}'"))

        self.stdout.write(self.style.SUCCESS(f"Selesai! {fixed_count} varian diperbaiki, {skipped_count} dilewati."))
