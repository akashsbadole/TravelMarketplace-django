from django.core.management.base import BaseCommand
from django.utils import timezone
from django.contrib.auth import get_user_model
from agents.models import Agent
from requirements.models import ServiceType

User = get_user_model()

class Command(BaseCommand):
    help = 'Create sample agents for testing'

    def handle(self, *args, **options):
        # Create sample users for agents if they don't exist
        agent_data = [
            {
                'username': 'travel_experts',
                'email': 'info@travelexperts.com',
                'first_name': 'John',
                'last_name': 'Smith',
                'user_type': 'agent',
            },
            {
                'username': 'asia_adventures',
                'email': 'contact@asiaadventures.com',
                'first_name': 'Mei',
                'last_name': 'Lin',
                'user_type': 'agent',
            },
            {
                'username': 'luxury_tours',
                'email': 'book@luxurytours.com',
                'first_name': 'Alexander',
                'last_name': 'Dubois',
                'user_type': 'agent',
            },
            {
                'username': 'adventure_plus',
                'email': 'info@adventureplus.com',
                'first_name': 'Carlos',
                'last_name': 'Rodriguez',
                'user_type': 'agent',
            },
            {
                'username': 'family_holidays',
                'email': 'hello@familyholidays.com',
                'first_name': 'Sarah',
                'last_name': 'Johnson',
                'user_type': 'agent',
            },
        ]
        
        agent_users = []
        for user_info in agent_data:
            user, created = User.objects.get_or_create(
                email=user_info['email'],
                defaults={
                    **user_info,
                    'is_staff': False,
                    'is_active': True,
                }
            )
            if created:
                user.set_password('password123')
                user.save()
                self.stdout.write(self.style.SUCCESS(f'Created user: {user.email}'))
            agent_users.append(user)
        
        # Get or create service types for specializations
        service_type_data = [
            {'name': 'Flight Booking'},
            {'name': 'Hotel Booking'},
            {'name': 'Tour Packages'},
            {'name': 'Travel Insurance'},
            {'name': 'Visa Assistance'},
            {'name': 'Cruise Booking'},
        ]
        
        service_types = []
        for st_data in service_type_data:
            service_type, created = ServiceType.objects.get_or_create(
                name=st_data['name'],
                defaults=st_data
            )
            service_types.append(service_type)
            if created:
                self.stdout.write(self.style.SUCCESS(f'Created service type: {service_type.name}'))
        
        # Create sample agents
        agents_info = [
            {
                'user': agent_users[0],
                'company_name': 'Travel Experts Inc',
                'company_registration_number': 'TE2023001',
                'gst_number': 'GSTTE2023001',
                'pan_number': 'PANTE2023001',
                'business_address': '123 Main Street, Suite 100',
                'business_city': 'New York',
                'business_state': 'NY',
                'business_country': 'USA',
                'business_postal_code': '10001',
                'business_phone': '+1-212-555-0101',
                'business_email': 'info@travelexperts.com',
                'contact_person_name': 'John Smith',
                'contact_person_designation': 'CEO',
                'years_in_business': 12,
                'license_number': 'NY2023TRV001',
                'destinations_served': 'France, Italy, Spain, Germany, UK, Netherlands, Switzerland',
                'verification_status': 'verified',
                'verification_date': timezone.now(),
                'total_bookings': 156,
                'completed_bookings': 142,
                'average_rating': 4.8,
                'total_reviews': 89,
                'is_featured': True,
                'is_active': True,
                'specializations': [service_types[0], service_types[1], service_types[2]],  # Flight, Hotel, Tours
            },
            {
                'user': agent_users[1],
                'company_name': 'Asia Adventures',
                'company_registration_number': 'AA2023002',
                'gst_number': 'GSTAA2023002',
                'pan_number': 'PANAA2023002',
                'business_address': '456 Orchard Road, #12-08',
                'business_city': 'Singapore',
                'business_state': 'Singapore',
                'business_country': 'Singapore',
                'business_postal_code': '238879',
                'business_phone': '+65-6555-0202',
                'business_email': 'contact@asiaadventures.com',
                'contact_person_name': 'Mei Lin',
                'contact_person_designation': 'Managing Director',
                'years_in_business': 8,
                'license_number': 'SG2023TRV002',
                'destinations_served': 'Japan, Thailand, Vietnam, Cambodia, Indonesia, Malaysia, Philippines',
                'verification_status': 'verified',
                'verification_date': timezone.now(),
                'total_bookings': 203,
                'completed_bookings': 195,
                'average_rating': 4.9,
                'total_reviews': 127,
                'is_featured': True,
                'is_active': True,
                'specializations': [service_types[2], service_types[4], service_types[0]],  # Tours, Visa, Flight
            },
            {
                'user': agent_users[2],
                'company_name': 'Luxury Tours & Co',
                'company_registration_number': 'LT2023003',
                'gst_number': 'GSTLT2023003',
                'pan_number': 'PANLT2023003',
                'business_address': '78 Champs-Élysées',
                'business_city': 'Paris',
                'business_state': 'Île-de-France',
                'business_country': 'France',
                'business_postal_code': '75008',
                'business_phone': '+33-1-555-0303',
                'business_email': 'book@luxurytours.com',
                'contact_person_name': 'Alexander Dubois',
                'contact_person_designation': 'Director',
                'years_in_business': 15,
                'license_number': 'FR2023TRV003',
                'destinations_served': 'France, Italy, Monaco, Switzerland, Austria, Greece, Croatia',
                'verification_status': 'verified',
                'verification_date': timezone.now(),
                'total_bookings': 98,
                'completed_bookings': 94,
                'average_rating': 4.9,
                'total_reviews': 67,
                'is_featured': True,
                'is_active': True,
                'specializations': [service_types[1], service_types[2], service_types[5]],  # Hotel, Tours, Cruise
            },
            {
                'user': agent_users[3],
                'company_name': 'Adventure Plus',
                'company_registration_number': 'AP2023004',
                'gst_number': 'GSTAP2023004',
                'pan_number': 'PANAP2023004',
                'business_address': '901 Adventure Plaza',
                'business_city': 'Denver',
                'business_state': 'CO',
                'business_country': 'USA',
                'business_postal_code': '80202',
                'business_phone': '+1-303-555-0404',
                'business_email': 'info@adventureplus.com',
                'contact_person_name': 'Carlos Rodriguez',
                'contact_person_designation': 'Founder',
                'years_in_business': 10,
                'license_number': 'US2023TRV004',
                'destinations_served': 'Costa Rica, Peru, Chile, Argentina, New Zealand, Nepal, Tanzania',
                'verification_status': 'verified',
                'verification_date': timezone.now(),
                'total_bookings': 134,
                'completed_bookings': 128,
                'average_rating': 4.7,
                'total_reviews': 98,
                'is_featured': False,
                'is_active': True,
                'specializations': [service_types[2], service_types[3], service_types[0]],  # Tours, Insurance, Flight
            },
            {
                'user': agent_users[4],
                'company_name': 'Family Holidays',
                'company_registration_number': 'FH2023005',
                'gst_number': 'GSTFH2023005',
                'pan_number': 'PANFH2023005',
                'business_address': '321 Family Lane',
                'business_city': 'Orlando',
                'business_state': 'FL',
                'business_country': 'USA',
                'business_postal_code': '32801',
                'business_phone': '+1-407-555-0505',
                'business_email': 'hello@familyholidays.com',
                'contact_person_name': 'Sarah Johnson',
                'contact_person_designation': 'Owner',
                'years_in_business': 7,
                'license_number': 'FL2023TRV005',
                'destinations_served': 'USA, Canada, Mexico, Caribbean, UK, Australia, Japan',
                'verification_status': 'verified',
                'verification_date': timezone.now(),
                'total_bookings': 187,
                'completed_bookings': 182,
                'average_rating': 4.6,
                'total_reviews': 143,
                'is_featured': False,
                'is_active': True,
                'specializations': [service_types[0], service_types[1], service_types[3]],  # Flight, Hotel, Insurance
            },
        ]
        
        for agent_info in agents_info:
            specializations = agent_info.pop('specializations', [])
            agent, created = Agent.objects.get_or_create(
                user=agent_info['user'],
                defaults=agent_info
            )
            
            if created:
                # Add specializations
                agent.specializations.add(*specializations)
                self.stdout.write(self.style.SUCCESS(f'Created agent: {agent.company_name}'))
        
        self.stdout.write(self.style.SUCCESS('Sample agents creation completed!'))