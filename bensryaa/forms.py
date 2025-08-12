from django import forms
from .models import Order, ProductVariant

class CheckoutForm(forms.ModelForm):
    class Meta:
        model = Order
        fields = ("game_user_id", "server_id", "payment_method")

    variant = forms.ChoiceField(required=False)  # kita isi choices di view
