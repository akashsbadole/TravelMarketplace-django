from django.urls import path
from . import views

app_name = 'amadeus'

urlpatterns = [
    # Flight Search
    path('flights/search/', views.flight_search, name='flight_search'),
    path('flights/results/<int:search_id>/', views.flight_results, name='flight_results'),
    path('flights/detail/<int:offer_id>/', views.flight_detail, name='flight_detail'),
    
    # Hotel Search
    path('hotels/search/', views.hotel_search, name='hotel_search'),
    path('hotels/results/<int:search_id>/', views.hotel_results, name='hotel_results'),
    path('hotels/detail/<int:offer_id>/', views.hotel_detail, name='hotel_detail'),
    
    # Flight Inspiration
    path('flights/inspiration/', views.flight_inspiration, name='flight_inspiration'),
    
    # Search History
    path('search/history/', views.search_history, name='search_history'),
    
    # Agent Quote Builder
    path('agent/quote-builder/<int:requirement_id>/', views.agent_quote_builder, name='agent_quote_builder'),
    
    # API Endpoints
    path('api/airport-autocomplete/', views.airport_autocomplete, name='airport_autocomplete'),
    path('api/status/', views.api_status, name='api_status'),
    
    # Main Amadeus Page
    path('', views.flight_search, name='home'),
]