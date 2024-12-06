import datetime
from . models import *
from django.conf import settings
from django.core.files.storage import FileSystemStorage
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from django.contrib.sites.shortcuts import get_current_site
import string, stripe, random
from django.shortcuts import render, redirect, get_object_or_404
from .models import ClientProfile
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from . forms import *
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from io import BytesIO
from django.http import HttpResponse
from django.db.models import Sum, Count
import os
from django.contrib.auth import get_user_model
from django.core.exceptions import *


# Stripe API keys
stripe.api_key = settings.STRIPE_TEST_SECRET_KEY


# Create your views here.
@login_required
def client_home(request):
    leasing_requests = LeasingRequest.objects.filter(renter=request.user, status='pending')
    current_bookings = LeasingRequest.objects.filter(renter=request.user, status='confirmed')
    payments = Payment.objects.filter(leasing_request__renter=request.user).order_by('-paid_at')

    return render(request, 'client_home.html', {
        'leasing_requests': leasing_requests,
        'current_bookings': current_bookings,
        'payments': payments,
    })


@login_required
def client_dashboard(request):
    # Fetch the current user's car listings
    cars = Car.objects.filter(owner=request.user)

    # Fetch leasing requests for the cars
    leasing_requests = LeasingRequest.objects.filter(car__owner=request.user)

    # Fetch payment records (earnings)
    payments = Payment.objects.filter(leasing_request__car__owner=request.user)

    # Fetch rental history for the user's cars
    rental_history = RentalHistory.objects.filter(car__owner=request.user)

    # Render the dashboard template with the necessary context
    return render(request, 'client_dashboard.html', {
        'cars': cars,
        'leasing_requests': leasing_requests,
        'payments': payments,
        'rental_history': rental_history,
    })


def client_register(request):
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

        client = Client.objects.create(user=user, First_name=first_name, Last_name=last_name, email=email,
                                       phone_number=phone_number, is_client=True, username=username)

        client.save()

        # Send verification email
        send_verification_email(request, user)
        print('done')

        # Redirect to a page informing the user to check their email
        return render(request, 'client_registration_pending.html')

    return render(request, 'Client_register.html')


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

    if hasattr(user, 'client_profile'):
        profile = user.client_profile
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


def client_logout(request):

    logout(request)

    return redirect('login')


def client_change_password(request):
    if not request.user.is_authenticated:
        return redirect('mylogin')

    if request.method == "POST":

        pass1 = request.POST.get('pass1')
        pass2 = request.POST.get('pass2')

        if pass1 == "" or pass2 == "":
            error = "Both fields Required"
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

    return render(request, 'Client_Home.html')


def owner_profile(request):
    if not request.user.is_authenticated:
        return redirect('login')

    # Fetch the car owner's profile
    profile = OwnerProfile.objects.get(user=request.user)

    # Fetch the owner's cars and bookings
    cars = profile.get_cars()
    bookings = profile.get_bookings()
    earnings = profile.get_earnings()

    return render(request, 'owner_profile.html', {
        'profile': profile,
        'cars': cars,
        'bookings': bookings,
        'earnings': earnings,
    })


