from django.db import models

class Product(models.Model):
    code = models.CharField(max_length=50, unique=True)
    name = models.CharField(max_length=200)
    price = models.IntegerField()
    desc = models.TextField(blank=True, null=True)
    category = models.CharField(max_length=100, blank=True, null=True)  # Game, Pulsa, E-Money
    brand = models.CharField(max_length=100, blank=True, null=True)     # Axis, Telkomsel, ML
    image_url = models.CharField(max_length=255, blank=True, null=True)

    class Meta:
        ordering = ["name"]

    def __str__(self):
        return self.name

