from django.db import models
from django.contrib.auth import get_user_model
from agents.models import Agent
from requirements.models import ServiceType

User = get_user_model()


class Airport(models.Model):
    """Airport information from Amadeus API"""
    iata_code = models.CharField(max_length=3, unique=True, db_index=True)
    icao_code = models.CharField(max_length=4, blank=True)
    name = models.CharField(max_length=255)
    city = models.CharField(max_length=100)
    country = models.CharField(max_length=100)
    country_code = models.CharField(max_length=2)
    latitude = models.DecimalField(max_digits=10, decimal_places=7, null=True, blank=True)
    longitude = models.DecimalField(max_digits=10, decimal_places=7, null=True, blank=True)
    timezone = models.CharField(max_length=50, blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['iata_code']
        indexes = [
            models.Index(fields=['iata_code']),
            models.Index(fields=['city']),
            models.Index(fields=['country']),
        ]

    def __str__(self):
        return f"{self.iata_code} - {self.name}, {self.city}"


class Airline(models.Model):
    """Airline information from Amadeus API"""
    iata_code = models.CharField(max_length=2, unique=True, db_index=True)
    icao_code = models.CharField(max_length=3, blank=True)
    name = models.CharField(max_length=255)
    logo_url = models.URLField(blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['iata_code']

    def __str__(self):
        return f"{self.iata_code} - {self.name}"


class Aircraft(models.Model):
    """Aircraft information from Amadeus API"""
    code = models.CharField(max_length=10, unique=True, db_index=True)
    name = models.CharField(max_length=255)
    manufacturer = models.CharField(max_length=100, blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['code']

    def __str__(self):
        return f"{self.code} - {self.name}"


class FlightSearch(models.Model):
    """Flight search query and results"""
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='flight_searches')
    origin = models.ForeignKey(Airport, on_delete=models.CASCADE, related_name='departure_searches')
    destination = models.ForeignKey(Airport, on_delete=models.CASCADE, related_name='arrival_searches')
    departure_date = models.DateField()
    return_date = models.DateField(null=True, blank=True)
    adults = models.PositiveIntegerField(default=1)
    children = models.PositiveIntegerField(default=0)
    infants = models.PositiveIntegerField(default=0)
    cabin_class = models.CharField(max_length=20, choices=[
        ('ECONOMY', 'Economy'),
        ('PREMIUM_ECONOMY', 'Premium Economy'),
        ('BUSINESS', 'Business'),
        ('FIRST', 'First'),
    ], default='ECONOMY')
    direct_flights_only = models.BooleanField(default=False)
    max_price = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    preferred_airlines = models.ManyToManyField(Airline, blank=True)
    search_results = models.JSONField(default=dict, blank=True)  # Store raw API response
    results_count = models.PositiveIntegerField(default=0)
    is_completed = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['user', '-created_at']),
            models.Index(fields=['origin', 'destination']),
            models.Index(fields=['departure_date']),
        ]

    def __str__(self):
        return f"{self.origin.iata_code} → {self.destination.iata_code} on {self.departure_date}"


class FlightOffer(models.Model):
    """Individual flight offer from Amadeus API"""
    search = models.ForeignKey(FlightSearch, on_delete=models.CASCADE, related_name='flight_offers')
    offer_id = models.CharField(max_length=100, db_index=True)
    price_total = models.DecimalField(max_digits=10, decimal_places=2)
    price_currency = models.CharField(max_length=3, default='USD')
    base_price = models.DecimalField(max_digits=10, decimal_places=2)
    taxes_fees = models.DecimalField(max_digits=10, decimal_places=2)
    last_ticketing_date = models.DateField()
    is_refundable = models.BooleanField(default=False)
    is_one_way = models.BooleanField(default=False)
    number_of_stops = models.PositiveIntegerField(default=0)
    total_duration = models.PositiveIntegerField()  # in minutes
    raw_data = models.JSONField(default=dict)  # Store complete offer data
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['price_total']
        indexes = [
            models.Index(fields=['search', 'price_total']),
            models.Index(fields=['offer_id']),
        ]

    def __str__(self):
        return f"Flight Offer {self.offer_id} - ${self.price_total}"


