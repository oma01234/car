from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver
import logging
import datetime
from django.db import models
from django.contrib.auth.models import User

class Car(models.Model):
    AVAILABILITY_CHOICES = [
        ('available', 'Available'),
        ('not_available', 'Not Available'),
    ]
    owner = models.ForeignKey(User, on_delete=models.CASCADE, related_name='cars')
    make = models.CharField(max_length=100)
    model = models.CharField(max_length=100)
    year = models.IntegerField()
    pic_url = models.ImageField(upload_to='media/', blank=True, null=True)
    price_per_day = models.DecimalField(max_digits=10, decimal_places=2, null=True)
    date = models.CharField(max_length=50, default="")
    description = models.TextField()
    is_active = models.BooleanField(default=True)
    available_for_testing = models.CharField(
        max_length=15,
        choices=AVAILABILITY_CHOICES,
        default='not_available'
    )
    test_drive_fee = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    test_location = models.TextField()
    maintenance_due_date = models.DateField(null=True, blank=True)

    insurance_document = models.FileField(upload_to='insurance_documents/', null=True, blank=True)
    insurance_expiry_date = models.DateField(null=True, blank=True)

    rental_agreement_document = models.FileField(upload_to='rental_agreements/', null=True, blank=True)
    views = models.PositiveIntegerField(default=0)

    mileage = models.IntegerField(default=0)

    def __str__(self):
        return f"{self.make} {self.model} ({self.year})"


class CarMaintenance(models.Model):
    car = models.ForeignKey(Car, on_delete=models.CASCADE, related_name="maintenances")
    service_date = models.DateField()
    service_type = models.CharField(max_length=200)  # e.g., "Oil Change", "Tire Replacement", etc.
    mileage = models.IntegerField()  # Mileage at the time of service
    cost = models.DecimalField(max_digits=10, decimal_places=2)
    details = models.TextField(blank=True, null=True)  # Any extra notes about the service

    def __str__(self):
        return f"Maintenance of {self.car} on {self.service_date}"

class DamageReport(models.Model):
    car = models.ForeignKey(Car, on_delete=models.CASCADE, related_name="damage_reports")
    renter = models.ForeignKey(User, on_delete=models.CASCADE, related_name="damage_reports")
    report_date = models.DateField(auto_now_add=True)
    description = models.TextField()
    damage_cost = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    is_claimed = models.BooleanField(default=False)  # Whether a claim was filed for the damage

    def __str__(self):
        return f"Damage Report for {self.car} by {self.renter} on {self.report_date}"


class LeasingRequest(models.Model):
    car = models.ForeignKey(Car, on_delete=models.CASCADE, related_name='leasing_requests')
    renter = models.ForeignKey(User, on_delete=models.CASCADE, related_name='leasing_requests')
    start_date = models.DateField()
    end_date = models.DateField()
    status = models.CharField(max_length=20, choices=[('pending', 'Pending'), ('approved', 'Approved'), ('rejected', 'Rejected')])
    message = models.TextField(blank=True, null=True)  # Optional message field for car owners to communicate with clients

    def __str__(self):
        return f"Request for {self.car} by {self.renter} from {self.start_date} to {self.end_date}"

class RentalHistory(models.Model):
    car = models.ForeignKey(Car, on_delete=models.CASCADE, related_name='rental_history')
    renter = models.ForeignKey(User, on_delete=models.CASCADE)
    start_date = models.DateField()
    end_date = models.DateField()
    total_amount = models.DecimalField(max_digits=10, decimal_places=2)
    review = models.TextField(null=True, blank=True)

    def __str__(self):
        return f"Rental of {self.car} by {self.renter} from {self.start_date} to {self.end_date}"


class ClientReview(models.Model):
    car_owner = models.ForeignKey(User, on_delete=models.CASCADE, related_name='client_reviews')
    client = models.ForeignKey(User, on_delete=models.CASCADE, related_name='received_reviews')
    rating = models.IntegerField(choices=[(1, '1 - Poor'), (2, '2 - Fair'), (3, '3 - Good'), (4, '4 - Very Good'), (5, '5 - Excellent')])
    review = models.TextField()
    rental_start_date = models.DateField()
    rental_end_date = models.DateField()

    def __str__(self):
        return f"Review by {self.client} for {self.car_owner} on rental from {self.rental_start_date} to {self.rental_end_date}"

