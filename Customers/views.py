import datetime
from clients.models import *
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from django.contrib.sites.shortcuts import get_current_site
import random
import string
from django.core.mail import send_mail
from django.http import JsonResponse
from .models import *
from Admins.models import *
import json
from django.db.models import Q
from django.contrib.auth.decorators import login_required
from django.utils import timezone
from datetime import timedelta
from django.contrib.auth import get_user_model
from django.shortcuts import render, get_object_or_404, redirect
import stripe
from django.conf import settings
from django.http import HttpResponseForbidden
from .forms import *
from decimal import Decimal


stripe.api_key = settings.STRIPE_SECRET_KEY
# Create your views here.


def customer_home(request):

    # person = Customer.objects.filter(customer_name=icon)

    return render(request, 'Customer_Home.html')


def customer_register(request):
    if request.method == "POST":
        # Get form data
        first_name = request.POST.get('First_name')
        last_name = request.POST.get('Last_name')
        username = request.POST.get('username')
        email = request.POST.get('email')
        phone_number = request.POST.get('phone_number')
        password1 = request.POST.get('password1')
        password2 = request.POST.get('password2')

        # Validate form data
        if not all([first_name, last_name, username, email, phone_number, password1, password2]):
            error_message = 'All fields are required'
            print('field')
            return JsonResponse({'status': 'error', 'msg': error_message})

        if User.objects.filter(username=username).exists():
            msg = "This username is already taken UVuTu.!MyY#b5yB"
            return JsonResponse({'status': 'error', 'msg': msg})
        #
        # if User.objects.filter(email=email).exists():
        #     msg = "This email is already registered"
        #     return JsonResponse({'status': 'error', 'msg': msg})

        if len(password1) < 8:
            msg = "Your password is too short"
            print('length')
            return JsonResponse({'status': 'error', 'msg': msg})

        if password1 != password2:
            msg = "Your passwords didn't match"
            print('match')
            return JsonResponse({'status': 'error', 'msg': msg})

        # Check password strength
        count1 = count2 = count3 = count4 = 0
        for i in password1:
            if '0' <= i <= '9':
                count1 = 1
            if 'A' <= i <= 'Z':
                count2 = 1
            if 'a' <= i <= 'z':
                count3 = 1
            if '!' <= i <= '(':
                count4 = 1

        if not all([count1, count2, count3, count4]):
            msg = "Your password isn't strong enough"
            print('here')
            return JsonResponse({'status': 'error', 'msg': msg})

        # Create user without activation
        user = User.objects.create_user(username=username, email=email, password=password1, first_name=first_name,
                                        last_name=last_name)
        user.is_active = False
        user.save()
        print('created')

        customer = Customer.objects.create(user=user, First_name=first_name, Last_name=last_name, email=email,
                                           phone_number=phone_number, is_customer=True, username=username)

        customer.save()

        # Send verification email
        send_verification_email(request, user)
        print('okay')

        # Redirect to a page informing the user to check their email
        return render(request, 'customer_registration_pending.html')

    return render(request, 'Customer_register.html')


def check_username(request):
    username = request.GET.get('username')
    is_taken = User.objects.filter(username=username).exists()
    return JsonResponse({'is_taken': is_taken})


def check_email(request):
    email = request.GET.get('email')
    is_taken = User.objects.filter(email=email).exists()
    return JsonResponse({'is_taken': is_taken})


def generate_verification_code():
    code = ''.join(random.choices(string.digits, k=6))
    return code


def send_verification_email(request, user):
    code = generate_verification_code()

    if hasattr(user, 'customer_profile'):
        profile = user.customer_profile
    else:
        print("error")
        raise AttributeError('User has no profile associated')

    profile.verification_code = code
    profile.save()

    current_site = get_current_site(request)
    subject = 'Activate Your Account'
    message = render_to_string('verification_email.html', {
        'user': user,
        'domain': current_site.domain,
        'code': code,
    })
    plain_message = strip_tags(message)
    send_mail(subject, plain_message, 'from@example.com', [user.email], html_message=message)