def new_post(request):
    if not request.user.is_authenticated:
        return redirect('login')

    if request.method == 'POST':
        # Get data from the form
        make = request.POST.get('make')
        model = request.POST.get('model')
        year = request.POST.get('year')
        description = request.POST.get('description')
        available_for_testing = request.POST.get('available_for_testing')
        test_location = request.POST.get('test_location')
        price_per_day = request.POST.get('price_per_day')
        test_drive_fee = request.POST.get('test_drive_fee', 0)  # Default to 0 if not provided
        insurance_document = request.FILES.get('insurance_document')
        rental_agreement_document = request.FILES.get('rental_agreement_document')
        mileage = request.POST.get('mileage', 0)  # Default to 0 if not provided
        maintenance_due_date = request.POST.get('maintenance_due_date')

        # Handle the date format
        date = datetime.datetime.now()
        date_str = date.strftime("%Y/%m/%d")

        # Ensure required fields are present
        if not make or not model or not description or not available_for_testing or not year:
            error = 'All Fields Required'
            return render(request, 'back/error.html', {'error': error})

        try:
            # Handle image upload for 'pic_url'
            if 'pic_url' in request.FILES:
                pic_file = request.FILES['pic_url']
                fs = FileSystemStorage()
                pic_filename = fs.save(pic_file.name, pic_file)
                pic_url = fs.url(pic_filename)
            else:
                pic_url = ''  # Default empty if no picture uploaded

            # Create the new Car object
            car = Car(
                owner=request.user,  # The logged-in user is the owner
                make=make,
                model=model,
                year=int(year),
                pic_url=pic_url,  # Picture URL saved from file upload
                price_per_day=float(price_per_day),
                date=date_str,
                description=description,
                is_active=True,  # Set as active by default
                available_for_testing=available_for_testing,
                test_drive_fee=float(test_drive_fee),
                test_location=test_location,
                maintenance_due_date=maintenance_due_date if maintenance_due_date else None,
                insurance_document=insurance_document,
                rental_agreement_document=rental_agreement_document,
                mileage=int(mileage),
            )
            car.save()  # Save the car object to the database

            return redirect('cars_list')  # Redirect to the car listings page

        except Exception as e:
            # Handle errors such as file upload issues
            error = f'Error: {str(e)}'
            return render(request, 'back/error.html', {'error': error})

    return render(request, 'New_post.html')


def car_detail(request, car_id):
    car = Car.objects.get(id=car_id)
    car.views += 1
    car.save()
    return render(request, 'car_owner/car_detail.html', {'car': car})


def edit_post(request, pk):
    if not request.user.is_authenticated:
        return redirect('login')

    # Fetch the car object or return a 404 error if not found
    car_ = get_object_or_404(Car, pk=pk)

    if request.method == 'POST':
        # Get the updated data from the POST request
        name = request.POST.get('make')
        desc = request.POST.get('description')

        # Check if required fields are empty
        if not name or not desc:
            error = 'All fields are required.'
            return render(request, 'back/error.html', {'error': error})

        try:
            # If a new file is uploaded
            if 'myfile' in request.FILES:
                myfile = request.FILES['myfile']
                fs = FileSystemStorage()

                # Validate if the file is an image and under 5MB
                if not str(myfile.content_type).startswith('image'):
                    error = 'Your file is not supported.'
                    return render(request, 'back/error.html', {'error': error})

                if myfile.size > 5000000:
                    error = 'Your file is bigger than 5MB.'
                    return render(request, 'back/error.html', {'error': error})

                # Delete the old image from storage if it's being replaced
                if car_.picname:
                    fss = FileSystemStorage()
                    fss.delete(car_.picname)

                # Save the new image and update the URL
                filename = fs.save(myfile.name, myfile)
                url = fs.url(filename)

                # Update the car object with the new data
                car_.picname = filename
                car_.picurl = url

            # Update the other fields (name and description)
            car_.Car_name = name
            car_.Description = desc

            # Save the updated car object
            car_.save()

            # Redirect to the car listings page after successful update
            return redirect('car_list')

        except Exception as e:
            # Catch any unexpected errors and display a generic error message
            error = f"An error occurred: {str(e)}"
            return render(request, 'back/error.html', {'error': error})

    # Render the edit form with the current car details
    return render(request, 'Edit_post.html', {'car': car_})


