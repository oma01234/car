from django.urls import path
from . import views
from .views import client_verify_code
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    # Home and Dashboard for Clients
    path('home/', views.client_home, name='client_home'),
    path('dashboard/', views.client_dashboard, name='client_dashboard'),

    # Registration and Login-related paths
    path('register/', views.client_register, name='client_register'),
    path('verify/', client_verify_code, name='client_verify_code'),
    path('logout/', views.client_logout, name='client_logout'),
    path('login/change_password/', views.client_change_password, name='change_password'),

    # Car-related actions
    path('create_post/', views.new_post, name='create_post'),
    path('car_list/', views.my_cars, name='cars_list'),
    path('edit_car/<int:pk>/', views.edit_post, name='edit_car'),
    path('delete_car/<int:pk>/', views.delete_post, name='delete_car'),

    # Leasing and Messaging
    path('leasing_requests/', views.leasing_requests, name='leasing_requests'),
    path('leasing_request/<int:pk>/', views.view_leasing_request, name='view_leasing_request'),
    path('add_client_review/<int:pk>/', views.add_client_review, name='add_client_review'),
    path('send_message/<int:pk>/', views.send_message, name='send_message'),

    # Username & Email validation
    path('check_username/', views.check_username, name='check_username'),
    path('check_email/', views.check_email, name='check_email'),
]

# Serve media files in development
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
