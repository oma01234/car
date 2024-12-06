from django.urls import path
from . import views
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    # Main page (landing page or dashboard)
    path('', views.main, name='main_page'),

    # Profile explanation page (for users who need guidance)
    path('signup/profile-explanation/', views.profiles_exp, name='profile_explanation'),

    # Login page
    path('login/', views.user_login, name='login'),
]

# Serve media files in development (only if DEBUG is True)
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
