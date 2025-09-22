from django.core.management.base import BaseCommand
from bensryaa.models import Order
from django.conf import settings
import requests

class Command(BaseCommand):
    help = "Cek status order ke Digiflazz dan update ke database"

    def handle(self, *args, **kwargs):
        # ambil semua order yang sudah dibayar tapi belum final
        orders = Order.objects.filter(status="paid", ref_id__isnull=False)
        for order in orders:
            payload = {
                "username": settings.DIGIFLAZZ_USERNAME,
                "ref_id": order.ref_id,
                "sign": settings.DIGIFLAZZ_SIGN,
            }
            try:
                res = requests.post("https://api.digiflazz.com/v1/transaction", json=payload, timeout=15).json()
                status = res.get("data", {}).get("status")

                if status == "Sukses":
                    order.status = "success"
                    order.save()
                    self.stdout.write(self.style.SUCCESS(f"Order {order.id} → SUCCESS"))
                elif status == "Gagal":
                    order.status = "failed"
                    order.save()
                    self.stdout.write(self.style.ERROR(f"Order {order.id} → FAILED"))
                else:
                    self.stdout.write(f"Order {order.id} masih {status}")

            except Exception as e:
                self.stdout.write(self.style.ERROR(f"Error cek order {order.id}: {e}"))