def customer_verify_code(request):
    if request.method == 'POST':
        verification_code = request.POST.get('verification_code')

        try:
            # Find the profile with the matching verification code
            profile = CustomerProfile.objects.get(verification_code=verification_code)

            # Retrieve the associated user
            user = profile.user

            # Ensure user is not already active
            if not user.is_active:
                # Activate the user
                user.is_active = True
                user.save()
                profile.is_verified = True
                profile.save()
                return redirect('login')  # Redirect to login page after verification
            else:
                # User is already active
                context = {'error_message': 'User is already active.'}
                return render(request, 'error.html', context)

        except CustomerProfile.DoesNotExist:
            # Handle incorrect verification code scenario
            context = {'error_message': 'Incorrect verification code. Please try again.'}
            print('here')
            return render(request, 'error.html', context)

    # If the request method is not POST, render registration pending or another appropriate template
    return render(request, 'customer_verify.html')


def error_page(request):
    error_message = "Oops! Something went wrong."
    return render(request, 'error.html', {'error': error_message})


def customer_logout(request):

    logout(request)

    return redirect('login')


def customer_change_password(request):

    if not request.user.is_authenticated:
        return redirect('mylogin')

    if request.method == "POST":

        pass1 = request.POST.get('pass1')
        pass2 = request.POST.get('pass2')

        if pass1 == "" or pass2 == "":
            error = "Both fields Required"
            print(request.user)
            return render(request, 'back/error.html', {'error': error})

        user = authenticate(username=request.user, password=pass1)

        if user:
            if len(pass2) < 6:
                error = "Your password must be greater than six characters"
                return render(request, 'back/error.html', {'error': error})

            count1 = 0
            count2 = 0
            count3 = 0
            count4 = 0

            for i in pass2:
                if '0' <= i <= '9':
                    count1 = 1
                if 'A' <= i <= 'Z':
                    count2 = 1
                if 'a' <= i <= 'z':
                    count3 = 1
                if '!' <= i <= '(':
                    count4 = 1

            if count1 and count2 and count3 and count4 == 1:

                user = User.objects.get(username=request.user)
                user.set_password(pass2)
                user.save()
                return redirect('mylogout')

        else:
            error = "INCORRECT PASSWORD"
            return render(request, 'back/error.html', {'error': error})

    return render(request, 'Customer_Home.html')


def car_detail(request, car_id):
    car = get_object_or_404(Car, id=car_id)

    # Get all reviews for the car
    reviews = car.reviews.all()

    return render(request, 'car/car_detail.html', {
        'car': car,
        'reviews': reviews
    })


def schedule_date(request):

    unavailable_dates = list(Dates.objects.values_list('Scheduled_date', flat=True))
    unavailable_dates_json = json.dumps([d.isoformat() for d in unavailable_dates])
    return render(request, 'schedule_date.html', {'unavailable_dates': unavailable_dates_json})


def search_car(request):
    # Initialize an empty queryset
    cars = Car.objects.all()

    # Handle search query
    if 'searched' in request.GET:
        searched_car = request.GET.get('searched')
        cars = cars.filter(make__icontains=searched_car)  # Case insensitive search
    else:
        searched_car = ""

    # Apply filters based on form input (if any)
    if 'car_type' in request.GET:
        car_type = request.GET.get('car_type')
        cars = cars.filter(model=car_type)

    if 'min_price' in request.GET and request.GET['min_price'] != "" and 'max_price' in request.GET and request.GET['max_price'] != "":
        min_price = request.GET.get('min_price')
        max_price = request.GET.get('max_price')

        # Convert min_price and max_price to Decimal
        if min_price:
            min_price = Decimal(min_price)
        if max_price:
            max_price = Decimal(max_price)

        cars = cars.filter(price_per_day__gte=min_price, price_per_day__lte=max_price)

    else:
        pass

    if 'year' in request.GET:
        year = request.GET.get('year')
        cars = cars.filter(year=year)

    if 'mileage' in request.GET:
        mileage = request.GET.get('mileage')
        cars = cars.filter(mileage__lte=mileage)

    if 'location' in request.GET:
        location = request.GET.get('location')
        cars = cars.filter(test_location__icontains=location)

    if 'available_for_testing' in request.GET:
        available_for_testing = request.GET.get('available_for_testing')
        cars = cars.filter(available_for_testing=available_for_testing)

    # Sorting
    if 'sort_by' in request.GET:
        sort_by = request.GET.get('sort_by')
        if sort_by == 'price_low_to_high':
            cars = cars.order_by('price_per_day')
        elif sort_by == 'price_high_to_low':
            cars = cars.order_by('-price_per_day')
        elif sort_by == 'most_recent':
            cars = cars.order_by('-date')
        elif sort_by == 'customer_rating':
            cars = cars.order_by('-rating')  # Assuming you have a rating field

    # Car comparison (optional)
    selected_car_ids = request.session.get('selected_cars', [])  # Get selected car IDs from session
    if 'compare_cars' in request.GET:
        compare_car_ids = request.GET.getlist('compare_cars')

        # Update the session with new selected car IDs
        selected_car_ids.extend([car_id for car_id in compare_car_ids if car_id not in selected_car_ids])
        request.session['selected_cars'] = selected_car_ids  # Update the session

        # Fetch the selected cars using the IDs stored in session
        selected_cars = Car.objects.filter(id__in=selected_car_ids)
    else:
        # If no cars are selected for comparison, fetch only the selected ones stored in the session
        selected_cars = Car.objects.filter(id__in=selected_car_ids)

    return render(request, 'car_search.html', {
        'searched_car': searched_car,
        'cars': cars,
        'selected_cars': selected_cars,
        'selected_car_ids': selected_car_ids,  # Pass selected car IDs to template
    })