class FlightSegment(models.Model):
    """Individual flight segment within a flight offer"""
    offer = models.ForeignKey(FlightOffer, on_delete=models.CASCADE, related_name='segments')
    segment_number = models.PositiveIntegerField()
    departure_airport = models.ForeignKey(Airport, on_delete=models.CASCADE, related_name='departure_segments')
    arrival_airport = models.ForeignKey(Airport, on_delete=models.CASCADE, related_name='arrival_segments')
    departure_time = models.DateTimeField()
    arrival_time = models.DateTimeField()
    airline = models.ForeignKey(Airline, on_delete=models.CASCADE)
    flight_number = models.CharField(max_length=10)
    aircraft = models.ForeignKey(Aircraft, on_delete=models.SET_NULL, null=True, blank=True)
    cabin_class = models.CharField(max_length=20)
    booking_class = models.CharField(max_length=3)
    duration = models.PositiveIntegerField()  # in minutes
    is_married_segment = models.BooleanField(default=False)
    raw_data = models.JSONField(default=dict, blank=True)

    class Meta:
        ordering = ['offer', 'segment_number']
        indexes = [
            models.Index(fields=['offer', 'segment_number']),
            models.Index(fields=['departure_airport', 'departure_time']),
            models.Index(fields=['airline']),
        ]

    def __str__(self):
        return f"{self.airline.iata_code}{self.flight_number} {self.departure_airport.iata_code} → {self.arrival_airport.iata_code}"


class Hotel(models.Model):
    """Hotel information from Amadeus API"""
    hotel_id = models.CharField(max_length=50, unique=True, db_index=True)
    name = models.CharField(max_length=255)
    chain_code = models.CharField(max_length=10, blank=True)
    rating = models.DecimalField(max_digits=3, decimal_places=1, null=True, blank=True)
    latitude = models.DecimalField(max_digits=10, decimal_places=7, null=True, blank=True)
    longitude = models.DecimalField(max_digits=10, decimal_places=7, null=True, blank=True)
    address = models.TextField(blank=True)
    city = models.CharField(max_length=100, blank=True)
    country = models.CharField(max_length=100, blank=True)
    country_code = models.CharField(max_length=2, blank=True)
    postal_code = models.CharField(max_length=20, blank=True)
    phone = models.CharField(max_length=50, blank=True)
    email = models.EmailField(blank=True)
    website = models.URLField(blank=True)
    description = models.TextField(blank=True)
    amenities = models.JSONField(default=list, blank=True)
    images = models.JSONField(default=list, blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['name']
        indexes = [
            models.Index(fields=['hotel_id']),
            models.Index(fields=['city']),
            models.Index(fields=['country']),
            models.Index(fields=['rating']),
        ]

    def __str__(self):
        return f"{self.name} - {self.city}"


class HotelSearch(models.Model):
    """Hotel search query and results"""
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='hotel_searches')
    city_code = models.CharField(max_length=10)  # IATA city code
    check_in_date = models.DateField()
    check_out_date = models.DateField()
    adults = models.PositiveIntegerField(default=1)
    children = models.PositiveIntegerField(default=0)
    room_quantity = models.PositiveIntegerField(default=1)
    price_range = models.CharField(max_length=20, blank=True)  # e.g., "50-100"
    rating = models.DecimalField(max_digits=3, decimal_places=1, null=True, blank=True)
    amenities = models.JSONField(default=list, blank=True)
    search_results = models.JSONField(default=dict, blank=True)  # Store raw API response
    results_count = models.PositiveIntegerField(default=0)
    is_completed = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['user', '-created_at']),
            models.Index(fields=['city_code']),
            models.Index(fields=['check_in_date']),
        ]

    def __str__(self):
        return f"Hotels in {self.city_code} from {self.check_in_date} to {self.check_out_date}"


