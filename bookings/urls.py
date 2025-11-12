from django.urls import path
from . import views

app_name = 'bookings'

urlpatterns = [
    path('', views.list, name='list'),
    path('create/<int:quote_id>/', views.create, name='create'),
    path('<int:booking_id>/', views.detail, name='detail'),
    path('payment/<int:booking_id>/', views.payment, name='payment'),
    path('confirmation/<int:booking_id>/', views.confirmation, name='confirmation'),
]