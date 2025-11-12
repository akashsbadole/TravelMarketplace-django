from django.urls import path
from . import views

app_name = 'chat'

urlpatterns = [
    path('', views.index, name='index'),
    path('send/', views.send_message, name='send_message'),
    path('history/<int:booking_id>/', views.chat_history, name='chat_history'),
    path('api/', views.api_chat, name='api_chat'),
]
