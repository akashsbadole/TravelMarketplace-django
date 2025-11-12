from django.urls import path
from . import views

app_name = 'dashboard'

urlpatterns = [
    path('', views.dashboard, name='dashboard'),
    path('requirements/', views.requirements_list, name='requirements'),
    path('requirements/<int:requirement_id>/', views.requirement_detail, name='requirement_detail'),
    path('requirements/<int:requirement_id>/compare/', views.quote_comparison, name='quote_comparison'),
    path('quotes/<int:quote_id>/accept/', views.accept_quote, name='accept_quote'),
    path('quotes/<int:quote_id>/reject/', views.reject_quote, name='reject_quote'),
    path('bookings/', views.bookings_list, name='bookings'),
    path('bookings/<int:booking_id>/', views.booking_detail, name='booking_detail'),
    path('notifications/', views.notifications, name='notifications'),
]
