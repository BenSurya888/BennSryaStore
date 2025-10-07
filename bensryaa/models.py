from django.db import models
from django.contrib.auth.models import User

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

class Order(models.Model):
    PAYMENT_METHODS = [
        ('qris', 'QRIS'),
        ('virtual_account', 'Virtual Account'),
        ('ewallet', 'E-Wallet'),
    ]
    
    STATUS_CHOICES = [
        ("pending", "Pending"),
        ("paid", "Paid"),
        ("success", "Success"),
        ("failed", "Failed"),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    product_variant = models.ForeignKey("ProductVariant", on_delete=models.CASCADE)
    target_id = models.CharField(max_length=50)
    server_id = models.CharField(max_length=50, blank=True, null=True)
    amount = models.PositiveIntegerField()
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default="pending",
    )
    payment_method = models.CharField(
        max_length=20,
        choices=PAYMENT_METHODS,
        default='qris'
    )
    payment_proof = models.ImageField(upload_to="payment_proofs/", blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    ref_id = models.CharField(max_length=100, null=True, blank=True)  # untuk tracking ke Digiflazz

    def __str__(self):
        return f"Order #{self.id} - {self.product_variant.name}"