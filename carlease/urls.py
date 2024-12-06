from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.views.static import serve
from django.conf.urls.static import static

urlpatterns = [
    # Admin route
    path('admin/', admin.site.urls),

    # Add each app under a different URL prefix
    path('main/', include('main.urls')),         # For the 'main' app
    path('customers/', include('Customers.urls')),  # For the 'Customers' app
    path('clients/', include('clients.urls')),   # For the 'clients' app
    path('admins/', include('Admins.urls')),     # For the 'Admins' app

    # Serve media files at the correct path
    path('media/<path>', serve, {'document_root': settings.MEDIA_ROOT}),
]

# Serve static and media files in development
if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
