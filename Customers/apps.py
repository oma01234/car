from django.apps import AppConfig


class FrontConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'Customers'


class RentalConfig(AppConfig):
    name = 'Customers'

    def ready(self):
        from Customers import tasks
        from celery import Celery
        from celery.schedules import crontab

        app = Celery('project_name')
        app.conf.beat_schedule = {
            'send-booking-reminder': {
                'task': 'rental.tasks.send_booking_reminder',
                'schedule': crontab(minute=0, hour=9),  # Run every day at 9 AM
            },
        }

