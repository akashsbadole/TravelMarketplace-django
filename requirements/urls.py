from django.urls import path
from . import views

app_name = 'requirements'

urlpatterns = [
    path('create/', views.create, name='create'),
    path('<int:requirement_id>/', views.detail, name='detail'),
    path('my/', views.my_requirements, name='my_requirements'),
]