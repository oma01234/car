from django.shortcuts import render, redirect
from django.contrib.admin.views.decorators import staff_member_required
from clients.models import *
from Customers.models import *
from django.db.models import Sum


# Create your views here.

def home(request):

     return render(request,"")


@staff_member_required
def admin_dashboard(request):
    if not request.user.is_authenticated or not request.user.is_staff:
        return redirect('login')  # Redirect to login if not authenticated or not admin

    # Calculate total revenue, bookings, cars, etc.
    total_revenue = 0
    total_bookings = LeasingRequest.objects.count()
    total_cars = Car.objects.count()

    car_revenue = []
    for car in Car.objects.all():
        revenue = car.leasing_requests.aggregate(total_revenue=models.Sum('payment__amount'))
        car_revenue.append({
            'make': car.make,
            'model': car.model,
            'total_revenue': revenue['total_revenue'] or 0
        })

    context = {
        'total_revenue': total_revenue,
        'total_bookings': total_bookings,
        'total_cars': total_cars,
        'car_revenue': car_revenue,
    }

    return render(request, 'admin_dashboard.html', context)