from django.core.management.base import BaseCommand
from pages.models import Destination

class Command(BaseCommand):
    help = 'Create sample destinations for testing'

    def handle(self, *args, **options):
        destinations_data = [
            {
                'name': 'Paris',
                'slug': 'paris',
                'description': 'The City of Light, famous for the Eiffel Tower, Louvre Museum, and romantic atmosphere. Paris offers world-class art, cuisine, and fashion.',
                'country': 'France',
                'city': 'Paris',
                'region': 'europe',
                'image_url': 'https://picsum.photos/seed/paris/800/600.jpg',
                'gallery_images': [
                    'https://picsum.photos/seed/eiffel-tower/400/300.jpg',
                    'https://picsum.photos/seed/louvre/400/300.jpg',
                    'https://picsum.photos/seed/notre-dame/400/300.jpg'
                ],
                'popular_attractions': [
                    'Eiffel Tower',
                    'Louvre Museum',
                    'Notre-Dame Cathedral',
                    'Arc de Triomphe',
                    'Champs-Élysées'
                ],
                'best_time_to_visit': 'spring',
                'average_rating': 4.8,
                'price_range': 'premium',
                'requirements_count': 45,
                'view_count': 1250,
                'is_featured': True,
                'is_active': True,
            },
            {
                'name': 'Tokyo',
                'slug': 'tokyo',
                'description': 'A mesmerizing blend of ancient traditions and cutting-edge technology. Tokyo offers everything from historic temples to neon-lit skyscrapers.',
                'country': 'Japan',
                'city': 'Tokyo',
                'region': 'asia',
                'image_url': 'https://picsum.photos/seed/tokyo/800/600.jpg',
                'gallery_images': [
                    'https://picsum.photos/seed/mount-fuji/400/300.jpg',
                    'https://picsum.photos/seed/senso-ji/400/300.jpg',
                    'https://picsum.photos/seed/shibuya/400/300.jpg'
                ],
                'popular_attractions': [
                    'Tokyo Skytree',
                    'Senso-ji Temple',
                    'Meiji Shrine',
                    'Shibuya Crossing',
                    'Tsukiji Fish Market'
                ],
                'best_time_to_visit': 'spring',
                'average_rating': 4.9,
                'price_range': 'moderate',
                'requirements_count': 52,
                'view_count': 1480,
                'is_featured': True,
                'is_active': True,
            },
            {
                'name': 'New York',
                'slug': 'new-york',
                'description': 'The city that never sleeps, New York is a global hub for culture, finance, and entertainment. From Broadway to Central Park, NYC has it all.',
                'country': 'USA',
                'city': 'New York',
                'region': 'americas',
                'image_url': 'https://picsum.photos/seed/newyork/800/600.jpg',
                'gallery_images': [
                    'https://picsum.photos/seed/statue-of-liberty/400/300.jpg',
                    'https://picsum.photos/seed/times-square/400/300.jpg',
                    'https://picsum.photos/seed/central-park/400/300.jpg'
                ],
                'popular_attractions': [
                    'Statue of Liberty',
                    'Times Square',
                    'Central Park',
                    'Empire State Building',
                    'Brooklyn Bridge'
                ],
                'best_time_to_visit': 'autumn',
                'average_rating': 4.7,
                'price_range': 'premium',
                'requirements_count': 38,
                'view_count': 1100,
                'is_featured': True,
                'is_active': True,
            },
            {
                'name': 'Bali',
                'slug': 'bali',
                'description': 'A tropical paradise known for its forested volcanic mountains, iconic rice paddies, beaches and coral reefs. Bali offers spiritual retreats and surfing adventures.',
                'country': 'Indonesia',
                'city': 'Denpasar',
                'region': 'asia',
                'image_url': 'https://picsum.photos/seed/bali/800/600.jpg',
                'gallery_images': [
                    'https://picsum.photos/seed/ubud/400/300.jpg',
                    'https://picsum.photos/seed/temple/400/300.jpg',
                    'https://picsum.photos/seed/rice-terrace/400/300.jpg'
                ],
                'popular_attractions': [
                    'Ubud Rice Terraces',
                    'Tanah Lot Temple',
                    'Seminyak Beach',
                    'Mount Batur',
                    'Sacred Monkey Forest'
                ],
                'best_time_to_visit': 'all_year',
                'average_rating': 4.6,
                'price_range': 'budget',
                'requirements_count': 29,
                'view_count': 950,
                'is_featured': True,
                'is_active': True,
            },
            {
                'name': 'Rome',
                'slug': 'rome',
                'description': 'The Eternal City, where ancient ruins meet Renaissance art. Rome is home to the Colosseum, Vatican City, and countless historical treasures.',
                'country': 'Italy',
                'city': 'Rome',
                'region': 'europe',
                'image_url': 'https://picsum.photos/seed/rome/800/600.jpg',
                'gallery_images': [
                    'https://picsum.photos/seed/colosseum/400/300.jpg',
                    'https://picsum.photos/seed/vatican/400/300.jpg',
                    'https://picsum.photos/seed/trevi-fountain/400/300.jpg'
                ],
                'popular_attractions': [
                    'Colosseum',
                    'Vatican City',
                    'Trevi Fountain',
                    'Pantheon',
                    'Sistine Chapel'
                ],
                'best_time_to_visit': 'spring',
                'average_rating': 4.8,
                'price_range': 'moderate',
                'requirements_count': 41,
                'view_count': 1180,
                'is_featured': False,
                'is_active': True,
            },
            {
                'name': 'Dubai',
                'slug': 'dubai',
                'description': 'A modern oasis of luxury and innovation. Dubai is known for its stunning architecture, luxury shopping, and vibrant nightlife.',
                'country': 'UAE',
                'city': 'Dubai',
                'region': 'middle_east',
                'image_url': 'https://picsum.photos/seed/dubai/800/600.jpg',
                'gallery_images': [
                    'https://picsum.photos/seed/burj-khalifa/400/300.jpg',
                    'https://picsum.photos/seed/dubai-mall/400/300.jpg',
                    'https://picsum.photos/seed/palm-jumeirah/400/300.jpg'
                ],
                'popular_attractions': [
                    'Burj Khalifa',
                    'Dubai Mall',
                    'Palm Jumeirah',
                    'Dubai Marina',
                    'Gold Souk'
                ],
                'best_time_to_visit': 'winter',
                'average_rating': 4.7,
                'price_range': 'luxury',
                'requirements_count': 33,
                'view_count': 1020,
                'is_featured': False,
                'is_active': True,
            },
            {
                'name': 'London',
                'slug': 'london',
                'description': 'A perfect blend of history and modernity, London offers world-class museums, iconic landmarks, and diverse cultural experiences.',
                'country': 'UK',
                'city': 'London',
                'region': 'europe',
                'image_url': 'https://picsum.photos/seed/london/800/600.jpg',
                'gallery_images': [
                    'https://picsum.photos/seed/big-ben/400/300.jpg',
                    'https://picsum.photos/seed/tower-bridge/400/300.jpg',
                    'https://picsum.photos/seed/british-museum/400/300.jpg'
                ],
                'popular_attractions': [
                    'Big Ben',
                    'Tower Bridge',
                    'British Museum',
                    'Buckingham Palace',
                    'London Eye'
                ],
                'best_time_to_visit': 'summer',
                'average_rating': 4.6,
                'price_range': 'premium',
                'requirements_count': 36,
                'view_count': 1050,
                'is_featured': False,
                'is_active': True,
            },
            {
                'name': 'Sydney',
                'slug': 'sydney',
                'description': 'Famous for its harbourfront Sydney Opera House and beautiful beaches. Sydney offers a relaxed lifestyle with stunning natural beauty.',
                'country': 'Australia',
                'city': 'Sydney',
                'region': 'oceania',
                'image_url': 'https://picsum.photos/seed/sydney/800/600.jpg',
                'gallery_images': [
                    'https://picsum.photos/seed/opera-house/400/300.jpg',
                    'https://picsum.photos/seed/harbour-bridge/400/300.jpg',
                    'https://picsum.photos/seed/bondi-beach/400/300.jpg'
                ],
                'popular_attractions': [
                    'Sydney Opera House',
                    'Sydney Harbour Bridge',
                    'Bondi Beach',
                    'Darling Harbour',
                    'Royal Botanic Gardens'
                ],
                'best_time_to_visit': 'all_year',
                'average_rating': 4.7,
                'price_range': 'moderate',
                'requirements_count': 25,
                'view_count': 890,
                'is_featured': False,
                'is_active': True,
            },
        ]
        
        for dest_data in destinations_data:
            destination, created = Destination.objects.get_or_create(
                slug=dest_data['slug'],
                defaults=dest_data
            )
            
            if created:
                self.stdout.write(self.style.SUCCESS(f'Created destination: {destination.name}'))
            else:
                self.stdout.write(self.style.WARNING(f'Destination already exists: {destination.name}'))
        
        self.stdout.write(self.style.SUCCESS('Sample destinations creation completed!'))