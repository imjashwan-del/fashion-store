from django import forms
from django.core.validators import RegexValidator

from .models import Category, Product, StoreConfig

phone_validator = RegexValidator(
    regex=r'^[0-9+\-\s()]{7,20}$', message='Enter a valid phone number.'
)
pincode_validator = RegexValidator(regex=r'^\d{4,10}$', message='Enter a valid PIN code.')


class CheckoutForm(forms.Form):
    full_name = forms.CharField(max_length=120, label='Full Name')
    phone = forms.CharField(max_length=20, label='Phone Number', validators=[phone_validator])
    address = forms.CharField(
        max_length=255, label='Complete Delivery Address', widget=forms.Textarea(attrs={'rows': 3})
    )
    city = forms.CharField(max_length=100, label='City')
    pincode = forms.CharField(max_length=10, label='PIN Code', validators=[pincode_validator])

    # Hidden fields populated by the browser's Geolocation API on the page
    # (see static/store/js/geolocation.js). Never rendered as visible inputs
    # and never trusted as "verified" until the server re-checks distance.
    latitude = forms.FloatField(widget=forms.HiddenInput(), required=False)
    longitude = forms.FloatField(widget=forms.HiddenInput(), required=False)

    def clean_full_name(self):
        name = self.cleaned_data['full_name'].strip()
        if len(name) < 2:
            raise forms.ValidationError('Please enter your full name.')
        return name


# ---------------------------------------------------------------------------
# Owner dashboard forms
# ---------------------------------------------------------------------------

class ProductForm(forms.ModelForm):
    class Meta:
        model = Product
        fields = [
            'name', 'slug', 'description', 'price', 'category',
            'stock_quantity', 'image', 'is_featured', 'is_active',
        ]
        widgets = {
            'description': forms.Textarea(attrs={'rows': 4}),
        }

    def clean_price(self):
        price = self.cleaned_data['price']
        if price < 0:
            raise forms.ValidationError('Price cannot be negative.')
        return price

    def clean_stock_quantity(self):
        qty = self.cleaned_data['stock_quantity']
        if qty < 0:
            raise forms.ValidationError('Stock cannot be negative.')
        return qty


class CategoryForm(forms.ModelForm):
    class Meta:
        model = Category
        fields = ['name', 'slug', 'image', 'description', 'display_order']


class StoreConfigForm(forms.ModelForm):
    class Meta:
        model = StoreConfig
        exclude = []
        widgets = {
            'about_text': forms.Textarea(attrs={'rows': 5}),
        }

    def clean_delivery_radius_km(self):
        radius = self.cleaned_data['delivery_radius_km']
        if radius <= 0:
            raise forms.ValidationError('Delivery radius must be greater than zero.')
        return radius
