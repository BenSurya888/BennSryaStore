from django.db import models

class Product(models.Model):
    brand = models.CharField(max_length=100, unique=True)
    image_url = models.CharField(max_length=255, blank=True, null=True)

    def __str__(self):
        return self.brand


class ProductVariant(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name="variants")
    category = models.CharField(max_length=100)  # Pulsa / Data / Masa Aktif
    code = models.CharField(max_length=50, unique=True)
    name = models.CharField(max_length=200)   # contoh: "10GB", "15.000"
    price = models.IntegerField()
    desc = models.TextField(blank=True, null=True)

    def __str__(self):
        return f"{self.product.brand} - {self.category} - {self.name}"
