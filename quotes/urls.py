from django.urls import path
from . import views

app_name = 'quotes'

urlpatterns = [
    path('', views.list, name='list'),
    path('create/', views.create, name='create'),
    path('<int:quote_id>/', views.detail, name='detail'),
]