@login_required
def select_car(request, car_id):
    car = get_object_or_404(Car, id=car_id)

    # Handle the form submission for booking
    if request.method == 'POST':
        start_date = request.POST.get('start_date')
        end_date = request.POST.get('end_date')

        # Convert the dates from string to datetime
        start_date = timezone.datetime.strptime(start_date, '%Y-%m-%d').date()
        end_date = timezone.datetime.strptime(end_date, '%Y-%m-%d').date()

        # Check car availability
        if Reservation.objects.filter(car=car, start_date__lt=end_date, end_date__gt=start_date).exists():
            error = "The car is not available for the selected dates."
            return render(request, 'car/select_car.html', {'car': car, 'error': error})

        # Calculate the total price
        num_days = (end_date - start_date).days
        total_price = num_days * car.price_per_day

        # Create a new reservation
        reservation = Reservation(
            car=car,
            renter=request.user,
            start_date=start_date,
            end_date=end_date,
            total_amount=total_price,
            status='pending'
        )
        reservation.save()

        return render(request, 'car/booking_confirmation.html', {'reservation': reservation})

    return render(request, 'car/select_car.html', {'car': car})


@login_required
def booking_confirmation(request, reservation_id):
    reservation = get_object_or_404(Reservation, id=reservation_id)

    return render(request, 'car/booking_confirmation.html', {'reservation': reservation})


from django.shortcuts import render, get_object_or_404
from django.utils import timezone
from datetime import timedelta


def availability_calendar(request, car_id):
    car = get_object_or_404(Car, id=car_id)

    # Get all reservations for this car
    reservations = Reservation.objects.filter(car=car)

    # Generate a list of booked dates for the car
    booked_dates = []
    for reservation in reservations:
        start_date = reservation.start_date
        end_date = reservation.end_date
        while start_date <= end_date:
            booked_dates.append(start_date)
            start_date += timedelta(days=1)

    # Generate a list of availability dates (for example, next 30 days)
    today = timezone.now().date()
    availability_dates = [today + timedelta(days=i) for i in range(30)]  # 30-day calendar

    # Convert booked_dates into a list of strings for easy comparison in the template
    booked_dates_str = [date.strftime('%Y-%m-%d') for date in booked_dates]

    # Pass the availability and booked dates to the template
    return render(request, 'car/availability_calendar.html', {
        'car': car,
        'availability_dates': availability_dates,
        'booked_dates': booked_dates_str,
    })


@login_required
def leave_review(request, reservation_id):
    reservation = get_object_or_404(Reservation, id=reservation_id)

    # Check if the user is the renter of the car in the reservation
    if reservation.renter != request.user:
        return redirect('home')  # You can redirect them to an error page or home if not the renter

    # Handle POST request to save the review
    if request.method == 'POST':
        rating = int(request.POST.get('rating'))
        review_text = request.POST.get('review_text')

        # Ensure rating is between 1 and 5
        if rating < 1 or rating > 5:
            return render(request, 'car/leave_review.html', {'error': 'Rating must be between 1 and 5', 'reservation': reservation})

        # Create the review
        review = Review(
            car=reservation.car,
            renter=request.user,
            reservation=reservation,
            rating=rating,
            review_text=review_text
        )
        review.save()

        # Redirect to the car detail page
        return redirect('car_detail', car_id=reservation.car.id)

    return render(request, 'car/leave_review.html', {'reservation': reservation})


