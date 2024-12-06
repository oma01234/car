from django.urls import path
from . import views
from .views import customer_verify_code
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    # Customer-related pages
    path('home/', views.customer_home, name='customer_home'),
    path('register/', views.customer_register, name='customer_register'),
    path('logout/', views.customer_logout, name='customer_logout'),
    path('login/change_password/', views.customer_change_password, name='change_password'),

    # Car-related pages
    path('car/<str:car>/', views.car_detail, name='car_detail'),  # Using <str:car> for car detail page
    path('search/', views.search_car, name='search_car'),

    # Error handling and reservation pages
    path('error/', views.error_page, name='error'),
    path('schedule/', views.schedule_date, name='schedule_date'),
    path('check_email/', views.check_email, name='check_email'),
    path('verify/', customer_verify_code, name='customer_verify_code'),

    # Reviews and booking pages
    path('reviews/', views.customer_reviews, name='customer_reviews'),
    path('reservation/<int:reservation_id>/leave_review/', views.leave_review, name='leave_review'),
    path('booking-history/', views.booking_history, name='booking_history'),
    path('pending-requests/', views.pending_requests, name='pending_requests'),
    path('reservation/<int:reservation_id>/cancel/', views.cancel_reservation, name='cancel_reservation'),
    path('reservation/<int:reservation_id>/modify/', views.modify_reservation, name='modify_reservation'),

    # Profile and support pages
    path('profile/', views.manage_profile, name='profile'),
    path('contact/', views.contact_support, name='contact_support'),
    path('faq/', views.faq_view, name='faq_view'),
]

# Serve media files in development
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
