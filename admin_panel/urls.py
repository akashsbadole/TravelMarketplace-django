from django.urls import path
from . import views

app_name = 'admin_panel'

urlpatterns = [
    path('', views.dashboard, name='dashboard'),
    path('users/', views.manage_users, name='manage_users'),
    path('agents/', views.manage_agents, name='manage_agents'),
    path('agents/<int:agent_id>/verify/', views.verify_agent, name='verify_agent'),
    path('commission/', views.commission_management, name='commission_management'),
    path('payouts/', views.payout_management, name='payout_management'),
    path('disputes/', views.dispute_management, name='dispute_management'),
    path('analytics/', views.analytics, name='analytics'),
    path('settings/', views.system_settings, name='system_settings'),
    path('export/', views.data_export, name='data_export'),
]