def delete_post(request, pk):
    if not request.user.is_authenticated:
        return redirect('login')

    try:
        # Fetch the car object to be deleted
        car = Car.objects.get(pk=pk)

        # Check if the logged-in user is the owner of the car
        if car.owner != request.user:
            return redirect('cars_list')  # Unauthorized access: user is not the owner of the car

        # List of files to delete (pic_url, insurance_document, rental_agreement_document)
        files_to_delete = []
        if car.pic_url:
            # Strip the /media/ prefix and combine with MEDIA_ROOT to get the absolute file path
            file_path = os.path.join(settings.MEDIA_ROOT, car.pic_url.name.lstrip('/media/'))
            print(f"Full file path for pic_url: {file_path}")
            files_to_delete.append(file_path)

        if car.insurance_document:
            file_path = os.path.join(settings.MEDIA_ROOT, car.insurance_document.name)
            files_to_delete.append(file_path)

        if car.rental_agreement_document:
            file_path = os.path.join(settings.MEDIA_ROOT, car.rental_agreement_document.name)
            files_to_delete.append(file_path)

        # Loop through the files to delete and remove them from the file system
        fs = FileSystemStorage()
        for file_path in files_to_delete:
            # Ensure the file path is inside MEDIA_ROOT to avoid security issues
            if file_path.startswith(settings.MEDIA_ROOT):
                fs.delete(file_path)  # Delete the file from the file system
            else:
                # If file is outside of MEDIA_ROOT, raise an exception
                raise SuspiciousFileOperation(f"Attempt to delete a file outside of MEDIA_ROOT: {file_path}")

        # Now delete the car object itself
        car.delete()

        return redirect('cars_list')  # Redirect to the car listings page

    except Car.DoesNotExist:
        # If the car doesn't exist, return to the car listings page
        return redirect('cars_list')

    except SuspiciousFileOperation as e:
        # Handle any suspicious file operation (deleting files outside MEDIA_ROOT)
        error = f"Error: {e}"
        return render(request, 'error.html', {'error': error})

    except Exception as e:
        # Catch other exceptions (e.g., database or file handling errors)
        error = f"An unexpected error occurred: {str(e)}"
        return render(request, 'error.html', {'error': error})


def my_cars(request):
    if not request.user.is_authenticated:
        return redirect('login')

    # Get all cars that belong to the logged-in user
    cars = Car.objects.filter(owner=request.user)

    return render(request, 'my_cars.html', {'cars': cars})


def client_verify_code(request):
    if request.method == 'POST':
        verification_code = request.POST.get('verification_code')

        try:
            # Find the profile with the matching verification code
            profile = ClientProfile.objects.get(verification_code=verification_code)
            print('nawa')
            print(profile)

            # Retrieve the associated user
            user = profile.user

            # Ensure user is not already active
            if not user.is_active:
                # Activate the user
                user.is_active = True
                user.save()
                profile.is_verified = True
                profile.save()
                print('yes?')
                messages.success(request, 'Registration successful! You can now log in.')
                return redirect('login')  # Redirect to login page after verification
            else:
                # User is already active
                context = {'error_message': 'User is already active.'}
                return render(request, 'error.html', context)

        except ClientProfile.DoesNotExist:
            # Handle incorrect verification code scenario
            context = {'error_message': 'Incorrect verification code. Please try again.'}
            return render(request, 'error.html', context)

    # If the request method is not POST, render registration pending or another appropriate template
    return render(request, 'client_verify.html')


@login_required
def leasing_requests(request):
    # Fetch leasing requests for cars owned by the logged-in user
    requests = LeasingRequest.objects.filter(car__owner=request.user)

    return render(request, 'leasing_requests.html', {
        'requests': requests
    })


@login_required
def view_leasing_request(request, pk):
    leasing_request = get_object_or_404(LeasingRequest, pk=pk)

    if request.method == 'POST':
        action = request.POST.get('action')

        if action == 'approve':
            leasing_request.status = 'approved'
        elif action == 'reject':
            leasing_request.status = 'rejected'
        leasing_request.save()
        return redirect('car_owner:leasing_requests')

    return render(request, 'car_owner/view_leasing_request.html', {
        'leasing_request': leasing_request
    })


@login_required
def add_client_review(request, pk):
    car_owner = request.user
    client = get_object_or_404(User, pk=pk)

    if request.method == 'POST':
        rating = int(request.POST.get('rating'))
        review = request.POST.get('review')

        # Ensure review is submitted after the rental is completed
        leasing_request = LeasingRequest.objects.filter(car__owner=car_owner, renter=client, status='approved').first()
        if not leasing_request:
            return redirect('car_owner:leasing_requests')

        client_review = ClientReview(
            car_owner=car_owner,
            client=client,
            rating=rating,
            review=review,
            rental_start_date=leasing_request.start_date,
            rental_end_date=leasing_request.end_date
        )
        client_review.save()
        return redirect('car_owner:leasing_requests')

    return render(request, 'car_owner/add_client_review.html', {
        'client': client
    })


@login_required
def send_message(request, pk):
    receiver = get_object_or_404(User, pk=pk)

    if request.method == 'POST':
        message = request.POST.get('message')
        if message:
            Message.objects.create(
                sender=request.user,
                receiver=receiver,
                message=message
            )
            return redirect('car_owner:leasing_requests')

    return render(request, 'car_owner/send_message.html', {
        'receiver': receiver
    })


