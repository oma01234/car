from django.urls import path
from . import views
from .views import client_verify_code
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    # path('home/<str:icon>', views.client_home, name='home'),
    path('client_home/', views.client_home, name='client_home'),
    path('client_dashboard/', views.client_dashboard, name='client_dashboard'),
    path('client-register/', views.client_register, name='client_register'),
    path('client_verify/', client_verify_code, name='client_verify_code'),
    path('client_logout/', views.client_logout, name='client_logout'),
    path('Client-Login/change_password/', views.client_change_password, name='change_password'),
    path('create_post/', views.new_post, name='New_Post'),
    path('car_list/', views.my_cars, name='cars_list'),
    path('bulk-update/', views.bulk_update, name='bulk_update'),
    path('edit_car/<int:pk>/', views.edit_post, name='Edit_post'),
    path('delete_car/<int:pk>/', views.delete_post, name='Delete_post'),
    path('check_username/', views.check_username, name='check_username'),
    path('check_email/', views.check_email, name='check_email'),
    path('leasing-requests/', views.leasing_requests, name='leasing_requests'),
    path('leasing-request/<int:pk>/', views.view_leasing_request, name='view_leasing_request'),
    path('add-client-review/<int:pk>/', views.add_client_review, name='add_client_review'),
    path('send-message/<int:pk>/', views.send_message, name='send_message'),

]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)