from django.test import TestCase, Client
from django.contrib.auth import get_user_model
from django.urls import reverse
from django.utils import timezone
from datetime import datetime, timedelta
from .models import Airport, Airline, FlightSearch, HotelSearch, APIConfiguration
from .services import AmadeusAPIService

User = get_user_model()


class AmadeusAPITestCase(TestCase):
    """Test cases for Amadeus API integration"""
    
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        
        # Create test airport
        self.origin_airport = Airport.objects.create(
            iata_code='NYC',
            name='New York John F. Kennedy',
            city='New York',
            country='United States',
            country_code='US',
            latitude=40.6413,
            longitude=-73.7781
        )
        
        self.destination_airport = Airport.objects.create(
            iata_code='LON',
            name='London Heathrow',
            city='London',
            country='United Kingdom',
            country_code='GB',
            latitude=51.4700,
            longitude=-0.4543
        )
        
        # Create test airline
        self.airline = Airline.objects.create(
            iata_code='BA',
            name='British Airways',
            is_active=True
        )
        
        # Create API configuration
        self.api_config = APIConfiguration.objects.create(
            name='Test Config',
            api_key='test_key',
            api_secret='test_secret',
            environment='TEST',
            is_active=True
        )
    
    def test_flight_search_page_loads(self):
        """Test that flight search page loads correctly"""
        self.client.login(username='testuser', password='testpass123')
        response = self.client.get(reverse('amadeus:flight_search'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Find Your Perfect Flight')
    
    def test_hotel_search_page_loads(self):
        """Test that hotel search page loads correctly"""
        self.client.login(username='testuser', password='testpass123')
        response = self.client.get(reverse('amadeus:hotel_search'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Find Your Perfect Hotel')
    
    def test_flight_search_form_submission(self):
        """Test flight search form submission"""
        self.client.login(username='testuser', password='testpass123')
        
        data = {
            'origin': self.origin_airport.id,
            'destination': self.destination_airport.id,
            'departure_date': (timezone.now() + timedelta(days=7)).strftime('%Y-%m-%d'),
            'return_date': (timezone.now() + timedelta(days=14)).strftime('%Y-%m-%d'),
            'trip_type': 'round_trip',
            'adults': 2,
            'children': 0,
            'infants': 0,
            'cabin_class': 'ECONOMY'
        }
        
        response = self.client.post(reverse('amadeus:flight_search'), data)
        
        # Should create a flight search record
        self.assertTrue(FlightSearch.objects.filter(user=self.user).exists())
        
        # Should redirect to results page
        flight_search = FlightSearch.objects.get(user=self.user)
        self.assertRedirects(response, reverse('amadeus:flight_results', args=[flight_search.id]))
    
    def test_hotel_search_form_submission(self):
        """Test hotel search form submission"""
        self.client.login(username='testuser', password='testpass123')
        
        data = {
            'city_code': 'PAR',
            'check_in_date': (timezone.now() + timedelta(days=7)).strftime('%Y-%m-%d'),
            'check_out_date': (timezone.now() + timedelta(days=10)).strftime('%Y-%m-%d'),
            'adults': 2,
            'room_quantity': 1
        }
        
        response = self.client.post(reverse('amadeus:hotel_search'), data)
        
        # Should create a hotel search record
        self.assertTrue(HotelSearch.objects.filter(user=self.user).exists())
        
        # Should redirect to results page
        hotel_search = HotelSearch.objects.get(user=self.user)
        self.assertRedirects(response, reverse('amadeus:hotel_results', args=[hotel_search.id]))
    
    def test_airport_autocomplete(self):
        """Test airport autocomplete functionality"""
        response = self.client.post(
            reverse('amadeus:airport_autocomplete'),
            {'query': 'New York'},
            content_type='application/x-www-form-urlencoded'
        )
        
        self.assertEqual(response.status_code, 200)
        self.assertIn('suggestions', response.json())
    
    def test_flight_inspiration_page(self):
        """Test flight inspiration page"""
        self.client.login(username='testuser', password='testpass123')
        response = self.client.get(reverse('amadeus:flight_inspiration'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Not sure where to go?')
    
    def test_search_history_page(self):
        """Test search history page"""
        self.client.login(username='testuser', password='testpass123')
        
        # Create some test searches
        FlightSearch.objects.create(
            user=self.user,
            origin=self.origin_airport,
            destination=self.destination_airport,
            departure_date=timezone.now() + timedelta(days=7),
            adults=1
        )
        
        HotelSearch.objects.create(
            user=self.user,
            city_code='PAR',
            check_in_date=timezone.now() + timedelta(days=7),
            check_out_date=timezone.now() + timedelta(days=10),
            adults=1
        )
        
        response = self.client.get(reverse('amadeus:search_history'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Search History')


class AmadeusServiceTestCase(TestCase):
    """Test cases for Amadeus API service"""
    
    def setUp(self):
        self.api_config = APIConfiguration.objects.create(
            name='Test Config',
            api_key='test_key',
            api_secret='test_secret',
            environment='TEST',
            is_active=True
        )
    
    def test_api_service_initialization(self):
        """Test that API service initializes correctly"""
        service = AmadeusAPIService()
        self.assertIsNotNone(service.config)
        self.assertEqual(service.config.name, 'Test Config')
        self.assertIn(service.base_url, ['https://test.api.amadeus.com', 'https://api.amadeus.com'])
    
    def test_cache_key_generation(self):
        """Test cache key generation"""
        service = AmadeusAPIService()
        params = {'origin': 'NYC', 'destination': 'LON', 'date': '2024-01-01'}
        cache_key = service._get_cache_key('FLIGHT', params)
        
        self.assertIsInstance(cache_key, str)
        self.assertIn('amadeus_FLIGHT', cache_key)
    
    def test_quota_check(self):
        """Test API quota checking"""
        service = AmadeusAPIService()
        
        # This should not raise an exception
        service._check_quota()
        
        # Set quota to 0 to test limit
        from .models import APIQuota
        from django.utils import timezone
        today = timezone.now().date()
        quota, _ = APIQuota.objects.get_or_create(
            date=today,
            defaults={'quota_limit': 0, 'quota_remaining': 0}
        )
        quota.quota_remaining = 0
        quota.save()
        
        # This should raise an exception
        with self.assertRaises(Exception) as context:
            service._check_quota()
        self.assertIn('quota exceeded', str(context.exception))


class AmadeusModelTestCase(TestCase):
    """Test cases for Amadeus models"""
    
    def setUp(self):
        self.airport = Airport.objects.create(
            iata_code='JFK',
            name='John F. Kennedy International Airport',
            city='New York',
            country='United States',
            country_code='US'
        )
    
    def test_airport_str_representation(self):
        """Test airport string representation"""
        expected = "JFK - John F. Kennedy International Airport, New York"
        self.assertEqual(str(self.airport), expected)
    
    def test_airport_ordering(self):
        """Test airport ordering"""
        airport2 = Airport.objects.create(
            iata_code='LAX',
            name='Los Angeles International',
            city='Los Angeles',
            country='United States',
            country_code='US'
        )
        
        airports = list(Airport.objects.all())
        self.assertEqual(airports[0].iata_code, 'JFK')
        self.assertEqual(airports[1].iata_code, 'LAX')
    
    def test_flight_search_creation(self):
        """Test flight search creation"""
        user = User.objects.create_user(
            username='testuser2',
            email='test2@example.com',
            password='testpass123'
        )
        
        destination = Airport.objects.create(
            iata_code='LAX',
            name='Los Angeles International',
            city='Los Angeles',
            country='United States',
            country_code='US'
        )
        
        flight_search = FlightSearch.objects.create(
            user=user,
            origin=self.airport,
            destination=destination,
            departure_date=timezone.now() + timedelta(days=7),
            adults=2,
            cabin_class='ECONOMY'
        )
        
        self.assertEqual(flight_search.user, user)
        self.assertEqual(flight_search.origin, self.airport)
        self.assertEqual(flight_search.destination, destination)
        self.assertEqual(flight_search.adults, 2)
        self.assertEqual(flight_search.cabin_class, 'ECONOMY')
    
    def test_hotel_search_creation(self):
        """Test hotel search creation"""
        user = User.objects.create_user(
            username='testuser3',
            email='test3@example.com',
            password='testpass123'
        )
        
        hotel_search = HotelSearch.objects.create(
            user=user,
            city_code='PAR',
            check_in_date=timezone.now() + timedelta(days=7),
            check_out_date=timezone.now() + timedelta(days=10),
            adults=2,
            room_quantity=1
        )
        
        self.assertEqual(hotel_search.user, user)
        self.assertEqual(hotel_search.city_code, 'PAR')
        self.assertEqual(hotel_search.adults, 2)
        self.assertEqual(hotel_search.room_quantity, 1)


class AmadeusViewTestCase(TestCase):
    """Test cases for Amadeus views"""
    
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        
        self.client = Client()
        self.client.login(username='testuser', password='testpass123')
    
    def test_api_status_endpoint(self):
        """Test API status endpoint"""
        response = self.client.get(reverse('amadeus:api_status'))
        self.assertEqual(response.status_code, 200)
        
        data = response.json()
        self.assertIn('status', data)
        self.assertIn('api_environment', data)
        self.assertIn('quota_used', data)
        self.assertIn('quota_limit', data)
    
    def test_unauthorized_access(self):
        """Test that unauthorized users are redirected"""
        self.client.logout()
        
        response = self.client.get(reverse('amadeus:flight_search'))
        self.assertNotEqual(response.status_code, 200)
        
        response = self.client.get(reverse('amadeus:hotel_search'))
        self.assertNotEqual(response.status_code, 200)
        
        response = self.client.get(reverse('amadeus:search_history'))
        self.assertNotEqual(response.status_code, 200)
    
    def test_flight_results_page_requires_search_id(self):
        """Test that flight results page requires valid search ID"""
        # Test with invalid ID
        response = self.client.get(reverse('amadeus:flight_results', args=[99999]))
        self.assertEqual(response.status_code, 404)
    
    def test_hotel_results_page_requires_search_id(self):
        """Test that hotel results page requires valid search ID"""
        # Test with invalid ID
        response = self.client.get(reverse('amadeus:hotel_results', args=[99999]))
        self.assertEqual(response.status_code, 404)