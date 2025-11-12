from django.core.management.base import BaseCommand
from django.utils import timezone
from pages.models import BlogCategory, BlogPost, BlogTag
from users.models import User

class Command(BaseCommand):
    help = 'Create sample blog data for testing'

    def handle(self, *args, **options):
        # Create a sample user if not exists
        user, created = User.objects.get_or_create(
            username='admin',
            defaults={
                'email': 'admin@example.com',
                'first_name': 'Admin',
                'last_name': 'User',
                'user_type': 'admin',
                'is_staff': True,
                'is_superuser': True,
            }
        )
        
        if created:
            user.set_password('admin123')
            user.save()
            self.stdout.write(self.style.SUCCESS('Created admin user'))
        
        # Create blog categories
        categories_data = [
            ('Travel Tips', 'travel-tips', 'Helpful tips for travelers'),
            ('Destinations', 'destinations', 'Destination guides and reviews'),
            ('Food & Culture', 'food-culture', 'Local cuisine and cultural experiences'),
        ]
        
        categories = []
        for name, slug, description in categories_data:
            category, created = BlogCategory.objects.get_or_create(
                slug=slug,
                defaults={
                    'name': name,
                    'description': description,
                }
            )
            categories.append(category)
            if created:
                self.stdout.write(self.style.SUCCESS(f'Created category: {name}'))
        
        # Create blog tags
        tags_data = [
            ('adventure', 'adventure'),
            ('budget-travel', 'budget-travel'),
            ('luxury', 'luxury'),
            ('solo-travel', 'solo-travel'),
            ('family-travel', 'family-travel'),
        ]
        
        tags = []
        for name, slug in tags_data:
            tag, created = BlogTag.objects.get_or_create(
                slug=slug,
                defaults={'name': name}
            )
            tags.append(tag)
            if created:
                self.stdout.write(self.style.SUCCESS(f'Created tag: {name}'))
        
        # Create sample blog posts
        posts_data = [
            {
                'title': '10 Essential Travel Tips for First-Time Travelers',
                'slug': 'essential-travel-tips-beginners',
                'content': 'Traveling for the first time can be both exciting and overwhelming. Here are 10 essential tips to make your journey smooth and memorable...',
                'excerpt': 'Essential tips to help first-time travelers navigate their adventures with confidence.',
                'category': categories[0],
                'is_featured': True,
            },
            {
                'title': 'Hidden Gems of Southeast Asia',
                'slug': 'hidden-gems-southeast-asia',
                'content': 'Beyond the popular tourist destinations, Southeast Asia offers countless hidden gems waiting to be discovered...',
                'excerpt': 'Discover the lesser-known treasures of Southeast Asia that most tourists miss.',
                'category': categories[1],
                'is_featured': True,
            },
            {
                'title': 'Street Food Guide: Bangkok Edition',
                'slug': 'street-food-guide-bangkok',
                'content': 'Bangkok\'s street food scene is legendary. From spicy tom yum to sweet mango sticky rice, here\'s what you need to try...',
                'excerpt': 'A comprehensive guide to the best street food experiences in Bangkok.',
                'category': categories[2],
                'is_featured': False,
            },
        ]
        
        for post_data in posts_data:
            post, created = BlogPost.objects.get_or_create(
                slug=post_data['slug'],
                defaults={
                    **post_data,
                    'author': user,
                    'status': 'published',
                    'published_at': timezone.now(),
                }
            )
            
            if created:
                # Add some tags to the post
                post.tags.add(*tags[:3])
                post.calculate_reading_time()
                post.save()
                self.stdout.write(self.style.SUCCESS(f'Created blog post: {post.title}'))
        
        self.stdout.write(self.style.SUCCESS('Sample data creation completed!'))
