from django.contrib import admin
from .models import (
    Airport, Airline, Aircraft, FlightSearch, FlightOffer, FlightSegment,
    Hotel, HotelSearch, HotelOffer, PointOfInterest, APIQuota,
    AmadeusAPIConfiguration, CachedSearchResult
)


@admin.register(Airport)
class AirportAdmin(admin.ModelAdmin):
    list_display = ['iata_code', 'name', 'city', 'country', 'is_active', 'created_at']
    list_filter = ['is_active', 'country']
    search_fields = ['iata_code', 'name', 'city']
    ordering = ['iata_code']
    readonly_fields = ['created_at', 'updated_at']


@admin.register(Airline)
class AirlineAdmin(admin.ModelAdmin):
    list_display = ['iata_code', 'name', 'is_active', 'created_at']
    list_filter = ['is_active']
    search_fields = ['iata_code', 'name']
    ordering = ['iata_code']
    readonly_fields = ['created_at', 'updated_at']


@admin.register(Aircraft)
class AircraftAdmin(admin.ModelAdmin):
    list_display = ['code', 'name', 'manufacturer', 'is_active', 'created_at']
    list_filter = ['is_active', 'manufacturer']
    search_fields = ['code', 'name', 'manufacturer']
    ordering = ['code']
    readonly_fields = ['created_at', 'updated_at']


class FlightSegmentInline(admin.TabularInline):
    model = FlightSegment
    extra = 0
    readonly_fields = ['departure_time', 'arrival_time', 'duration', 'raw_data']
    fields = ['segment_number', 'departure_airport', 'arrival_airport', 
              'departure_time', 'arrival_time', 'airline', 'flight_number',
              'aircraft', 'cabin_class', 'booking_class', 'duration']


@admin.register(FlightSearch)
class FlightSearchAdmin(admin.ModelAdmin):
    list_display = ['user', 'origin', 'destination', 'departure_date', 
                   'return_date', 'adults', 'results_count', 'is_completed', 'created_at']
    list_filter = ['is_completed', 'cabin_class', 'direct_flights_only', 'created_at']
    search_fields = ['user__username', 'user__email', 'origin__iata_code', 'destination__iata_code']
    ordering = ['-created_at']
    readonly_fields = ['created_at', 'updated_at']
    date_hierarchy = 'departure_date'


@admin.register(FlightOffer)
class FlightOfferAdmin(admin.ModelAdmin):
    list_display = ['offer_id', 'search', 'price_total', 'price_currency', 
                   'number_of_stops', 'is_refundable', 'created_at']
    list_filter = ['is_refundable', 'is_one_way', 'number_of_stops', 'created_at']
    search_fields = ['offer_id', 'search__user__username']
    ordering = ['-created_at']
    readonly_fields = ['created_at', 'updated_at']
    inlines = [FlightSegmentInline]


@admin.register(Hotel)
class HotelAdmin(admin.ModelAdmin):
    list_display = ['hotel_id', 'name', 'city', 'country', 'rating', 'is_active', 'created_at']
    list_filter = ['is_active', 'rating', 'country']
    search_fields = ['hotel_id', 'name', 'city', 'country']
    ordering = ['name']
    readonly_fields = ['created_at', 'updated_at']


@admin.register(HotelSearch)
class HotelSearchAdmin(admin.ModelAdmin):
    list_display = ['user', 'city_code', 'check_in_date', 'check_out_date', 
                   'adults', 'room_quantity', 'results_count', 'is_completed', 'created_at']
    list_filter = ['is_completed', 'created_at']
    search_fields = ['user__username', 'user__email', 'city_code']
    ordering = ['-created_at']
    readonly_fields = ['created_at', 'updated_at']
    date_hierarchy = 'check_in_date'


@admin.register(HotelOffer)
class HotelOfferAdmin(admin.ModelAdmin):
    list_display = ['offer_id', 'hotel', 'search', 'room_type', 'price_total', 
                   'price_currency', 'is_refundable', 'created_at']
    list_filter = ['is_refundable', 'board_type', 'created_at']
    search_fields = ['offer_id', 'hotel__name', 'search__user__username']
    ordering = ['-created_at']
    readonly_fields = ['created_at', 'updated_at']


@admin.register(PointOfInterest)
class PointOfInterestAdmin(admin.ModelAdmin):
    list_display = ['poi_id', 'name', 'category', 'subcategory', 'city', 'country', 'rating', 'is_active']
    list_filter = ['is_active', 'category', 'subcategory', 'country']
    search_fields = ['poi_id', 'name', 'city', 'country']
    ordering = ['name']
    readonly_fields = ['created_at', 'updated_at']


@admin.register(APIQuota)
class APIQuotaAdmin(admin.ModelAdmin):
    list_display = ['date', 'flight_search_requests', 'hotel_search_requests', 
                   'total_requests', 'quota_limit', 'quota_remaining']
    list_filter = ['date']
    ordering = ['-date']
    readonly_fields = ['date', 'flight_search_requests', 'hotel_search_requests', 
                    'inspiration_search_requests', 'poi_search_requests', 
                    'total_requests', 'quota_limit', 'quota_remaining', 
                    'created_at', 'updated_at']
    
    def has_add_permission(self, request):
        return False
    
    def has_change_permission(self, request, obj=None):
        return False


@admin.register(AmadeusAPIConfiguration)
class AmadeusAPIConfigurationAdmin(admin.ModelAdmin):
    list_display = ['name', 'environment', 'is_active', 'daily_quota_limit', 
                   'rate_limit_per_minute', 'created_at']
    list_filter = ['is_active', 'environment']
    search_fields = ['name']
    ordering = ['name']
    readonly_fields = ['created_at', 'updated_at', 'access_token', 'token_expires_at']
    
    fieldsets = (
        ('Basic Configuration', {
            'fields': ('name', 'environment', 'is_active')
        }),
        ('API Credentials', {
            'fields': ('api_key', 'api_secret'),
            'classes': ('collapse',)
        }),
        ('Rate Limiting', {
            'fields': ('daily_quota_limit', 'rate_limit_per_minute')
        }),
        ('Token Information', {
            'fields': ('access_token', 'token_expires_at'),
            'classes': ('collapse',)
        }),
    )


@admin.register(CachedSearchResult)
class CachedSearchResultAdmin(admin.ModelAdmin):
    list_display = ['cache_key', 'search_type', 'hit_count', 'expires_at', 'created_at']
    list_filter = ['search_type', 'expires_at', 'created_at']
    search_fields = ['cache_key']
    ordering = ['-created_at']
    readonly_fields = ['cache_key', 'search_type', 'search_params', 
                    'response_data', 'hit_count', 'created_at', 'updated_at']
    
    def has_add_permission(self, request):
        return False
    
    def has_change_permission(self, request, obj=None):
        return False


# Customize admin site header
admin.site.site_header = 'Travel Marketplace Administration'
admin.site.site_title = 'Travel Marketplace Admin'
admin.site.index_title = 'Welcome to Travel Marketplace Admin Panel'