class Message(models.Model):
    sender = models.ForeignKey(User, on_delete=models.CASCADE, related_name='sent_messages')
    receiver = models.ForeignKey(User, on_delete=models.CASCADE, related_name='received_messages')
    message = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Message from {self.sender} to {self.receiver} at {self.timestamp}"



class Client(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='client')
    First_name = models.CharField(max_length=30)
    Last_name = models.CharField(max_length=30)
    username = models.CharField(max_length=30)
    email = models.EmailField(default='pass@gmail.com')
    phone_number = models.IntegerField()
    date_created = models.DateField(auto_now_add=True)
    is_client = models.BooleanField(default=True)

    def __str__(self):
        return str(self.First_name) + ' ' + str(self.Last_name)


class ClientProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='client_profile')
    verification_code = models.CharField(max_length=6, blank=True, null=True)
    is_verified = models.BooleanField(default=False)
    # Add other fields as needed for your user profile

    def __str__(self):
        return f"Profile for {self.user}"


logger = logging.getLogger(__name__)


@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        try:
            ClientProfile.objects.create(user=instance)
            logger.debug(f"Profile created for user: {instance.username}")
        except Exception as e:
            logger.error(f"Error creating profile for user {instance.username}: {e}")


@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    try:
        if hasattr(instance, 'client_profile'):
            instance.client_profile.save()
            logger.debug(f"Client profile saved for user: {instance.username}")
    except Exception as e:
        logger.error(f"Error saving profile for user {instance.username}: {e}")

class Payment(models.Model):
    leasing_request = models.OneToOneField(LeasingRequest, on_delete=models.CASCADE)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    paid_at = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=50, choices=[('pending', 'Pending'), ('paid', 'Paid')], default='pending')

    def __str__(self):
        return f"Payment for {self.leasing_request.car.make} {self.leasing_request.car.model} - {self.status}"


class OwnerProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="owner_profile")
    full_name = models.CharField(max_length=200)
    phone_number = models.CharField(max_length=20, blank=True, null=True)
    address = models.TextField(blank=True, null=True)
    profile_picture = models.ImageField(upload_to='profile_pics/', blank=True, null=True)
    verification_status = models.BooleanField(default=False)  # Used for verifying the owner's identity
    identity_verified_at = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return f"{self.full_name} (Owner)"

    def get_cars(self):
        return self.user.cars.all()  # Assuming a relationship to cars via the `Car` model

    def get_bookings(self):
        return LeasingRequest.objects.filter(car__owner=self.user).all()  # All leasing requests for this owner’s cars

    def get_earnings(self):
        total_earnings = Payment.objects.filter(
            leasing_request__car__owner=self.user
        ).aggregate(models.Sum('amount'))['amount__sum'] or 0
        return total_earnings


class Review(models.Model):
    car = models.ForeignKey(Car, on_delete=models.CASCADE, related_name="reviews")
    client = models.ForeignKey(User, on_delete=models.CASCADE, related_name="reviews")
    owner = models.ForeignKey(User, on_delete=models.CASCADE, related_name="owner_reviews")  # The owner being reviewed
    rating = models.IntegerField(choices=[(1, '1 - Poor'), (2, '2 - Fair'), (3, '3 - Good'), (4, '4 - Very Good'), (5, '5 - Excellent')])
    comment = models.TextField()

    def __str__(self):
        return f"Review by {self.client.username} for {self.car.make} {self.car.model} ({self.rating} stars)"


class MaintenanceReminder(models.Model):
    car = models.ForeignKey(Car, on_delete=models.CASCADE, related_name="maintenance_reminders")
    reminder_type = models.CharField(max_length=100)  # "Mileage" or "Time"
    reminder_value = models.IntegerField()  # Could be a mileage threshold or time interval in days
    next_due_date = models.DateField()
    is_due = models.BooleanField(default=False)

    def check_if_due(self):
        if self.reminder_type == "Mileage" and self.car.mileage >= self.reminder_value:
            self.is_due = True
        elif self.reminder_type == "Time" and datetime.date.today() >= self.next_due_date:
            self.is_due = True
        self.save()

    def __str__(self):
        return f"Reminder for {self.car} - {self.reminder_type} {self.reminder_value}"
