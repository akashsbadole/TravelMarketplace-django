from django.shortcuts import render, get_object_or_404
from django.http import HttpResponse
from .models import Page, BlogPost, FAQ, BlogCategory, Destination
from django.db.models import Q
from agents.models import Agent

def home(request):
    """Homepage with hero section and featured content"""
    # Get featured destinations from database
    featured_destinations_db = Destination.objects.filter(is_featured=True, is_active=True)[:4]
    
    # Format for home template
    featured_destinations = [
        {
            'name': dest.name,
            'country': dest.country,
            'image': dest.image_url or 'default-destination.jpg',
            'count': dest.requirements_count
        }
        for dest in featured_destinations_db
    ]
    
    # If no featured destinations in database, use fallback
    if not featured_destinations:
        featured_destinations = [
            {'name': 'Paris', 'country': 'France', 'image': 'paris.jpg', 'count': 45},
            {'name': 'Tokyo', 'country': 'Japan', 'image': 'tokyo.jpg', 'count': 52},
            {'name': 'New York', 'country': 'USA', 'image': 'newyork.jpg', 'count': 38},
            {'name': 'Bali', 'country': 'Indonesia', 'image': 'bali.jpg', 'count': 29},
        ]
    
    # Get featured agents from database
    featured_agents_db = Agent.objects.filter(is_featured=True, is_active=True, verification_status='verified').order_by('-average_rating')[:3]
    
    # Format for home template
    featured_agents = []
    for agent in featured_agents_db:
        # Get the first specialization as the main one
        specialization = agent.specializations.first()
        specialization_name = specialization.name if specialization else "Travel Services"
        
        featured_agents.append({
            'name': agent.company_name,
            'specialization': specialization_name,
            'rating': float(agent.average_rating),
            'reviews_count': agent.total_reviews,
            'completed_bookings': agent.completed_bookings,
            'image': agent.company_logo.url if agent.company_logo else 'default-agent.jpg'
        })
    
    # If no featured agents in database, use fallback
    if not featured_agents:
        featured_agents = [
            {
                'name': 'Travel Experts Inc',
                'specialization': 'European Tours',
                'rating': 4.8,
                'reviews_count': 89,
                'completed_bookings': 142,
                'image': 'agent1.jpg'
            },
            {
                'name': 'Asia Adventures',
                'specialization': 'Asian Travel',
                'rating': 4.9,
                'reviews_count': 127,
                'completed_bookings': 195,
                'image': 'agent2.jpg'
            },
        ]
    
    context = {
        'featured_destinations': featured_destinations,
        'featured_agents': featured_agents,
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
    """Browse destinations page with filtering and search functionality"""
    # Get query parameters for filtering
    search_query = request.GET.get('search', '')
    region_filter = request.GET.get('region', '')
    sort_by = request.GET.get('sort', 'popular')
    
    # Start with all active destinations
    destinations_queryset = Destination.objects.filter(is_active=True)
    
    # Apply search filter
    if search_query:
        destinations_queryset = destinations_queryset.filter(
            Q(name__icontains=search_query) |
            Q(country__icontains=search_query) |
            Q(city__icontains=search_query) |
            Q(description__icontains=search_query)
        )
    
    # Apply region filter
    if region_filter:
        destinations_queryset = destinations_queryset.filter(region=region_filter)
    
    # Apply sorting
    if sort_by == 'popular':
        destinations_queryset = destinations_queryset.order_by('-view_count', '-requirements_count')
    elif sort_by == 'name':
        destinations_queryset = destinations_queryset.order_by('name')
    elif sort_by == 'requirements':
        destinations_queryset = destinations_queryset.order_by('-requirements_count')
    elif sort_by == 'rating':
        destinations_queryset = destinations_queryset.order_by('-average_rating')
    else:  # default to featured first, then rating
        destinations_queryset = destinations_queryset.order_by('-is_featured', '-average_rating')
    
    # Get regions for filter dropdown
    regions = Destination.REGION_CHOICES
    
    context = {
        'destinations': destinations_queryset,
        'regions': regions,
        'current_search': search_query,
        'current_region': region_filter,
        'current_sort': sort_by,
    }
    
    return render(request, 'pages/destinations.html', context)

def destination_detail(request, slug):
    """Individual destination detail page"""
    destination = get_object_or_404(Destination, slug=slug, is_active=True)
    
    # Increment view count
    destination.increment_views()
    
    context = {
        'destination': destination,
    }
    
    return render(request, 'pages/destination_detail.html', context)

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