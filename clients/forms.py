# forms.py
from django import forms
from .models import *


class CarForm(forms.ModelForm):
    class Meta:
        model = Car
        fields = ['make', 'model', 'pic_url', 'description', 'available_for_testing', 'date']
        widgets = {
            'Available_for_testing': forms.RadioSelect(choices=Car.AVAILABILITY_CHOICES),
        }

class CarInsuranceForm(forms.ModelForm):
    class Meta:
        model = Car
        fields = ['insurance_document', 'insurance_expiry_date']


class ReviewForm(forms.ModelForm):
    class Meta:
        model = Review
        fields = ['rating', 'comment']


class BulkUpdateForm(forms.Form):
    cars = forms.ModelMultipleChoiceField(queryset=Car.objects.all(), widget=forms.CheckboxSelectMultiple)
    price_per_day = forms.DecimalField(max_digits=10, decimal_places=2, required=False)
    Available_for_testing = forms.ChoiceField(choices=Car.AVAILABILITY_CHOICES, required=False)

    def clean(self):
        cleaned_data = super().clean()
        cars = cleaned_data.get("cars")
        price_per_day = cleaned_data.get("price_per_day")
        available_for_testing = cleaned_data.get("Available_for_testing")

        if not price_per_day and not available_for_testing:
            raise forms.ValidationError("You must select at least one field to update.")

        return cleaned_data


