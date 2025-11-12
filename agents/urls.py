from django.urls import path
from . import views

app_name = 'agents'

urlpatterns = [
    path('', views.dashboard, name='dashboard'),
    path('register/', views.register, name='register'),
    path('verification-pending/', views.verification_pending, name='verification_pending'),
    path('profile/', views.profile, name='profile'),
    path('requirements/', views.requirements, name='requirements'),
    path('requirements/<int:requirement_id>/', views.requirement_detail, name='requirement_detail'),
    path('requirements/<int:requirement_id>/quote/', views.create_quote, name='create_quote'),
    path('quotes/', views.quotes, name='quotes'),
    path('quotes/<int:quote_id>/edit/', views.edit_quote, name='edit_quote'),
    path('bookings/', views.bookings, name='bookings'),
    path('bookings/<int:booking_id>/', views.booking_detail, name='booking_detail'),
    path('bookings/<int:booking_id>/upload/', views.upload_documents, name='upload_documents'),
    path('earnings/', views.earnings, name='earnings'),
    path('earnings/request-payout/', views.request_payout, name='request_payout'),
    path('earnings/payout-history/', views.payout_history, name='payout_history'),
]
