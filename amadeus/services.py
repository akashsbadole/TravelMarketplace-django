import requests
import json
from datetime import datetime, timedelta
from django.conf import settings
from django.core.cache import cache
from django.utils import timezone
from .models import AmadeusAPIConfiguration, APIQuota, CachedSearchResult


class AmadeusAPIService:
    """Service for integrating with Amadeus API"""
    
    BASE_URLS = {
        'TEST': 'https://test.api.amadeus.com',
        'PRODUCTION': 'https://api.amadeus.com'
    }
    
    def __init__(self):
        self.config = self._get_active_config()
        self.base_url = self.BASE_URLS.get(self.config.environment, self.BASE_URLS['TEST'])
        self.access_token = None
        
    def _get_active_config(self):
        """Get active API configuration"""
        config = AmadeusAPIConfiguration.objects.filter(is_active=True).first()
        if not config:
            raise ValueError("No active Amadeus API configuration found")
        return config
    
    def _get_access_token(self):
        """Get or refresh access token"""
        # Check if we have a valid cached token
        cache_key = 'amadeus_access_token'
        cached_token = cache.get(cache_key)
        
        if cached_token:
            return cached_token
        
        # Get new token from API
        url = f"{self.base_url}/v1/security/oauth2/token"
        data = {
            'grant_type': 'client_credentials',
            'client_id': self.config.api_key,
            'client_secret': self.config.api_secret
        }
        
        try:
            response = requests.post(url, data=data)
            response.raise_for_status()
            token_data = response.json()
            
            access_token = token_data['access_token']
            expires_in = token_data['expires_in'] - 60  # Subtract 1 minute for safety
            
            # Cache the token
            cache.set(cache_key, access_token, expires_in)
            
            # Update config
            self.config.access_token = access_token
            self.config.token_expires_at = timezone.now() + timedelta(seconds=expires_in)
            self.config.save()
            
            return access_token
            
        except requests.exceptions.RequestException as e:
            raise Exception(f"Failed to get access token: {str(e)}")
    
    def _make_request(self, method, endpoint, params=None, data=None):
        """Make authenticated request to Amadeus API"""
        if not self.access_token:
            self.access_token = self._get_access_token()
        
        url = f"{self.base_url}{endpoint}"
        headers = {
            'Authorization': f'Bearer {self.access_token}',
            'Content-Type': 'application/json'
        }
        
        try:
            # Check API quota
            self._check_quota()
            
            if method.upper() == 'GET':
                response = requests.get(url, headers=headers, params=params)
            elif method.upper() == 'POST':
                response = requests.post(url, headers=headers, json=data)
            else:
                raise ValueError(f"Unsupported HTTP method: {method}")
            
            response.raise_for_status()
            
            # Update quota
            self._update_quota(method, endpoint)
            
            return response.json()
            
        except requests.exceptions.RequestException as e:
            raise Exception(f"API request failed: {str(e)}")
    
    def _check_quota(self):
        """Check if we have remaining API quota"""
        today = timezone.now().date()
        quota, created = APIQuota.objects.get_or_create(
            date=today,
            defaults={
                'quota_limit': self.config.daily_quota_limit,
                'quota_remaining': self.config.daily_quota_limit
            }
        )
        
        if quota.quota_remaining <= 0:
            raise Exception("Daily API quota exceeded")
    
    def _update_quota(self, method, endpoint):
        """Update API usage quota"""
        today = timezone.now().date()
        quota, created = APIQuota.objects.get_or_create(
            date=today,
            defaults={
                'quota_limit': self.config.daily_quota_limit,
                'quota_remaining': self.config.daily_quota_limit
            }
        )
        
        # Update based on endpoint type
        if '/v2/shopping/flight-offers' in endpoint:
            quota.flight_search_requests += 1
        elif '/v2/shopping/hotel-offers' in endpoint:
            quota.hotel_search_requests += 1
        elif '/v1/shopping/flight-destinations' in endpoint:
            quota.inspiration_search_requests += 1
        elif '/v1/reference-data/locations/pois' in endpoint:
            quota.poi_search_requests += 1
        
        quota.total_requests += 1
        quota.quota_remaining = max(0, quota.quota_limit - quota.total_requests)
        quota.save()
    
    def _get_cache_key(self, search_type, params):
        """Generate cache key for search results"""
        import hashlib
        params_str = json.dumps(params, sort_keys=True)
        hash_obj = hashlib.md5(params_str.encode())
        return f"amadeus_{search_type}_{hash_obj.hexdigest()}"
    
    def _get_cached_result(self, cache_key):
        """Get cached search result"""
        try:
            cached = CachedSearchResult.objects.get(
                cache_key=cache_key,
                expires_at__gt=timezone.now()
            )
            cached.hit_count += 1
            cached.save()
            return cached.response_data
        except CachedSearchResult.DoesNotExist:
            return None
    
    def _cache_result(self, cache_key, search_type, params, response_data, expire_hours=2):
        """Cache search result"""
        expires_at = timezone.now() + timedelta(hours=expire_hours)
        
        CachedSearchResult.objects.update_or_create(
            cache_key=cache_key,
            defaults={
                'search_type': search_type,
                'search_params': params,
                'response_data': response_data,
                'expires_at': expires_at
            }
        )
    
    def search_flights(self, origin, destination, departure_date, return_date=None, 
                      adults=1, children=0, infants=0, cabin_class='ECONOMY',
                      direct_flights_only=False, max_price=None, airlines=None):
        """Search for flight offers"""
        params = {
            'originLocationCode': origin,
            'destinationLocationCode': destination,
            'departureDate': departure_date.strftime('%Y-%m-%d'),
            'adults': adults,
            'children': children,
            'infants': infants,
            'travelClass': cabin_class,
            'currencyCode': 'USD',
            'max': 50  # Limit results
        }
        
        if return_date:
            params['returnDate'] = return_date.strftime('%Y-%m-%d')
        
        if direct_flights_only:
            params['nonStop'] = 'true'
        
        if max_price:
            params['maxPrice'] = str(max_price)
        
        if airlines:
            params['includedAirlineCodes'] = ','.join(airlines)
        
        # Check cache first
        cache_key = self._get_cache_key('FLIGHT', params)
        cached_result = self._get_cached_result(cache_key)
        if cached_result:
            return cached_result
        
        # Make API request
        try:
            response = self._make_request('GET', '/v2/shopping/flight-offers', params=params)
            
            # Cache the result
            self._cache_result(cache_key, 'FLIGHT', params, response)
            
            return response
            
        except Exception as e:
            raise Exception(f"Flight search failed: {str(e)}")
    
    def get_flight_price(self, offer_ids):
        """Get pricing details for specific flight offers"""
        data = {
            'data': [
                {'type': 'flight-offers', 'id': offer_id}
                for offer_id in offer_ids
            ]
        }
        
        try:
            response = self._make_request('POST', '/v2/shopping/flight-offers/pricing', data=data)
            return response
        except Exception as e:
            raise Exception(f"Flight pricing failed: {str(e)}")
    
    def search_hotels(self, city_code, check_in_date, check_out_date,
                     adults=1, room_quantity=1, price_range=None, rating=None, amenities=None):
        """Search for hotel offers"""
        params = {
            'cityCode': city_code,
            'checkInDate': check_in_date.strftime('%Y-%m-%d'),
            'checkOutDate': check_out_date.strftime('%Y-%m-%d'),
            'adults': adults,
            'roomQuantity': room_quantity,
            'currencyCode': 'USD',
            'bestRateOnly': 'true'
        }
        
        if price_range:
            params['priceRange'] = price_range
        
        if rating:
            params['ratings'] = str(int(rating))
        
        if amenities:
            params['amenities'] = ','.join(amenities)
        
        # Check cache first
        cache_key = self._get_cache_key('HOTEL', params)
        cached_result = self._get_cached_result(cache_key)
        if cached_result:
            return cached_result
        
        # Make API request
        try:
            response = self._make_request('GET', '/v2/shopping/hotel-offers', params=params)
            
            # Cache the result
            self._cache_result(cache_key, 'HOTEL', params, response)
            
            return response
            
        except Exception as e:
            raise Exception(f"Hotel search failed: {str(e)}")
    
    def get_hotel_details(self, hotel_id):
        """Get detailed information about a specific hotel"""
        try:
            response = self._make_request('GET', f'/v2/shopping/hotel-offers/by-hotel', 
                                        params={'hotelId': hotel_id})
            return response
        except Exception as e:
            raise Exception(f"Hotel details failed: {str(e)}")
    
    def search_flight_inspiration(self, origin, budget=None, departure_date=None, 
                                 duration=None, destination_country_code=None):
        """Get flight inspiration based on budget"""
        params = {
            'origin': origin,
            'maxPrice': budget or '1000'
        }
        
        if departure_date:
            params['departureDate'] = departure_date.strftime('%Y-%m-%d')
        
        if duration:
            params['duration'] = duration
        
        if destination_country_code:
            params['destinationCountryCode'] = destination_country_code
        
        # Check cache first
        cache_key = self._get_cache_key('INSPIRATION', params)
        cached_result = self._get_cached_result(cache_key)
        if cached_result:
            return cached_result
        
        try:
            response = self._make_request('GET', '/v1/shopping/flight-destinations', params=params)
            
            # Cache the result
            self._cache_result(cache_key, 'INSPIRATION', params, response, expire_hours=24)
            
            return response
            
        except Exception as e:
            raise Exception(f"Flight inspiration search failed: {str(e)}")
    
    def search_airports(self, keyword, sub_type='AIRPORT,CITY'):
        """Search for airports and cities"""
        params = {
            'keyword': keyword,
            'subType': sub_type,
            'page[limit]': 10
        }
        
        try:
            response = self._make_request('GET', '/v1/reference-data/locations', params=params)
            return response
        except Exception as e:
            raise Exception(f"Airport search failed: {str(e)}")
    
    def search_points_of_interest(self, latitude, longitude, radius=1, category=None):
        """Search for points of interest near a location"""
        params = {
            'latitude': latitude,
            'longitude': longitude,
            'radius': radius
        }
        
        if category:
            params['categories'] = category
        
        # Check cache first
        cache_key = self._get_cache_key('POI', params)
        cached_result = self._get_cached_result(cache_key)
        if cached_result:
            return cached_result
        
        try:
            response = self._make_request('GET', '/v1/reference-data/locations/pois', params=params)
            
            # Cache the result
            self._cache_result(cache_key, 'POI', params, response, expire_hours=24)
            
            return response
            
        except Exception as e:
            raise Exception(f"Points of interest search failed: {str(e)}")
    
    def get_hotel_reviews(self, hotel_id):
        """Get hotel reviews and ratings"""
        try:
            response = self._make_request('GET', f'/v2/e-reputation/hotel-sentiments', 
                                        params={'hotelIds': hotel_id})
            return response
        except Exception as e:
            raise Exception(f"Hotel reviews failed: {str(e)}")


