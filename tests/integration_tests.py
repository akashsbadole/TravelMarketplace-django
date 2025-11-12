"""
Integration tests for the Travel Marketplace
Tests the complete user journey from registration to booking
"""
import json
from datetime import datetime, timedelta
from django.test import TestCase, Client, TransactionTestCase
from django.contrib.auth import get_user_model
from django.urls import reverse
from django.utils import timezone
from unittest.mock import patch, MagicMock
from users.models import UserProfile
from agents.models import Agent
from requirements.models import Requirement
from quotes.models import Quote
from bookings.models import Booking
from reviews.models import Review

User = get_user_model()


class UserJourneyTestCase(TransactionTestCase):
    """Test complete user journey from registration to booking"""
    
    def setUp(self):
        self.client = Client()
        
    def test_complete_user_registration_flow(self):
        """Test user registration and profile creation"""
        # Step 1: Register user
        registration_data = {
            'username': 'testuser',
            'email': 'testuser@example.com',
            'password1': 'complexpass123',
            'password2': 'complexpass123',
            'first_name': 'Test',
            'last_name': 'User',
            'phone_number': '+1234567890'
        }
        
        response = self.client.post(reverse('users:register'), registration_data)
        self.assertRedirects(response, reverse('users:login'))
        
        # Verify user was created
        user = User.objects.get(username='testuser')
        self.assertEqual(user.email, 'testuser@example.com')
        self.assertTrue(user.check_password('complexpass123'))
        
        # Verify profile was created
        profile = UserProfile.objects.get(user=user)
        self.assertEqual(profile.phone_number, '+1234567890')
    
    def test_user_login_and_dashboard(self):
        """Test user login and dashboard access"""
        # Create and login user
        user = User.objects.create_user(
            username='dashboarduser',
            email='dashboard@example.com',
            password='testpass123'
        )
        UserProfile.objects.create(user=user)
        
        self.client.login(username='dashboarduser', password='testpass123')
        
        # Test dashboard access
        response = self.client.get(reverse('dashboard:dashboard'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Welcome')
    
    def test_requirement_submission_flow(self):
        """Test requirement submission and quote reception"""
        # Create and login user
        user = User.objects.create_user(
            username='requirementuser',
            email='req@example.com',
            password='testpass123'
        )
        UserProfile.objects.create(user=user)
        self.client.login(username='requirementuser', password='testpass123')
        
        # Step 1: Submit requirement
        requirement_data = {
            'title': 'Test Flight Requirement',
            'service_type': 1,  # Assuming flight service type ID
            'origin_city': 'New York',
            'destination_city': 'London',
            'travel_date_start': (timezone.now() + timedelta(days=30)).strftime('%Y-%m-%d'),
            'travel_date_end': (timezone.now() + timedelta(days=37)).strftime('%Y-%m-%d'),
            'adults': 2,
            'children': 1,
            'budget': '5000',
            'description': 'Test flight requirement for integration testing',
            'flexible_dates': True,
            'flexibility_days': 3
        }
        
        response = self.client.post(reverse('requirements:create'), requirement_data)
        self.assertRedirects(response)
        
        # Verify requirement was created
        requirement = Requirement.objects.get(user=user, title='Test Flight Requirement')
        self.assertEqual(requirement.destination_city, 'London')
        self.assertEqual(requirement.adults, 2)
        self.assertEqual(requirement.budget, '5000.00')
    
    @patch('amadeus.services.AmadeusAPIService.search_flights')
    def test_agent_quote_creation_flow(self, mock_search_flights):
        """Test agent quote creation with Amadeus integration"""
        # Create agent
        agent_user = User.objects.create_user(
            username='agentuser',
            email='agent@example.com',
            password='testpass123'
        )
        agent = Agent.objects.create(
            user=agent_user,
            company_name='Test Travel Agency',
            business_email='business@agency.com',
            phone_number='+1234567890',
            is_verified=True
        )
        self.client.login(username='agentuser', password='testpass123')
        
        # Create requirement for agent to quote on
        requirement = Requirement.objects.create(
            user=User.objects.create_user(
                username='customer',
                email='customer@example.com',
                password='testpass123'
            ),
            title='Flight to Paris',
            service_type_id=1,
            origin_city='New York',
            destination_city='Paris',
            travel_date_start=timezone.now() + timedelta(days=30),
            travel_date_end=timezone.now() + timedelta(days=37),
            adults=2,
            budget=3000
        )
        
        # Mock Amadeus API response
        mock_search_flights.return_value = {
            'data': [
                {
                    'id': 'flight_123',
                    'price': {'total': '1500.00', 'currency': 'USD'},
                    'itineraries': [
                        {
                            'segments': [
                                {
                                    'departure': {'iataCode': 'NYC', 'at': '2024-06-15T10:00:00'},
                                    'arrival': {'iataCode': 'PAR', 'at': '2024-06-15T22:00:00'},
                                    'carrierCode': 'BA',
                                    'number': '123',
                                    'duration': 'PT7H'
                                }
                            ]
                        }
                    ]
                }
            ]
        }
        
        # Step 1: Access quote builder
        response = self.client.get(reverse('amadeus:agent_quote_builder', args=[requirement.id]))
        self.assertEqual(response.status_code, 200)
        
        # Step 2: Create quote
        quote_data = {
            'requirement_id': requirement.id,
            'base_price': '1500.00',
            'markup_amount': '300.00',
            'markup_percentage': '20',
            'final_price': '1800.00',
            'title': 'Flight to Paris - Economy Class',
            'validity_days': 7,
            'inclusions': 'Round-trip flights, 23kg baggage',
            'exclusions': 'Travel insurance, meals',
            'special_notes': 'Book early for best prices'
        }
        
        response = self.client.post(
            reverse('quotes:create'),
            data=json.dumps(quote_data),
            content_type='application/json'
        )
        
        # Verify quote was created
        self.assertTrue(Quote.objects.filter(agent=agent).exists())
        quote = Quote.objects.get(agent=agent)
        self.assertEqual(quote.final_price, '1800.00')
        self.assertEqual(quote.requirement, requirement)
    
    def test_quote_acceptance_and_booking_flow(self):
        """Test quote acceptance and booking creation"""
        # Create user, requirement, and quote
        user = User.objects.create_user(
            username='bookinguser',
            email='booking@example.com',
            password='testpass123'
        )
        UserProfile.objects.create(user=user)
        self.client.login(username='bookinguser', password='testpass123')
        
        requirement = Requirement.objects.create(
            user=user,
            title='Test Booking Requirement',
            service_type_id=1,
            origin_city='New York',
            destination_city='London',
            travel_date_start=timezone.now() + timedelta(days=30),
            travel_date_end=timezone.now() + timedelta(days=37),
            adults=1,
            budget=2000
        )
        
        agent = Agent.objects.create(
            user=User.objects.create_user(
                username='quoteagent',
                email='quoteagent@example.com',
                password='testpass123'
            ),
            company_name='Test Agency',
            is_verified=True
        )
        
        quote = Quote.objects.create(
            requirement=requirement,
            agent=agent,
            title='Test Quote',
            price='1500.00',
            final_price='1650.00',
            validity_period=7,
            inclusions='Flight and baggage',
            status='submitted'
        )
        
        # Step 1: Accept quote
        response = self.client.post(
            reverse('quotes:accept', args=[quote.id]),
            {'action': 'accept'}
        )
        self.assertRedirects(response)
        
        # Verify quote status changed
        quote.refresh_from_db()
        self.assertEqual(quote.status, 'accepted')
        
        # Step 2: Create booking
        booking_data = {
            'quote_id': quote.id,
            'traveler_first_name': 'John',
            'traveler_last_name': 'Doe',
            'traveler_email': 'john@example.com',
            'traveler_phone': '+1234567890',
            'traveler_passport_number': 'AB1234567',
            'special_requests': 'Window seat preferred',
            'terms_accepted': True
        }
        
        response = self.client.post(
            reverse('bookings:create', args=[quote.id]),
            booking_data
        )
        
        # Verify booking was created
        self.assertTrue(Booking.objects.filter(user=user).exists())
        booking = Booking.objects.get(user=user)
        self.assertEqual(booking.quote, quote)
        self.assertEqual(booking.status, 'pending')
        self.assertEqual(booking.total_amount, '1650.00')
    
    @patch('paymentsdetails.views.paypal_payment_process')
    def test_payment_processing_flow(self, mock_paypal):
        """Test payment processing and booking confirmation"""
        # Create booking
        user = User.objects.create_user(
            username='paymentuser',
            email='payment@example.com',
            password='testpass123'
        )
        
        booking = Booking.objects.create(
            user=user,
            quote=Quote.objects.create(
                requirement=Requirement.objects.create(
                    user=user,
                    title='Payment Test',
                    service_type_id=1
                ),
                agent=Agent.objects.create(
                    user=User.objects.create_user(
                        username='paymentagent',
                        email='paymentagent@example.com',
                        password='testpass123'
                    ),
                    company_name='Payment Agency'
                ),
                price='1000.00',
                final_price='1100.00'
            ),
            status='pending',
            total_amount='1100.00'
        )
        
        self.client.login(username='paymentuser', password='testpass123')
        
        # Mock PayPal response
        mock_paypal.return_value = {
            'success': True,
            'payment_id': 'PAYPAL_123',
            'status': 'completed'
        }
        
        # Process payment
        response = self.client.post(
            reverse('paymentsdetails:process_payment', args=[booking.id]),
            {'payment_method': 'paypal'}
        )
        
        # Verify payment processing
        mock_paypal.assert_called_once()
        
        # Verify booking status changed
        booking.refresh_from_db()
        self.assertEqual(booking.status, 'confirmed')
        self.assertEqual(booking.payment_status, 'paid')
    
    def test_review_submission_flow(self):
        """Test review submission after completed trip"""
        # Create completed booking
        user = User.objects.create_user(
            username='reviewuser',
            email='review@example.com',
            password='testpass123'
        )
        
        agent = Agent.objects.create(
            user=User.objects.create_user(
                username='reviewagent',
                email='reviewagent@example.com',
                password='testpass123'
            ),
            company_name='Review Agency'
        )
        
        booking = Booking.objects.create(
            user=user,
            quote=Quote.objects.create(
                requirement=Requirement.objects.create(
                    user=user,
                    title='Review Test',
                    service_type_id=1
                ),
                agent=agent,
                price='1000.00',
                final_price='1100.00'
            ),
            status='completed',
            travel_date_end=timezone.now() - timedelta(days=1)  # Trip ended yesterday
        )
        
        self.client.login(username='reviewuser', password='testpass123')
        
        # Submit review
        review_data = {
            'booking_id': booking.id,
            'rating': 5,
            'title': 'Excellent Service',
            'content': 'Great experience with this agency. Professional and helpful.',
            'communication_rating': 5,
            'value_rating': 4,
            'quality_rating': 5,
            'punctuality_rating': 5,
            'professionalism_rating': 5
        }
        
        response = self.client.post(
            reverse('reviews:create', args=[booking.id]),
            review_data
        )
        
        # Verify review was created
        self.assertTrue(Review.objects.filter(user=user).exists())
        review = Review.objects.get(user=user)
        self.assertEqual(review.rating, 5)
        self.assertEqual(review.booking, booking)
        self.assertEqual(review.agent, agent)
        self.assertEqual(review.title, 'Excellent Service')


class SystemIntegrationTestCase(TransactionTestCase):
    """Test system-level integrations and workflows"""
    
    def setUp(self):
        self.client = Client()
    
    def test_notification_system_integration(self):
        """Test that notifications are sent for key events"""
        # Create users
        customer = User.objects.create_user(
            username='customer',
            email='customer@example.com',
            password='testpass123'
        )
        agent = User.objects.create_user(
            username='agent',
            email='agent@example.com',
            password='testpass123'
        )
        
        # Create requirement
        requirement = Requirement.objects.create(
            user=customer,
            title='Notification Test',
            service_type_id=1,
            origin_city='New York',
            destination_city='London'
        )
        
        # Create quote (should trigger notification)
        agent_profile = Agent.objects.create(
            user=agent,
            company_name='Test Agency'
        )
        
        quote = Quote.objects.create(
            requirement=requirement,
            agent=agent_profile,
            title='Test Quote',
            price='1000.00'
        )
        
        # Verify notifications were created
        from notifications.models import Notification
        customer_notifications = Notification.objects.filter(user=customer)
        agent_notifications = Notification.objects.filter(user=agent)
        
        self.assertTrue(customer_notifications.exists())
        self.assertTrue(agent_notifications.exists())
    
    def test_commission_calculation_integration(self):
        """Test commission calculation on booking confirmation"""
        # Create booking
        booking = Booking.objects.create(
            user=User.objects.create_user(
                username='commissionuser',
                email='commission@example.com',
                password='testpass123'
            ),
            quote=Quote.objects.create(
                requirement=Requirement.objects.create(
                    user=User.objects.create_user(
                        username='commissioncustomer',
                        email='commcustomer@example.com',
                        password='testpass123'
                    ),
                    title='Commission Test',
                    service_type_id=1
                ),
                agent=Agent.objects.create(
                    user=User.objects.create_user(
                        username='commissionagent',
                        email='commissionagent@example.com',
                        password='testpass123'
                    ),
                    company_name='Commission Agency'
                ),
                price='1000.00',
                final_price='1100.00'
            ),
            status='confirmed',
            total_amount='1100.00'
        )
        
        # Verify commission calculations
        expected_agent_commission = 1100.00 * 0.02  # 2%
        expected_customer_commission = 1100.00 * 0.01  # 1%
        expected_platform_commission = expected_agent_commission + expected_customer_commission
        expected_agent_payout = 1100.00 - expected_agent_commission
        
        self.assertEqual(float(booking.agent_commission), expected_agent_commission)
        self.assertEqual(float(booking.customer_commission), expected_customer_commission)
        self.assertEqual(float(booking.platform_commission), expected_platform_commission)
        self.assertEqual(float(booking.agent_payout), expected_agent_payout)
    
    @patch('amadeus.services.AmadeusAPIService.search_flights')
    def test_amadeus_api_integration(self, mock_search):
        """Test Amadeus API integration"""
        # Mock API response
        mock_search.return_value = {
            'data': [
                {
                    'id': 'test_flight_1',
                    'price': {'total': '800.00', 'currency': 'USD'},
                    'itineraries': [
                        {
                            'duration': 'PT8H',
                            'segments': [
                                {
                                    'departure': {'iataCode': 'NYC', 'at': '2024-06-15T10:00:00'},
                                    'arrival': {'iataCode': 'LON', 'at': '2024-06-15T22:00:00'},
                                    'carrierCode': 'BA',
                                    'number': '123'
                                }
                            ]
                        }
                    ]
                }
            ]
        }
        
        # Test flight search
        user = User.objects.create_user(
            username='amadeususer',
            email='amadeus@example.com',
            password='testpass123'
        )
        self.client.login(username='amadeususer', password='testpass123')
        
        search_data = {
            'origin': 1,  # NYC airport ID
            'destination': 2,  # LON airport ID
            'departure_date': '2024-06-15',
            'return_date': '2024-06-22',
            'adults': 1,
            'cabin_class': 'ECONOMY'
        }
        
        response = self.client.post(reverse('amadeus:flight_search'), search_data)
        
        # Verify API was called
        mock_search.assert_called_once()
        
        # Verify search was created
        from amadeus.models import FlightSearch
        self.assertTrue(FlightSearch.objects.filter(user=user).exists())
    
    def test_messaging_system_integration(self):
        """Test real-time messaging integration"""
        # Create users and requirement
        customer = User.objects.create_user(
            username='msgcustomer',
            email='msgcustomer@example.com',
            password='testpass123'
        )
        agent = User.objects.create_user(
            username='msgagent',
            email='msgagent@example.com',
            password='testpass123'
        )
        
        requirement = Requirement.objects.create(
            user=customer,
            title='Message Test',
            service_type_id=1
        )
        
        # Send message
        self.client.login(username='msgcustomer', password='testpass123')
        
        message_data = {
            'content': 'I have a question about this requirement',
            'requirement_id': requirement.id
        }
        
        response = self.client.post(
            reverse('chat:send_message'),
            message_data
        )
        
        # Verify message was created
        from chat.models import Message
        self.assertTrue(Message.objects.filter(
            sender=customer,
            requirement=requirement
        ).exists())
        
        # Verify notification was sent to agent
        from notifications.models import Notification
        agent_notification = Notification.objects.filter(user=agent)
        self.assertTrue(agent_notification.exists())


class ErrorHandlingTestCase(TransactionTestCase):
    """Test error handling and edge cases"""
    
    def setUp(self):
        self.client = Client()
    
    def test_invalid_requirement_data_handling(self):
        """Test handling of invalid requirement data"""
        user = User.objects.create_user(
            username='erroruser',
            email='error@example.com',
            password='testpass123'
        )
        self.client.login(username='erroruser', password='testpass123')
        
        # Test invalid dates
        invalid_data = {
            'title': 'Invalid Requirement',
            'service_type': 1,
            'origin_city': 'New York',
            'destination_city': 'London',
            'travel_date_start': '2024-06-15',  # Past date
            'travel_date_end': '2024-06-10',  # Before start date
            'adults': 0,  # Invalid
            'budget': '-1000'  # Invalid budget
        }
        
        response = self.client.post(reverse('requirements:create'), invalid_data)
        
        # Should return form with errors
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'error')
        
        # Verify no requirement was created
        from requirements.models import Requirement
        self.assertFalse(Requirement.objects.filter(user=user).exists())
    
    def test_unauthorized_access_prevention(self):
        """Test that unauthorized access is properly prevented"""
        # Test accessing agent pages without being an agent
        regular_user = User.objects.create_user(
            username='regularuser',
            email='regular@example.com',
            password='testpass123'
        )
        self.client.login(username='regularuser', password='testpass123')
        
        response = self.client.get(reverse('agents:dashboard'))
        # Should redirect or show unauthorized
        self.assertNotEqual(response.status_code, 200)
        
        # Test accessing other user's data
        other_user = User.objects.create_user(
            username='otheruser',
            email='other@example.com',
            password='testpass123'
        )
        
        requirement = Requirement.objects.create(
            user=other_user,
            title='Other User Requirement',
            service_type_id=1
        )
        
        response = self.client.get(
            reverse('requirements:detail', args=[requirement.id])
        )
        # Should be forbidden
        self.assertEqual(response.status_code, 403 or 404)
    
    def test_api_rate_limiting(self):
        """Test API rate limiting functionality"""
        # This would test the rate limiting implementation
        # Implementation depends on specific rate limiting strategy used
        pass