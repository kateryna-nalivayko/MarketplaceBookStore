from django import forms
import re

class CreateOrderForm(forms.Form):
    first_name = forms.CharField(
        label="Імʼя",
        max_length=30,
        widget=forms.TextInput(attrs={'class': 'input', 'placeholder': 'Введіть ваше імʼя'}),
    )
    last_name = forms.CharField(
        label="Прізвище",
        max_length=30,
        widget=forms.TextInput(attrs={'class': 'input', 'placeholder': 'Введіть ваше прізвище'}),
    )
    phone_number = forms.CharField(
        label="Номер телефону",
        max_length=10,
        required=False,
        widget=forms.TextInput(attrs={'class': 'input', 'placeholder': '(000) 000-0000'}),
    )
    requires_delivery = forms.ChoiceField(
        label="Спосіб доставки",
        choices=[
            ("0", "Самовивіз"),
            ("1", "Мені потрібна доставка"),
        ],
        widget=forms.RadioSelect,
    )
    delivery_address = forms.CharField(
        label="Адреса доставки",
        required=False,
        widget=forms.Textarea(attrs={'class': 'textarea', 'rows': 2, 'placeholder': 'Введіть адресу доставки'}),
    )
    payment_on_get = forms.ChoiceField(
        label="Спосіб оплати",
        choices=[
            ("0", 'Розрахунок картою'),
            ("1", 'Готівка/карта при отримані'),
        ],
        widget=forms.RadioSelect,
    )

    def clean_phone_number(self):
        data = self.cleaned_data.get('phone_number', '')

        if data and not data.isdigit():
            raise forms.ValidationError("Номер телефону повинен містити тільки цифри")
        
        pattern = re.compile(r'^\d{10}$')
        if data and not pattern.match(data):
            raise forms.ValidationError("Хибний формат номеру")

        return data