from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import HttpResponse
from .models import Quote, QuoteItem
from requirements.models import TravelRequirement
from django.db.models import Q

@login_required
def list(request):
    """List of quotes view"""
    quotes_list = Quote.objects.filter(quote_item__agent__user=request.user).distinct()
    
    context = {
        'quotes': quotes_list,
        'user': request.user,
    }
    
    return render(request, 'quotes/list.html', context)

@login_required
def create(request, requirement_id):
    """Create quote view"""
    requirement = get_object_or_404(TravelRequirement, id=requirement_id)
    agent = request.user.agent
    
    if request.method == 'POST':
        # Handle quote creation
        pass
    
    context = {
        'requirement': requirement,
        'agent': agent,
        'user': request.user,
    }
    
    return render(request, 'quotes/create.html', context)

@login_required
def detail(request, quote_id):
    """Quote detail view"""
    quote = get_object_or_404(Quote, id=quote_id)
    
    # Check if user is the agent who created this quote
    if quote.quote_items.first().agent.user != request.user:
        return HttpResponse("Permission denied", status=403)
    
    context = {
        'quote': quote,
        'user': request.user,
    }
    
    return render(request, 'quotes/detail.html', context)