def send_booking_confirmation(leasing_request):
    car = leasing_request.car
    renter = leasing_request.renter
    start_date = leasing_request.start_date
    end_date = leasing_request.end_date
    total_amount = car.price_per_day * (end_date - start_date).days

    # Notify the car owner
    subject_owner = f"Booking Confirmed for {car.make} {car.model}"
    message_owner = f"""
    Hello {car.owner.username},

    Your car: {car.make} {car.model} has been successfully booked by {renter.username}.

    Booking Details:
    - Rental Period: {start_date} to {end_date}
    - Total Amount: ${total_amount}
    - Pickup Location: {car.test_location}

    Please ensure the car is ready for pickup.
    """
    from_email = settings.DEFAULT_FROM_EMAIL
    recipient_list_owner = [car.owner.email]
    send_mail(subject_owner, message_owner, from_email, recipient_list_owner)

    # Notify the renter (client)
    subject_renter = f"Booking Confirmed for {car.make} {car.model}"
    message_renter = f"""
    Hello {renter.username},

    Your booking for {car.make} {car.model} has been confirmed by the car owner.

    Booking Details:
    - Rental Period: {start_date} to {end_date}
    - Total Amount: ${total_amount}
    - Pickup Location: {car.test_location}

    Please make sure to arrive on time for pickup.
    """
    recipient_list_renter = [renter.email]
    send_mail(subject_renter, message_renter, from_email, recipient_list_renter)


@login_required
# Function to confirm leasing request
def approve_leasing_request(request, pk):
    leasing_request = get_object_or_404(LeasingRequest, pk=pk)

    if request.method == 'POST':
        # Approve the leasing request
        leasing_request.status = 'confirmed'
        leasing_request.save()

        # Send the booking confirmation email
        send_booking_confirmation(leasing_request)

        return redirect('car_owner:leasing_requests')

    return render(request, 'car_owner/approve_request.html', {'leasing_request': leasing_request})


def confirm_booking(request, leasing_request_id):
    leasing_request = get_object_or_404(LeasingRequest, pk=leasing_request_id)

    if request.method == 'POST':
        # Update status to confirmed
        leasing_request.status = 'confirmed'
        leasing_request.save()

        # Send booking confirmation emails
        send_booking_confirmation(leasing_request)

        # Show confirmation message in-app
        messages.success(request, f"Booking for {leasing_request.car.make} {leasing_request.car.model} has been confirmed.")

        return redirect('car_owner:leasing_requests')

    return render(request, 'car_owner/confirm_booking.html', {'leasing_request': leasing_request})


@login_required
def process_payment(request, leasing_request_id):
    leasing_request = get_object_or_404(LeasingRequest, pk=leasing_request_id)

    # Calculate the total amount based on car price per day and rental duration
    total_amount = leasing_request.car.price_per_day * (leasing_request.end_date - leasing_request.start_date).days

    if request.method == 'POST':
        # Create a Stripe payment intent
        intent = stripe.PaymentIntent.create(
            amount=int(total_amount * 100),  # Convert to cents
            currency='usd',
            metadata={'leasing_request_id': leasing_request.id},
        )

        # Create a Payment record in the database
        payment = Payment.objects.create(
            leasing_request=leasing_request,
            amount=total_amount,
            status='pending',
        )

        return render(request, 'client/payment_confirmation.html', {
            'client_secret': intent.client_secret,
            'payment_id': payment.id,
        })

    return render(request, 'client/payment_page.html', {
        'total_amount': total_amount,
    })

def payment_success(request, payment_id):
    payment = get_object_or_404(Payment, pk=payment_id)
    payment.status = 'paid'
    payment.save()

    return render(request, 'client/payment_success.html', {'payment': payment})

@login_required
def payment_history(request):
    # Get all payments for cars owned by the logged-in user
    payments = Payment.objects.filter(leasing_request__car__owner=request.user).order_by('-paid_at')

    return render(request, 'car_owner/payment_history.html', {'payments': payments})


