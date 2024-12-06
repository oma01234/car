from django.urls import path
from . import views
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    # Update the empty path '' to a more specific one, e.g., 'home'
    path('home/', views.home, name='CUhome'),  # Accessible at /customers/home/
]

# Serve media files in development
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
