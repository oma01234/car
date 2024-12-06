from django.core.files.storage import FileSystemStorage
from django.contrib.auth.models import User
from django.shortcuts import render

from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login
from django.contrib import messages
from clients.models import Client
from Customers.models import Customer
from django.http import JsonResponse

def main(request):

    return render(request, 'home.html')


def profiles_exp(request):

    return render(request, 'profile_explanation.html')


from django.contrib.auth import authenticate, login
from django.http import JsonResponse
from django.shortcuts import render, redirect

def user_login(request):
    if request.method == "POST":
        # Get form data
        username = request.POST.get('username')
        password = request.POST.get('password')

        # Authenticate user
        user = authenticate(request, username=username, password=password)

        if user is not None:
            # Log the user in
            login(request, user)

            # Check if the user is a Customer or Client and send the appropriate redirect URL
            try:
                customer_profile = Customer.objects.get(user=user)
                # Send a response with the redirect URL for the customer dashboard
                return JsonResponse({'status': 'success', 'redirect_url': '/customer_home/'})  # Adjust the URL
            except Customer.DoesNotExist:
                pass  # Not a customer, continue to check client profile

            try:
                client_profile = Client.objects.get(user=user)
                # Send a response with the redirect URL for the client dashboard
                return JsonResponse({'status': 'success', 'redirect_url': '/client_home/'})  # Adjust the URL
            except Client.DoesNotExist:
                pass  # Not a client, continue to check other profiles

        # If authentication fails or no valid profile is found, return error
        return JsonResponse({'status': 'error', 'message': 'Invalid credentials.'})

    return render(request, 'login.html')  # Render the login form page

