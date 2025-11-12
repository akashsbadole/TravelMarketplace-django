from django.urls import path
from . import views

app_name = 'notifications'

urlpatterns = [
    path('', views.list, name='list'),
    path('mark-read/<int:notification_id>/', views.mark_read, name='mark_read'),
    path('mark-all-read/', views.mark_all_read, name='mark_all_read'),
    path('preferences/', views.preferences, name='preferences'),
    path('api/get-unread-count/', views.get_unread_count, name='get_unread_count'),
]
