# forms.py

from django import forms
from .models import *
from .validators import *

class ReservationForm(forms.ModelForm):
    class Meta:
        model = Reservation
        fields = ['start_date', 'end_date']  # Allow modification of rental dates
        widgets = {
            'start_date': forms.DateInput(attrs={'type': 'date'}),
            'end_date': forms.DateInput(attrs={'type': 'date'}),
        }

    def clean(self):
        cleaned_data = super().clean()
        start_date = cleaned_data.get('start_date')
        end_date = cleaned_data.get('end_date')

        # Ensure the end date is not before the start date
        if start_date and end_date:
            if end_date <= start_date:
                raise forms.ValidationError('End date must be after the start date.')

        return cleaned_data


class CustomerProfileForm(forms.ModelForm):
    class Meta:
        model = CustomerProfile
        fields = ['phone_number', 'address', 'receive_notifications', 'driver_license']
        widgets = {
            'address': forms.Textarea(attrs={'rows': 3}),
        }

    def clean_driver_license(self):
        """
        Custom validation for the driver's license image field.
        """
        driver_license = self.cleaned_data.get('driver_license')

        if driver_license:  # Only validate if a file has been uploaded
            validate_license(driver_license)  # Call the custom validator

        return driver_license


class ContactForm(forms.Form):
    name = forms.CharField(max_length=100, label="Your Name")
    email = forms.EmailField(label="Your Email Address")
    message = forms.CharField(widget=forms.Textarea, label="Your Message")