from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver
import logging
from clients.models import Car
from phonenumber_field.modelfields import PhoneNumberField


# Create your models here.
class Customer(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='customer')
    First_name = models.CharField(max_length=30)
    Last_name = models.CharField(max_length=30)
    username = models.CharField(max_length=30)
    email = models.EmailField(default='pass@gmail.com')
    phone_number = PhoneNumberField(null=True, blank=True)
    date_created = models.DateField(auto_now_add=True)
    is_customer = models.BooleanField(default=True)

    def __str__(self):
        return str(self.First_name) + ' ' + str(self.Last_name)


class CustomerProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='customer_profile')
    phone_number = PhoneNumberField(null=True, blank=True)
    address = models.TextField(null=True, blank=True)
    verification_code = models.CharField(max_length=6, blank=True, null=True)
    receive_notifications = models.BooleanField(default=True)  # Option to receive notifications
    driver_license = models.ImageField(upload_to='licenses/', null=True,
                                       blank=True)  # Optional field for driver's license

    def __str__(self):
        return f"{self.user.username} Profile"


logger = logging.getLogger(__name__)


@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        try:
            CustomerProfile.objects.create(user=instance)
            logger.debug(f"Profile created for user: {instance.username}")
        except Exception as e:
            logger.error(f"Error creating profile for user {instance.username}: {e}")


@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    try:
        if hasattr(instance, 'customer_profile'):
            instance.customer_profile.save()
            logger.debug(f"Customer profile saved for user: {instance.username}")
    except Exception as e:
        logger.error(f"Error saving profile for user {instance.username}: {e}")


class Reservation(models.Model):
    car = models.ForeignKey(Car, on_delete=models.CASCADE)
    renter = models.ForeignKey(User, on_delete=models.CASCADE)
    start_date = models.DateField()
    end_date = models.DateField()
    total_amount = models.DecimalField(max_digits=10, decimal_places=2)
    payment_status = models.CharField(max_length=20,
                                      choices=[('pending', 'Pending'), ('paid', 'Paid'), ('failed', 'Failed')],
                                      default='pending')
    stripe_payment_intent_id = models.CharField(max_length=255, null=True, blank=True)
    status = models.CharField(max_length=20,
                              choices=[('confirmed', 'Confirmed'), ('pending', 'Pending'), ('canceled', 'Canceled')],
                              default='pending')

    def __str__(self):
        return f"Reservation for {self.car} by {self.renter} from {self.start_date} to {self.end_date}"

    def calculate_total_amount(self):
        # Assuming you have a base price and other factors like insurance, taxes, etc.
        base_price = self.car.price_per_day
        days_rented = (self.end_date - self.start_date).days
        self.total_amount = base_price * days_rented
        return self.total_amount



class Waitlist(models.Model):
    car = models.ForeignKey(Car, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    added_on = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username} on waitlist for {self.car.make} {self.car.model}"


