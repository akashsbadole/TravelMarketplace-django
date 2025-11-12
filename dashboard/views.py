from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.db.models import Count, Sum, Q
from django.utils import timezone
from django.http import JsonResponse
from datetime import timedelta
from requirements.models import TravelRequirement
from quotes.models import Quote
from bookings.models import Booking
from notifications.models import Notification


@login_required
def dashboard(request):
    """Main dashboard view"""
    user = request.user
    
    # Get user's stats
    stats = get_user_stats(user)
    
    # Get recent requirements
    recent_requirements = TravelRequirement.objects.filter(
        user=user
    ).order_by('-created_at')[:5]
    
    # Get recent activity
    recent_activity = get_recent_activity(user)
    
    context = {
        'user': user,
        'stats': stats,
        'recent_requirements': recent_requirements,
        'recent_activity': recent_activity,
    }
    
    return render(request, 'dashboard/dashboard.html', context)


@login_required
def requirements_list(request):
    """List user's requirements"""
    user = request.user
    
    # Get filter parameters
    status_filter = request.GET.get('status', '')
    service_filter = request.GET.get('service', '')
    date_filter = request.GET.get('date', '')
    
    # Build query
    requirements = TravelRequirement.objects.filter(user=user)
    
    if status_filter:
        requirements = requirements.filter(status=status_filter)
    
    if service_filter:
        requirements = requirements.filter(service_type__name=service_filter)
    
    if date_filter:
        if date_filter == 'week':
            requirements = requirements.filter(created_at__gte=timezone.now() - timedelta(days=7))
        elif date_filter == 'month':
            requirements = requirements.filter(created_at__gte=timezone.now() - timedelta(days=30))
        elif date_filter == 'year':
            requirements = requirements.filter(created_at__gte=timezone.now() - timedelta(days=365))
    
    requirements = requirements.order_by('-created_at')
    
    # Get filter options
    service_types = TravelRequirement.objects.filter(
        user=user
    ).values_list('service_type__name', flat=True).distinct()
    
    context = {
        'requirements': requirements,
        'service_types': service_types,
        'current_status': status_filter,
        'current_service': service_filter,
        'current_date': date_filter,
        'status_choices': TravelRequirement.STATUS_CHOICES,
    }
    
    return render(request, 'dashboard/requirements.html', context)


@login_required
def requirement_detail(request, requirement_id):
    """Requirement detail with quotes"""
    user = request.user
    requirement = get_object_or_404(TravelRequirement, id=requirement_id, user=user)
    
    # Get quotes for this requirement
    quotes = Quote.objects.filter(
        requirement=requirement
    ).select_related('agent', 'agent__user').order_by('-created_at')
    
    # Check if quotes are expired
    for quote in quotes:
        quote.is_expired_check = quote.is_expired()
    
    context = {
        'requirement': requirement,
        'quotes': quotes,
    }
    
    return render(request, 'dashboard/requirement_detail.html', context)


@login_required
def bookings_list(request):
    """List user's bookings"""
    user = request.user
    
    # Get filter parameters
    status_filter = request.GET.get('status', '')
    date_filter = request.GET.get('date', '')
    
    # Build query
    bookings = Booking.objects.filter(customer=user).select_related(
        'quote', 'quote__requirement', 'quote__agent', 'quote__agent__user'
    )
    
    if status_filter:
        bookings = bookings.filter(status=status_filter)
    
    if date_filter:
        if date_filter == 'upcoming':
            bookings = bookings.filter(
                quote__requirement__travel_date_start__gte=timezone.now().date()
            )
        elif date_filter == 'past':
            bookings = bookings.filter(
                quote__requirement__travel_date_start__lt=timezone.now().date()
            )
        elif date_filter == 'month':
            bookings = bookings.filter(created_at__gte=timezone.now() - timedelta(days=30))
    
    bookings = bookings.order_by('-created_at')
    
    context = {
        'bookings': bookings,
        'current_status': status_filter,
        'current_date': date_filter,
        'status_choices': Booking.STATUS_CHOICES,
    }
    
    return render(request, 'dashboard/bookings.html', context)


@login_required
def booking_detail(request, booking_id):
    """Booking detail view"""
    user = request.user
    booking = get_object_or_404(
        Booking, 
        id=booking_id, 
        customer=user
    ).select_related('quote', 'quote__requirement', 'quote__agent', 'quote__agent__user')
    
    context = {
        'booking': booking,
    }
    
    return render(request, 'dashboard/booking_detail.html', context)


