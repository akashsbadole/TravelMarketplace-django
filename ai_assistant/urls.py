from django.urls import path
from . import views

app_name = 'ai'

urlpatterns = [
    path('', views.ai_chat, name='chat'),
    path('ask/', views.ask_ai, name='ask_ai'),
]
