from django.shortcuts import render, get_object_or_404
from django.http import HttpResponse
from .models import Page, BlogPost, FAQ, BlogCategory
from django.db.models import Q

def home(request):
    """Homepage with hero section and featured content"""
    context = {
        'featured_destinations': [
            {'name': 'Paris', 'country': 'France', 'image': 'paris.jpg'},
            {'name': 'Tokyo', 'country': 'Japan', 'image': 'tokyo.jpg'},
            {'name': 'New York', 'country': 'USA', 'image': 'newyork.jpg'},
            {'name': 'Bali', 'country': 'Indonesia', 'image': 'bali.jpg'},
        ],
        'featured_agents': [
            {
                'name': 'Travel Experts Inc',
                'specialization': 'European Tours',
                'rating': 4.8,
                'image': 'agent1.jpg'
            },
            {
                'name': 'Asia Adventures',
                'specialization': 'Asian Travel',
                'rating': 4.9,
                'image': 'agent2.jpg'
            },
        ],
        'recent_blogs': BlogPost.objects.filter(status='published').order_by('-published_at')[:3],
    }
    return render(request, 'pages/home.html', context)

def about(request):
    """About us page"""
    return render(request, 'pages/about.html')

def how_it_works(request):
    """How it works page explaining the platform"""
    return render(request, 'pages/how_it_works.html')

def faq(request):
    """FAQ page with frequently asked questions"""
    faqs = FAQ.objects.filter(is_active=True).order_by('category', 'order')
    categories = FAQ.objects.values_list('category', flat=True).distinct()
    
    context = {
        'faqs_by_category': {}
    }
    
    for category in categories:
        context['faqs_by_category'][category] = faqs.filter(category=category)
    
    return render(request, 'pages/faq.html', context)

def contact(request):
    """Contact us page"""
    return render(request, 'pages/contact.html')

def privacy(request):
    """Privacy policy page"""
    return render(request, 'pages/privacy.html')

def terms(request):
    """Terms of service page"""
    return render(request, 'pages/terms.html')

def agents(request):
    """Browse agents page"""
    # Mock data for now
    agents = [
        {
            'id': 1,
            'name': 'Travel Experts Inc',
            'specialization': 'European Tours',
            'rating': 4.8,
            'reviews_count': 156,
            'completed_bookings': 89,
            'image': 'agent1.jpg',
            'description': 'Specializing in luxury European travel experiences with personalized itineraries and exceptional service.',
        },
        {
            'id': 2,
            'name': 'Asia Adventures',
            'specialization': 'Asian Travel',
            'rating': 4.9,
            'reviews_count': 203,
            'completed_bookings': 145,
            'image': 'agent2.jpg',
            'description': 'Your gateway to authentic Asian adventures with local guides and immersive cultural experiences.',
        },
    ]
    
    return render(request, 'pages/agents.html', {'agents': agents})

def destinations(request):
    """Browse destinations page"""
    destinations = [
        {'name': 'Paris', 'country': 'France', 'count': 45},
        {'name': 'Rome', 'country': 'Italy', 'count': 38},
        {'name': 'Tokyo', 'country': 'Japan', 'count': 52},
        {'name': 'Bali', 'country': 'Indonesia', 'count': 29},
        {'name': 'Dubai', 'country': 'UAE', 'count': 34},
        {'name': 'London', 'country': 'UK', 'count': 41},
    ]
    
    return render(request, 'pages/destinations.html', {'destinations': destinations})

def blog(request):
    """Travel blog page"""
    posts = BlogPost.objects.filter(status='published').order_by('-published_at')
    categories = BlogCategory.objects.all()
    
    # Get featured posts
    featured_posts = posts.filter(is_featured=True)[:3]
    
    context = {
        'posts': posts,
        'featured_posts': featured_posts,
        'categories': categories,
    }
    
    return render(request, 'pages/blog.html', context)

def blog_post(request, slug):
    """Individual blog post page"""
    post = get_object_or_404(BlogPost, slug=slug, status='published')
    
    # Increment view count
    post.increment_views()
    
    # Get related posts (same category)
    related_posts = BlogPost.objects.filter(
        category=post.category,
        status='published'
    ).exclude(id=post.id).order_by('-published_at')[:3]
    
    context = {
        'post': post,
        'related_posts': related_posts,
    }
    
    return render(request, 'pages/blog_post.html', context)
