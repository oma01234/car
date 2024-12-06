# rental/tasks.py

from celery import shared_task
from django.core.mail import send_mail
from django.utils import timezone
from datetime import timedelta
from clients.models import LeasingRequest
from django.conf import settings



@shared_task
def send_booking_reminder():
    # Get all bookings starting in the next 2 days
    upcoming_bookings = LeasingRequest.objects.filter(
        start_date=timezone.now() + timedelta(days=2), status='confirmed'
    )

    for booking in upcoming_bookings:
        customer = booking.renter
        car = booking.car

        send_mail(
            f"Reminder: Upcoming Booking for {car.make} {car.model}",
            f"Your booking for {car.make} {car.model} starts in 2 days. Rental period: {booking.start_date} to {booking.end_date}.",
            settings.DEFAULT_FROM_EMAIL,
            [customer.email],
            fail_silently=False,
        )


@shared_task
def send_late_return_alerts():
    # Find all bookings that are overdue
    overdue_bookings = LeasingRequest.objects.filter(
        end_date__lt=timezone.now(), status='confirmed'
    )

    for booking in overdue_bookings:
        customer = booking.renter
        car = booking.car

        send_mail(
            f"Late Return Alert: {car.make} {car.model}",
            f"Your rental of {car.make} {car.model} is overdue. Please return the car as soon as possible.",
            settings.DEFAULT_FROM_EMAIL,
            [customer.email],
            fail_silently=False,
        )