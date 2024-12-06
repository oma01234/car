from django.urls import path
from . import views
from .views import customer_verify_code
from django.conf import settings
from django.conf.urls.static import static


urlpatterns = [
    path('customer_home/', views.customer_home, name='customer_home'),
    path('customer_register/', views.customer_register, name='customer_register'),
    path('customer_logout/', views.customer_logout, name='customer_logout'),
    path('customer_login/change_password/', views.customer_change_password, name='change_password'),
    path('Car-/<str:car>/', views.car_detail, name='item_detail'),
    path('search_car/', views.search_car, name='search_car'),
    path('error/', views.error_page, name='error'),
    path('schedule-date/', views.schedule_date, name='schedule_date'),
    path('check_email/', views.check_email, name='check_email'),
    path('customer_verify/', customer_verify_code, name='customer_verify_code'),
    path('car/<int:car_id>/', views.car_detail, name='car_detail'),
    path('customer_reviews/', views.customer_reviews, name='customer_reviews'),
    path('reservation/<int:reservation_id>/leave_review/', views.leave_review, name='leave_review'),
    path('booking-history/', views.booking_history, name='booking_history'),
    path('pending_requests/', views.pending_requests, name='pending_requests'),
    path('cancel-reservation/<int:reservation_id>/', views.cancel_reservation, name='cancel_reservation'),
    path('modify-reservation/<int:reservation_id>/', views.modify_reservation, name='modify_reservation'),
    path('profile/', views.manage_profile, name='profile'),
    path('contact/', views.contact_support, name='contact_support'),
    path('faq/', views.faq_view, name='faq_view'),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)