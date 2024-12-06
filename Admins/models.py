from django.db import models

# Create your models here.


class Dates(models.Model):

    Scheduled_date = models.DateField(unique=True)


class FAQ(models.Model):
    question = models.CharField(max_length=255)
    answer = models.TextField()

    def __str__(self):
        return self.question