@login_required
def checkout(request, reservation_id):
    reservation = Reservation.objects.get(id=reservation_id)

    # Calculate total amount
    reservation.calculate_total_amount()
    amount = int(reservation.total_amount * 100)  # Amount in cents for Stripe

    # Create a Stripe PaymentIntent for secure payments
    payment_intent = stripe.PaymentIntent.create(
        amount=amount,
        currency="usd",  # You can adjust the currency as needed
        metadata={"reservation_id": reservation.id},
    )

    # Save the payment intent ID for reference
    reservation.stripe_payment_intent_id = payment_intent.id
    reservation.save()

    # Send the client secret to the front-end to complete the payment
    return render(request, 'payment/checkout.html', {
        'reservation': reservation,
        'client_secret': payment_intent.client_secret
    })


@csrf_exempt
def payment_success(request):
    # You will receive the payload from Stripe webhook here
    payload = request.body
    sig_header = request.META['HTTP_STRIPE_SIGNATURE']
    endpoint_secret = settings.STRIPE_WEBHOOK_SECRET

    try:
        event = stripe.Webhook.construct_event(
            payload, sig_header, endpoint_secret
        )

        # Handle the payment_intent.succeeded event
        if event['type'] == 'payment_intent.succeeded':
            payment_intent = event['data']['object']  # Contains a stripe.PaymentIntent object

            reservation_id = payment_intent['metadata']['reservation_id']
            reservation = Reservation.objects.get(id=reservation_id)
            reservation.payment_status = 'paid'
            reservation.save()

            # Redirect to success page or show success message
            return render(request, 'payment/success.html', {'reservation': reservation})

    except ValueError as e:
        # Invalid payload
        return JsonResponse({'error': 'Invalid payload'}, status=400)
    except stripe.error.SignatureVerificationError as e:
        # Invalid signature
        return JsonResponse({'error': 'Invalid signature'}, status=400)

    return JsonResponse({'status': 'success'}, status=200)


def calculate_total_amount(self):
    base_price = self.car.price_per_day
    days_rented = (self.end_date - self.start_date).days

    insurance = 10  # You can add dynamic insurance pricing logic
    taxes = 0.1 * (base_price * days_rented)  # Example: 10% tax

    additional_services = 20  # Example: some fixed additional services

    # Total amount
    self.total_amount = (base_price * days_rented) + insurance + taxes + additional_services
    return self.total_amount


@login_required
def booking_history(request):
    # Get all past and upcoming reservations for the logged-in user
    upcoming_reservations = Reservation.objects.filter(renter=request.user, end_date__gte=datetime.date.today(), status__in=['confirmed', 'pending'])
    past_reservations = Reservation.objects.filter(renter=request.user, end_date__lt=datetime.date.today(), status='confirmed')

    return render(request, 'booking_history.html', {
        'upcoming_reservations': upcoming_reservations,
        'past_reservations': past_reservations
    })


@login_required
def cancel_reservation(request, reservation_id):
    reservation = get_object_or_404(Reservation, id=reservation_id)

    # Ensure that the user is the renter of the reservation
    if reservation.renter != request.user:
        return HttpResponseForbidden("You are not allowed to cancel this reservation")

    # Prevent cancellation if the reservation has already started
    if reservation.start_date < datetime.date.today():
        return HttpResponseForbidden("You cannot cancel a reservation that has already started")

    # Update reservation status to 'canceled'
    reservation.status = 'canceled'
    reservation.save()

    # Redirect to booking history page
    return redirect('booking_history')


@login_required
def modify_reservation(request, reservation_id):
    reservation = get_object_or_404(Reservation, id=reservation_id)

    # Ensure the user is the renter of the reservation
    if reservation.renter != request.user:
        return HttpResponseForbidden("You are not allowed to modify this reservation")

    if reservation.start_date < datetime.date.today():
        return HttpResponseForbidden("You cannot modify a reservation that has already started")

    if request.method == 'POST':
        form = ReservationForm(request.POST, instance=reservation)
        if form.is_valid():
            form.save()  # Save the updated reservation
            return redirect('booking_history')
    else:
        form = ReservationForm(instance=reservation)

    return render(request, 'modify_reservation.html', {
        'form': form,
        'reservation': reservation
    })