class AmadeusDataProcessor:
    """Process and normalize Amadeus API data"""
    
    @staticmethod
    def process_flight_search_response(response_data, search_instance):
        """Process flight search response and save to database"""
        from .models import FlightOffer, FlightSegment, Airline, Aircraft, Airport
        
        offers = response_data.get('data', [])
        processed_offers = []
        
        for offer_data in offers:
            # Create flight offer
            offer = FlightOffer.objects.create(
                search=search_instance,
                offer_id=offer_data['id'],
                price_total=offer_data['price']['total'],
                price_currency=offer_data['price']['currency'],
                base_price=offer_data['price']['base'],
                taxes_fees=offer_data['price']['fees'].sum() if offer_data['price'].get('fees') else 0,
                last_ticketing_date=offer_data['lastTicketingDate'],
                is_refundable=offer_data.get('pricingOptions', {}).get('fareType', []) == ['REFUNDABLE'],
                is_one_way=len(offer_data['itineraries']) == 1,
                number_of_stops=sum(len(itinerary['segments']) - 1 for itinerary in offer_data['itineraries']),
                total_duration=sum(itinerary['duration'] for itinerary in offer_data['itineraries']),
                raw_data=offer_data
            )
            
            # Process segments
            for itinerary in offer_data['itineraries']:
                for segment_data in itinerary['segments']:
                    # Get or create airline
                    airline, _ = Airline.objects.get_or_create(
                        iata_code=segment_data['carrierCode'],
                        defaults={'name': segment_data.get('carrierCode', 'Unknown Airline')}
                    )
                    
                    # Get or create aircraft
                    aircraft = None
                    if 'aircraft' in segment_data:
                        aircraft, _ = Aircraft.objects.get_or_create(
                            code=segment_data['aircraft']['code'],
                            defaults={'name': segment_data['aircraft'].get('code', 'Unknown Aircraft')}
                        )
                    
                    # Get airports
                    departure_airport = Airport.objects.get(iata_code=segment_data['departure']['iataCode'])
                    arrival_airport = Airport.objects.get(iata_code=segment_data['arrival']['iataCode'])
                    
                    # Create segment
                    FlightSegment.objects.create(
                        offer=offer,
                        segment_number=segment_data.get('number', 1),
                        departure_airport=departure_airport,
                        arrival_airport=arrival_airport,
                        departure_time=segment_data['departure']['at'],
                        arrival_time=segment_data['arrival']['at'],
                        airline=airline,
                        flight_number=segment_data['number'],
                        aircraft=aircraft,
                        cabin_class=segment_data.get('cabin', 'ECONOMY'),
                        booking_class=segment_data.get('bookingClass', 'E'),
                        duration=segment_data['duration'],
                        is_married_segment=segment_data.get('marriedSegment', False),
                        raw_data=segment_data
                    )
            
            processed_offers.append(offer)
        
        return processed_offers
    
    @staticmethod
    def process_hotel_search_response(response_data, search_instance):
        """Process hotel search response and save to database"""
        from .models import HotelOffer, Hotel
        
        offers = response_data.get('data', [])
        processed_offers = []
        
        for offer_data in offers:
            # Get or create hotel
            hotel_data = offer_data.get('hotel', {})
            hotel, _ = Hotel.objects.get_or_create(
                hotel_id=hotel_data.get('hotelId'),
                defaults={
                    'name': hotel_data.get('name', 'Unknown Hotel'),
                    'rating': hotel_data.get('rating'),
                    'city': hotel_data.get('cityCode', ''),
                    'country': hotel_data.get('address', {}).get('countryCode', ''),
                }
            )
            
            # Create hotel offer
            offer = HotelOffer.objects.create(
                search=search_instance,
                hotel=hotel,
                offer_id=offer_data.get('id', ''),
                room_type=offer_data.get('room', {}).get('type', 'Standard Room'),
                board_type=offer_data.get('boardType', ''),
                price_total=offer_data['offers'][0]['price']['total'],
                price_currency=offer_data['offers'][0]['price']['currency'],
                price_per_night=offer_data['offers'][0]['price']['base'],
                cancellation_policy=offer_data['offers'][0].get('policies', {}).get('cancellation', ''),
                is_refundable=offer_data['offers'][0].get('policies', {}).get('guarantee', {}).get('acceptedPayments', {}).get('method') == 'CREDIT_CARD',
                available_rooms=offer_data['offers'][0].get('room', {}).get('quantityEstimated', 1),
                raw_data=offer_data
            )
            
            processed_offers.append(offer)
        
        return processed_offers