def send_new_request_notification(leasing_request):
    car = leasing_request.car
    owner = car.owner
    renter = leasing_request.renter
    subject = f"New Rental Request for {car.make} {car.model}"
    message = f"""
    Hello {owner.username},

    You have received a new rental request for your car: {car.make} {car.model}.

    Client Information:
    - Renter: {renter.username}
    - Rental Period: {leasing_request.start_date} to {leasing_request.end_date}
    - Pickup Location: {car.test_location}

    Please log in to your account to review and manage this request.

    Best regards,
    The Car Lease Team
    """
    from_email = settings.DEFAULT_FROM_EMAIL
    recipient_list = [owner.email]

    send_mail(subject, message, from_email, recipient_list)

@login_required
def new_rental_request(request, car_id):
    car = get_object_or_404(Car, pk=car_id)

    if request.method == 'POST':
        start_date = request.POST.get('start_date')
        end_date = request.POST.get('end_date')

        # Create a new LeasingRequest
        leasing_request = LeasingRequest.objects.create(
            car=car,
            renter=request.user,
            start_date=start_date,
            end_date=end_date,
            status='pending'
        )

        # Add a message to notify the car owner
        messages.success(request, f'New rental request received for your {car.make} {car.model}')

        # Send an email notification to the car owner
        send_new_request_notification(leasing_request)

        return redirect('car_owner:leasing_requests')

    return render(request, 'client/new_rental_request.html', {'car': car})

@login_required
def upload_insurance(request, car_id):
    car = Car.objects.get(id=car_id)

    if request.method == 'POST':
        form = CarInsuranceForm(request.POST, request.FILES, instance=car)
        if form.is_valid():
            form.save()
            return redirect('car_owner:my_listings')  # Redirect after saving
    else:
        form = CarInsuranceForm(instance=car)

    return render(request, 'car_owner/upload_insurance.html', {'form': form, 'car': car})


def generate_rental_agreement(leasing_request_id):
    leasing_request = LeasingRequest.objects.get(id=leasing_request_id)
    car = leasing_request.car
    renter = leasing_request.renter
    start_date = leasing_request.start_date
    end_date = leasing_request.end_date
    total_amount = car.price_per_day * (end_date - start_date).days

    # Create a PDF in memory
    buffer = BytesIO()
    p = canvas.Canvas(buffer, pagesize=letter)

    # Add text to the PDF (you can customize this as needed)
    p.drawString(100, 750, f"Rental Agreement for {car.make} {car.model}")
    p.drawString(100, 730, f"Renter: {renter.username}")
    p.drawString(100, 710, f"Rental Period: {start_date} to {end_date}")
    p.drawString(100, 690, f"Total Rental Amount: ${total_amount}")
    p.drawString(100, 670, f"Pickup Location: {car.test_location}")

    # Add terms and conditions
    p.drawString(100, 650, "Terms and Conditions:")
    p.drawString(100, 630, "1. The renter is responsible for the vehicle during the lease period.")
    p.drawString(100, 610, "2. Insurance must be valid for the rental period.")
    p.drawString(100, 590, "3. Any damages to the vehicle during the rental period are the responsibility of the renter.")

    # Save the PDF in memory and return it as an HTTP response
    p.showPage()
    p.save()

    buffer.seek(0)
    response = HttpResponse(buffer, content_type='application/pdf')
    response['Content-Disposition'] = f'inline; filename="rental_agreement_{leasing_request.id}.pdf"'
    return response


@login_required
def download_agreement(request, leasing_request_id):
    leasing_request = get_object_or_404(LeasingRequest, id=leasing_request_id)

    if leasing_request.car.owner != request.user:
        return redirect('login')  # Redirect if the user is not the owner of the car

    # Generate the rental agreement
    return generate_rental_agreement(leasing_request_id)


@login_required
def upload_custom_agreement(request, car_id):
    car = Car.objects.get(id=car_id)

    if request.method == 'POST':
        if 'agreement_document' in request.FILES:
            car.rental_agreement_document = request.FILES['agreement_document']
            car.save()
            return redirect('car_owner:my_listings')

    return render(request, 'car_owner/upload_custom_agreement.html', {'car': car})