class HotelOffer(models.Model):
    """Individual hotel offer from Amadeus API"""
    search = models.ForeignKey(HotelSearch, on_delete=models.CASCADE, related_name='hotel_offers')
    hotel = models.ForeignKey(Hotel, on_delete=models.CASCADE, related_name='offers')
    offer_id = models.CharField(max_length=100, db_index=True)
    room_type = models.CharField(max_length=100)
    board_type = models.CharField(max_length=50, blank=True)  # e.g., "ROOM_ONLY", "BREAKFAST"
    price_total = models.DecimalField(max_digits=10, decimal_places=2)
    price_currency = models.CharField(max_length=3, default='USD')
    price_per_night = models.DecimalField(max_digits=10, decimal_places=2)
    cancellation_policy = models.TextField(blank=True)
    is_refundable = models.BooleanField(default=False)
    available_rooms = models.PositiveIntegerField(default=1)
    raw_data = models.JSONField(default=dict)  # Store complete offer data
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['price_total']
        indexes = [
            models.Index(fields=['search', 'price_total']),
            models.Index(fields=['hotel']),
            models.Index(fields=['offer_id']),
        ]

    def __str__(self):
        return f"{self.hotel.name} - ${self.price_total} ({self.room_type})"


class PointOfInterest(models.Model):
    """Points of Interest from Amadeus API"""
    poi_id = models.CharField(max_length=50, unique=True, db_index=True)
    name = models.CharField(max_length=255)
    category = models.CharField(max_length=100)
    subcategory = models.CharField(max_length=100, blank=True)
    latitude = models.DecimalField(max_digits=10, decimal_places=7)
    longitude = models.DecimalField(max_digits=10, decimal_places=7)
    address = models.TextField(blank=True)
    city = models.CharField(max_length=100, blank=True)
    country = models.CharField(max_length=100, blank=True)
    description = models.TextField(blank=True)
    rating = models.DecimalField(max_digits=3, decimal_places=1, null=True, blank=True)
    images = models.JSONField(default=list, blank=True)
    opening_hours = models.JSONField(default=dict, blank=True)
    contact_info = models.JSONField(default=dict, blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['name']
        indexes = [
            models.Index(fields=['poi_id']),
            models.Index(fields=['category']),
            models.Index(fields=['city']),
        ]

    def __str__(self):
        return f"{self.name} - {self.category}"


class APIQuota(models.Model):
    """Track API usage and quotas"""
    date = models.DateField(auto_now_add=True)
    flight_search_requests = models.PositiveIntegerField(default=0)
    flight_search_results = models.PositiveIntegerField(default=0)
    hotel_search_requests = models.PositiveIntegerField(default=0)
    hotel_search_results = models.PositiveIntegerField(default=0)
    inspiration_search_requests = models.PositiveIntegerField(default=0)
    poi_search_requests = models.PositiveIntegerField(default=0)
    total_requests = models.PositiveIntegerField(default=0)
    quota_limit = models.PositiveIntegerField(default=10000)  # Daily quota limit
    quota_remaining = models.PositiveIntegerField(default=10000)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-date']
        indexes = [
            models.Index(fields=['date']),
        ]

    def __str__(self):
        return f"API Usage for {self.date}: {self.total_requests}/{self.quota_limit}"


class AmadeusAPIConfiguration(models.Model):
    """Store Amadeus API configuration"""
    name = models.CharField(max_length=100, unique=True)
    api_key = models.CharField(max_length=255)
    api_secret = models.CharField(max_length=255)
    environment = models.CharField(max_length=20, choices=[
        ('TEST', 'Test/Sandbox'),
        ('PRODUCTION', 'Production'),
    ], default='TEST')
    is_active = models.BooleanField(default=False)
    daily_quota_limit = models.PositiveIntegerField(default=10000)
    rate_limit_per_minute = models.PositiveIntegerField(default=100)
    access_token = models.TextField(blank=True)
    token_expires_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['name']

    def __str__(self):
        return f"{self.name} ({self.environment})"


class CachedSearchResult(models.Model):
    """Cache search results to reduce API calls"""
    cache_key = models.CharField(max_length=255, unique=True, db_index=True)
    search_type = models.CharField(max_length=20, choices=[
        ('FLIGHT', 'Flight Search'),
        ('HOTEL', 'Hotel Search'),
        ('INSPIRATION', 'Flight Inspiration'),
        ('POI', 'Point of Interest'),
    ])
    search_params = models.JSONField(default=dict)
    response_data = models.JSONField(default=dict)
    expires_at = models.DateTimeField()
    hit_count = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['cache_key']),
            models.Index(fields=['search_type']),
            models.Index(fields=['expires_at']),
        ]

    def __str__(self):
        return f"{self.search_type} Cache - {self.cache_key}"