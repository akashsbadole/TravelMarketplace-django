"""
URL configuration for travel_marketplace project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.http import HttpResponse

def home_view(request):
    return HttpResponse("Welcome to Travel Marketplace!")

def serve_media_file(request, path):
    """Serve media files in development"""
    from django.views.static import serve
    return serve(request, path, document_root=settings.MEDIA_ROOT)

urlpatterns = [
    path("admin/", admin.site.urls),
    path("", include('pages.urls')),
    path("users/", include('users.urls')),
    path("agents/", include('agents.urls')),
    path("dashboard/", include('dashboard.urls', namespace='dashboard')),
    path("requirements/", include('requirements.urls')),
    path("quotes/", include('quotes.urls')),
    path("bookings/", include('bookings.urls')),
    path("chat/", include('chat.urls')),
    path("notifications/", include('notifications.urls')),
    path("payments/", include('paymentsdetails.urls')),
    path("reviews/", include('reviews.urls')),
    path("ai/", include('ai_assistant.urls', namespace='ai_assistant')),
    path("admin-panel/", include('admin_panel.urls')),
    path("flights/", include('amadeus.urls', namespace='amadeus')),
    path("media/<path:path>", serve_media_file, name='media'),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
