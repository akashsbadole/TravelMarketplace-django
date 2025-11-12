from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse, HttpResponse
from django.views.decorators.http import require_http_methods
from django.db.models import Q, Avg, Count
from django.utils import timezone
from datetime import timedelta

from .models import Review, ReviewHelpful, ReviewReport, AgentRatingSummary
from bookings.models import Booking
from agents.models import Agent

@login_required
def create_review(request, booking_id):
    """Create review view"""
    booking = get_object_or_404(Booking, id=booking_id)
    
    # Check if user can review this booking
    if booking.customer != request.user:
        messages.error(request, 'You can only review your own bookings.')
        return redirect('dashboard:bookings')
    
    # Check if booking is completed
    if booking.status != 'completed':
        messages.error(request, 'You can only review completed bookings.')
        return redirect('dashboard:bookings')
    
    # Check if review already exists
    if Review.objects.filter(booking=booking).exists():
        messages.error(request, 'You have already reviewed this booking.')
        return redirect('dashboard:bookings')
    
    if request.method == 'POST':
        try:
            review = Review.objects.create(
                booking=booking,
                customer=request.user,
                agent=booking.quote.agent,
                title=request.POST.get('title'),
                content=request.POST.get('content'),
                rating=int(request.POST.get('rating')),
                communication_rating=int(request.POST.get('communication_rating', 0)) or None,
                value_rating=int(request.POST.get('value_rating', 0)) or None,
                quality_rating=int(request.POST.get('quality_rating', 0)) or None,
                punctuality_rating=int(request.POST.get('punctuality_rating', 0)) or None,
                professionalism_rating=int(request.POST.get('professionalism_rating', 0)) or None,
            )
            
            # Handle photo uploads
            if 'photos' in request.FILES:
                for photo in request.FILES.getlist('photos'):
                    # Would need ReviewPhoto model
                    pass
            
            messages.success(request, 'Your review has been submitted and is pending moderation.')
            return redirect('dashboard:bookings')
            
        except Exception as e:
            messages.error(request, f'Error submitting review: {str(e)}')
    
    context = {
        'booking': booking,
        'agent': booking.quote.agent,
    }
    
    return render(request, 'reviews/create.html', context)

@login_required
def review_list(request):
    """List reviews for agent or user"""
    user_type = request.GET.get('type', 'agent')
    entity_id = request.GET.get('id')
    
    if user_type == 'agent' and entity_id:
        agent = get_object_or_404(Agent, id=entity_id)
        reviews = Review.objects.filter(agent=agent, status='approved').order_by('-created_at')
        
        context = {
            'agent': agent,
            'reviews': reviews,
            'rating_summary': get_agent_rating_summary(agent),
            'user_type': 'agent',
        }
        
    elif user_type == 'user' and entity_id:
        reviews = Review.objects.filter(customer__id=entity_id, status='approved').order_by('-created_at')
        
        context = {
            'reviews': reviews,
            'user_type': 'user',
        }
        
    else:
        # Show all reviews for current user
        reviews = Review.objects.filter(customer=request.user, status='approved').order_by('-created_at')
        
        context = {
            'reviews': reviews,
            'user_type': 'my',
        }
    
    return render(request, 'reviews/list.html', context)

@login_required
def review_detail(request, review_id):
    """Review detail view"""
    review = get_object_or_404(Review, id=review_id)
    
    # Check permissions
    if review.customer != request.user and review.agent.user != request.user:
        return redirect('reviews:list')
    
    context = {
        'review': review,
        'can_edit': review.customer == request.user and review.status == 'pending',
        'can_respond': review.agent.user == request.user,
    }
    
    return render(request, 'reviews/detail.html', context)

@login_required
@require_http_methods(["POST"])
def mark_helpful(request, review_id):
    """Mark review as helpful"""
    review = get_object_or_404(Review, id=review_id)
    
    # Check if already voted
    if ReviewHelpful.objects.filter(review=review, user=request.user).exists():
        return JsonResponse({'success': False, 'message': 'You have already voted on this review'})
    
    is_helpful = request.POST.get('helpful') == 'true'
    
    ReviewHelpful.objects.create(
        review=review,
        user=request.user,
        is_helpful=is_helpful
    )
    
    # Update helpful count
    if is_helpful:
        review.helpful_count += 1
    else:
        review.helpful_count = max(0, review.helpful_count - 1)
    
    review.save()
    
    return JsonResponse({
        'success': True,
        'helpful_count': review.helpful_count
    })

@login_required
@require_http_methods(["POST"])
def report_review(request, review_id):
    """Report a review"""
    review = get_object_or_404(Review, id=review_id)
    
    # Check if already reported
    if ReviewReport.objects.filter(review=review, reporter=request.user).exists():
        return JsonResponse({'success': False, 'message': 'You have already reported this review'})
    
    reason = request.POST.get('reason')
    description = request.POST.get('description', '')
    
    ReviewReport.objects.create(
        review=review,
        reporter=request.user,
        reason=reason,
        description=description
    )
    
    return JsonResponse({
        'success': True,
        'message': 'Review has been reported and will be reviewed by our team'
    })

@login_required
def agent_reviews(request, agent_id):
    """Agent reviews page (public)"""
    agent = get_object_or_404(Agent, id=agent_id)
    
    # Get approved reviews
    reviews = Review.objects.filter(agent=agent, status='approved').order_by('-created_at')
    
    # Calculate rating summary
    rating_summary = get_agent_rating_summary(agent)
    
    context = {
        'agent': agent,
        'reviews': reviews,
        'rating_summary': rating_summary,
    }
    
    return render(request, 'reviews/agent_reviews.html', context)

def get_agent_rating_summary(agent):
    """Get or create agent rating summary"""
    summary, created = AgentRatingSummary.objects.get_or_create(
        agent=agent,
        service_type=None  # Overall rating
    )
    
    if not created:
        summary.update_summary()
    
    return summary