@login_required
def notifications(request):
    """User notifications"""
    user = request.user
    
    # Get notifications
    notifications_list = Notification.objects.filter(
        user=user
    ).order_by('-created_at')
    
    # Mark as read
    if request.method == 'POST' and 'mark_read' in request.POST:
        notification_id = request.POST.get('notification_id')
        notification = get_object_or_404(Notification, id=notification_id, user=user)
        notification.is_read = True
        notification.save()
    
    # Mark all as read
    if request.method == 'POST' and 'mark_all_read' in request.POST:
        notifications_list.update(is_read=True)
    
    context = {
        'notifications': notifications_list,
        'unread_count': notifications_list.filter(is_read=False).count(),
    }
    
    return render(request, 'dashboard/notifications.html', context)


@login_required
def quote_comparison(request, requirement_id):
    """Compare quotes for a requirement"""
    user = request.user
    requirement = get_object_or_404(TravelRequirement, id=requirement_id, user=user)
    
    # Get accepted and submitted quotes
    quotes = Quote.objects.filter(
        requirement=requirement,
        status__in=['submitted', 'accepted']
    ).select_related('agent', 'agent__user').order_by('total_amount')
    
    context = {
        'requirement': requirement,
        'quotes': quotes,
    }
    
    return render(request, 'dashboard/quote_comparison.html', context)


@login_required
def accept_quote(request, quote_id):
    """Accept a quote"""
    if request.method == 'POST':
        user = request.user
        quote = get_object_or_404(Quote, id=quote_id, customer=user)
        
        if quote.status != 'submitted':
            return JsonResponse({'success': False, 'message': 'Quote cannot be accepted'})
        
        if quote.is_expired():
            return JsonResponse({'success': False, 'message': 'Quote has expired'})
        
        try:
            quote.accept_quote()
            return JsonResponse({'success': True, 'message': 'Quote accepted successfully'})
        except Exception as e:
            return JsonResponse({'success': False, 'message': str(e)})
    
    return JsonResponse({'success': False, 'message': 'Invalid request method'})


@login_required
def reject_quote(request, quote_id):
    """Reject a quote"""
    if request.method == 'POST':
        user = request.user
        quote = get_object_or_404(Quote, id=quote_id, customer=user)
        
        if quote.status in ['accepted', 'rejected']:
            return JsonResponse({'success': False, 'message': 'Quote cannot be rejected'})
        
        try:
            quote.reject_quote()
            return JsonResponse({'success': True, 'message': 'Quote rejected successfully'})
        except Exception as e:
            return JsonResponse({'success': False, 'message': str(e)})
    
    return JsonResponse({'success': False, 'message': 'Invalid request method'})


def get_user_stats(user):
    """Get user statistics"""
    from decimal import Decimal
    
    # Active requirements
    active_requirements = TravelRequirement.objects.filter(
        user=user,
        status__in=['open', 'draft']
    ).count()
    
    # Received quotes
    received_quotes = Quote.objects.filter(
        customer=user
    ).count()
    
    # Active bookings
    active_bookings = Booking.objects.filter(
        customer=user,
        status__in=['paid', 'confirmed']
    ).count()
    
    # Total spent
    total_spent = Booking.objects.filter(
        customer=user,
        status__in=['paid', 'confirmed', 'completed']
    ).aggregate(total=Sum('total_amount'))['total'] or Decimal('0.00')
    
    return {
        'active_requirements': active_requirements,
        'received_quotes': received_quotes,
        'active_bookings': active_bookings,
        'total_spent': total_spent,
    }


def get_recent_activity(user):
    """Get recent activity for user"""
    activity = []
    
    # Recent quotes received
    recent_quotes = Quote.objects.filter(
        customer=user
    ).order_by('-created_at')[:3]
    
    for quote in recent_quotes:
        activity.append({
            'type': 'quote',
            'message': f'Received quote from {quote.agent.company_name} for {quote.requirement.title}',
            'created_at': quote.created_at,
        })
    
    # Recent bookings
    recent_bookings = Booking.objects.filter(
        customer=user
    ).order_by('-created_at')[:3]
    
    for booking in recent_bookings:
        activity.append({
            'type': 'booking',
            'message': f'Booking confirmed for {booking.quote.requirement.title}',
            'created_at': booking.created_at,
        })
    
    # Sort by date
    activity.sort(key=lambda x: x['created_at'], reverse=True)
    
    return activity[:5]