from django.urls import path
from . import views

app_name = 'reviews'

urlpatterns = [
    path('', views.review_list, name='review_list'),
    path('<int:review_id>/', views.review_detail, name='review_detail'),
    path('create/<int:booking_id>/', views.create_review, name='create_review'),
    path('<int:review_id>/helpful/', views.mark_helpful, name='mark_helpful'),
    path('<int:review_id>/report/', views.report_review, name='report_review'),
    path('agent/<int:agent_id>/', views.agent_reviews, name='agent_reviews'),
]