@login_required
def manage_profile(request):
    # Get the current user's profile
    profile, created = CustomerProfile.objects.get_or_create(user=request.user)

    if request.method == 'POST':
        form = CustomerProfileForm(request.POST, request.FILES, instance=profile)
        if form.is_valid():
            form.save()
            return redirect('profile')
    else:
        form = CustomerProfileForm(instance=profile)

    return render(request, 'manage_profile.html', {'form': form, 'profile': profile})


def contact_support(request):
    if request.method == "POST":
        form = ContactForm(request.POST)
        if form.is_valid():
            name = form.cleaned_data['name']
            email = form.cleaned_data['email']
            message = form.cleaned_data['message']

            # Send email to support team
            send_mail(
                f"Support Request from {name}",
                message,
                email,
                [settings.SUPPORT_EMAIL],  # Define SUPPORT_EMAIL in settings.py
                fail_silently=False,
            )

            # Optional: Provide a thank you message
            return render(request, 'contact_success.html')

    else:
        form = ContactForm()

    return render(request, 'contact.html', {'form': form})


def faq_view(request):
    faqs = FAQ.objects.all()
    return render(request, 'faq.html', {'faqs': faqs})


def confirm_booking(request, car_id):
    if request.method == 'POST':
        car = Car.objects.get(id=car_id)
        customer = request.user

        # Create a booking request (LeasingRequest)
        leasing_request = LeasingRequest.objects.create(
            car=car,
            renter=customer,
            start_date=timezone.now(),
            end_date=timezone.now() + timedelta(days=3),  # Example 3-day rental
            status='confirmed'
        )

        # Send booking confirmation email
        send_mail(
            f"Booking Confirmed: {car.make} {car.model}",
            f"Your booking for {car.make} {car.model} is confirmed. The rental period is from {leasing_request.start_date} to {leasing_request.end_date}.",
            settings.DEFAULT_FROM_EMAIL,
            [customer.email],
            fail_silently=False,
        )

        return redirect('booking_success')  # Redirect to a success page


def notify_waitlist_user(car):
    # Get all users on the waitlist for this car
    waitlist_users = Waitlist.objects.filter(car=car)

    for waitlist_user in waitlist_users:
        user = waitlist_user.user
        send_mail(
            f"Car Available: {car.make} {car.model}",
            f"Good news! The car you were interested in, {car.make} {car.model}, is now available for booking.",
            settings.DEFAULT_FROM_EMAIL,
            [user.email],
            fail_silently=False,
        )


@login_required
def customer_dashboard(request):
    # Get the current user
    user = request.user

    # Get the user's rentals (past and future)
    rentals = LeasingRequest.objects.filter(renter=user).order_by('-start_date')

    # Get payment history for the user
    payments = Payment.objects.filter(leasing_request__renter=user).order_by('-paid_at')

    # Get reviews written by the customer and received by the customer
    reviews_written = Review.objects.filter(user=user)
    reviews_received = Review.objects.filter(car__owner=user)

    # Get pending actions (e.g., unpaid rentals or pending requests)
    pending_requests = LeasingRequest.objects.filter(renter=user, status='pending')

    context = {
        'rentals': rentals,
        'payments': payments,
        'reviews_written': reviews_written,
        'reviews_received': reviews_received,
        'pending_requests': pending_requests,
    }

    return render(request, 'customer_dashboard.html', context)


@login_required
def customer_reviews(request):
    # Fetch reviews written by the customer (the user)
    reviews_written = Review.objects.filter(renter=request.user)

    # Fetch reviews received by the customer (the user) for the cars they rented out
    reviews_received = Review.objects.filter(car__renter=request.user)

    return render(request, 'customer_reviews.html', {
        'reviews_written': reviews_written,
        'reviews_received': reviews_received,
    })


@login_required
def pending_requests(request):
    user = request.user
    # Fetch all pending requests for the current logged-in user
    pending_requests = LeasingRequest.objects.filter(renter=user, status='pending')

    return render(request, 'pending_requests.html', {'pending_requests': pending_requests})