def get_car_performance(car_id):
    # Get the car object
    car = Car.objects.get(id=car_id)

    # Count the number of leasing requests (rental frequency)
    rental_frequency = LeasingRequest.objects.filter(car=car).count()

    # Calculate total income generated (sum of payments for the car)
    total_income = Payment.objects.filter(leasing_request__car=car).aggregate(Sum('amount'))['amount__sum'] or 0

    # Get the car's view count (if you have a views field)
    views = car.views

    # Return the performance metrics
    return {
        'car': car,
        'rental_frequency': rental_frequency,
        'total_income': total_income,
        'views': views,
    }


def car_performance_report(request):
    cars = Car.objects.all()

    performance_data = []
    for car in cars:
        # Get car performance data
        data = get_car_performance(car.id)
        performance_data.append(data)

    # You can also filter by a specific time period if needed
    # Example: Filter only rentals in the last 30 days
    start_date = datetime.now() - datetime.timedelta(days=30)
    cars_recent_performance = Car.objects.filter(leasing_requests__start_date__gte=start_date)

    return render(request, 'car_owner/car_performance_report.html', {
        'performance_data': performance_data,
        'cars_recent_performance': cars_recent_performance,
    })


def submit_review(request, leasing_request_id):
    if not request.user.is_authenticated:
        return redirect('login')

    leasing_request = LeasingRequest.objects.get(id=leasing_request_id)

    if leasing_request.renter != request.user:
        return redirect('error')  # Only the renter can review

    if leasing_request.status != 'confirmed':
        return redirect('error')  # Can only review after the rental is confirmed

    # Check if review already exists
    if Review.objects.filter(leasing_request=leasing_request).exists():
        return redirect('error')  # User has already submitted a review for this rental

    if request.method == 'POST':
        form = ReviewForm(request.POST)
        if form.is_valid():
            # Save the review with the car and owner details
            review = form.save(commit=False)
            review.car = leasing_request.car
            review.owner = leasing_request.car.owner
            review.client = request.user
            review.save()
            return redirect('owner_profile')  # Redirect to the owner's profile after review submission
    else:
        form = ReviewForm()

    return render(request, 'submit_review.html', {'form': form, 'leasing_request': leasing_request})


def view_maintenance(request, car_id):
    if not request.user.is_authenticated:
        return redirect('login')

    car = Car.objects.get(id=car_id, owner=request.user)
    maintenances = car.maintenances.all()

    return render(request, 'car_maintenance.html', {'car': car, 'maintenances': maintenances})


def report_damage(request, car_id, renter_id):
    if not request.user.is_authenticated:
        return redirect('login')

    car = Car.objects.get(id=car_id, owner=request.user)
    renter = User.objects.get(id=renter_id)

    if request.method == "POST":
        description = request.POST.get('description')
        damage_cost = request.POST.get('damage_cost')

        damage_report = DamageReport(
            car=car,
            renter=renter,
            description=description,
            damage_cost=damage_cost,
        )
        damage_report.save()

        return redirect('car_maintenance', car_id=car.id)  # Redirect back to car's maintenance history

    return render(request, 'report_damage.html', {'car': car, 'renter': renter})


def maintenance_reminders(request):
    if not request.user.is_authenticated:
        return redirect('login')

    cars = Car.objects.filter(owner=request.user)
    reminders = []

    for car in cars:
        for reminder in car.maintenance_reminders.all():
            reminder.check_if_due()
            if reminder.is_due:
                reminders.append(reminder)

    return render(request, 'maintenance_reminders.html', {'reminders': reminders})


def bulk_update(request):
    if not request.user.is_authenticated:
        return redirect('login')

    # Handle the form submission
    if request.method == 'POST':
        form = BulkUpdateForm(request.POST)

        if form.is_valid():
            # Get the selected cars
            cars = form.cleaned_data.get('cars')

            # Update the selected cars with the provided data
            price_per_day = form.cleaned_data.get('price_per_day')
            available_for_testing = form.cleaned_data.get('Available_for_testing')

            if price_per_day:
                cars.update(price_per_day=price_per_day)
            if available_for_testing:
                cars.update(Available_for_testing=available_for_testing)

            return redirect('my_cars')  # Redirect to the "My Cars" page after the update

    else:
        form = BulkUpdateForm()

    return render(request, 'bulk_update.html', {'form': form})

