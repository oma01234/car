from django.core.management.base import BaseCommand
from django.core.mail import send_mail
from django.conf import settings
from datetime import datetime, timedelta
from clients.models import Car

class Command(BaseCommand):
    help = 'Sends maintenance reminders to car owners'

    def handle(self, *args, **kwargs):
        today = datetime.today().date()
        cars_due_for_maintenance = Car.objects.filter(maintenance_due_date__lte=today)

        for car in cars_due_for_maintenance:
            owner = car.owner
            subject = f"Maintenance Reminder for {car.make} {car.model}"
            message = f"Hello {owner.username},\n\nYour car {car.make} {car.model} is due for maintenance. Please check the vehicle.\n\nBest regards,\nCar Lease Team"
            send_mail(subject, message, settings.DEFAULT_FROM_EMAIL, [owner.email])

        self.stdout.write(self.style.SUCCESS('Maintenance reminders sent successfully.'))
