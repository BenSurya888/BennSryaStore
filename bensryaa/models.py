from django.db import models
from django.urls import reverse
from django.conf import settings
from django.contrib.auth.models import User


class Product(models.Model):
    CATEGORY_CHOICES = [
        ("game", "Game"),
        ("app", "App"),
        ("bundle", "Bundle"),
    ]

    EXTRA_INPUT_CHOICES = [
        ("none", "Tidak Ada"),
        ("game_id_server", "User ID + Server ID"),
        ("phone_number", "Nomor HP"),
        ("email", "Email"),
        ("custom", "Custom Text"),
    ]

    title = models.CharField(max_length=200)
    slug = models.SlugField(max_length=220, unique=True)
    description = models.TextField(blank=True)
    category = models.CharField(max_length=30, choices=CATEGORY_CHOICES, default="game")
    is_premium = models.BooleanField(default=True)
    cover = models.ImageField(upload_to="products/covers/", null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    price = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)

    extra_input_type = models.CharField(
        max_length=20,
        choices=EXTRA_INPUT_CHOICES,
        default="none"
    )
    extra_input_label = models.CharField(max_length=100, blank=True, help_text="Opsional: ganti label input untuk tipe custom")

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return reverse("bensryaa:product_detail", kwargs={"slug": self.slug})


class ProductVariant(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name="variants")
    name = models.CharField(max_length=100)  # contoh: "86 Diamond", "172 Diamond"
    price = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return f"{self.product.title} - {self.name}"


class CartItem(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)

    @property
    def total(self):
        return self.product.price * self.quantity

    def __str__(self):
        return f"{self.product.title} ({self.quantity})"


class Order(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending Payment'),
        ('paid', 'Paid'),
        ('processing', 'Processing'),
        ('completed', 'Completed'),
        ('failed', 'Failed'),
        ('cancelled', 'Cancelled'),
    ]

    user = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, blank=True, on_delete=models.SET_NULL)
    created_at = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')

    product = models.ForeignKey(Product, on_delete=models.PROTECT)
    variant = models.ForeignKey(ProductVariant, null=True, blank=True, on_delete=models.PROTECT)

    price = models.DecimalField(max_digits=12, decimal_places=2)
    variant_name = models.CharField(max_length=200, blank=True)

    game_user_id = models.CharField(max_length=100, blank=True)
    server_id = models.CharField(max_length=100, blank=True)

    payment_method = models.CharField(max_length=50, blank=True)
    payment_ref = models.CharField(max_length=200, blank=True, null=True)

    # 🔹 ref_id untuk Digiflazz
    ref_id = models.CharField(max_length=50, unique=True, blank=True, null=True)

    result = models.TextField(blank=True)

    def __str__(self):
        return f"#{self.pk} {self.product.title} ({self.variant_name or 'default'}) - {self.get_status_display()}"
