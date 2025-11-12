from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse, HttpResponse
from django.db.models import Q, Count, Sum, Avg
from django.utils import timezone
from datetime import timedelta
from django.views.decorators.http import require_http_methods
from django.core.serializers.json import DjangoJSONEncoder
import json

@login_required
def list(request):
    """List of notifications view"""
    user = request.user
    
    # Get notifications for this user
    notifications_list = user.received_notifications.select_related('sender').order_by('-created_at')
    
    # Get unread count
    unread_count = user.received_notifications.filter(is_read=False).count()
    
    context = {
        'notifications': notifications_list,
        'unread_count': unread_count,
        'user': user,
    }
    
    return render(request, 'notifications/list.html', context)

@login_required
@require_http_methods(["POST"])
def mark_read(request, notification_id):
    """Mark notification as read"""
    notification = get_object_or_404(
        request.user.received_notifications, 
        id=notification_id
    )
    
    notification.is_read = True
    notification.read_at = timezone.now()
    notification.save()
    
    return JsonResponse({
        'success': True,
        'message': 'Notification marked as read'
    })

@login_required
@require_http_methods(["POST"])
def mark_all_read(request):
    """Mark all notifications as read"""
    count = request.user.received_notifications.filter(is_read=False).update(
        is_read=True,
        read_at=timezone.now()
    )
    
    return JsonResponse({
        'success': True,
        'message': f'{count} notifications marked as read'
    })

@login_required
def preferences(request):
    """Notification preferences view"""
    user = request.user
    
    if request.method == 'POST':
        # Update notification preferences
        email_notifications = request.POST.get('email_notifications', 'off') == 'on'
        push_notifications = request.POST.get('push_notifications', 'off') == 'on'
        sms_notifications = request.POST.get('sms_notifications', 'off') == 'on'
        
        # Save preferences
        profile = user.profile
        profile.email_notifications = email_notifications
        profile.push_notifications = push_notifications
        profile.sms_notifications = sms_notifications
        profile.save()
        
        messages.success(request, "Preferences updated successfully!")
        return redirect('notifications:preferences')
    
    # Get current preferences
    try:
        profile = user.profile
    except:
        profile = None
    
    context = {
        'user': user,
        'email_notifications': profile.email_notifications if profile else True,
        'push_notifications': profile.push_notifications if profile else True,
        'sms_notifications': profile.sms_notifications if profile else False,
    }
    
    return render(request, 'notifications/preferences.html', context)

@login_required
def get_unread_count(request):
    """Get unread notifications count (API)"""
    count = request.user.received_notifications.filter(is_read=False).count()
    
    return JsonResponse({
        'unread_count': count
    })

def create_notification(user, title, message, notification_type='info', 
                           sender=None, url=None, related_object=None):
    """Helper function to create notifications"""
    from .models import Notification
    
    notification = Notification.objects.create(
        recipient=user,
        title=title,
        message=message,
        notification_type=notification_type,
        sender=sender,
        url=url,
        related_object=related_object
    )
    
    # Send email notification if enabled
    try:
        if user.profile.email_notifications:
            from django.core.mail import send_mail
            from django.conf import settings
            
            send_mail(
                subject=f"Travel Marketplace - {title}",
                message=message,
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[user.email],
                fail_silently=False,
            )
    except:
        pass
    
    return notification

# Notification creation helpers for different types
def create_quote_notification(user, quote):
    """Create notification for new quote"""
    title = "New Quote Received"
    message = f"You have received a new quote for your travel requirement: {quote.requirement.title}"
    url = f"/quotes/{quote.id}/"
    
    return create_notification(
        user=user,
        title=title,
        message=message,
        notification_type='quote',
        sender=quote.quote_items.first().agent.user if quote.quote_items.exists() else None,
        url=url,
        related_object=quote
    )

def create_booking_notification(user, booking):
    """Create notification for new booking"""
    title = "Booking Confirmation"
    message = f"Your booking #{booking.id} has been confirmed. Total: ${booking.total_amount}"
    url = f"/bookings/{booking.id}/"
    
    return create_notification(
        user=user,
        title=title,
        message=message,
        notification_type='booking',
        url=url,
        related_object=booking
    )

def create_payment_notification(user, payment):
    """Create notification for payment confirmation"""
    title = "Payment Confirmation"
    message = f"Payment of ${payment.amount} has been received for your booking."
    url = f"/bookings/{payment.booking.id}/"
    
    return create_notification(
        user=user,
        title=title,
        message=message,
        notification_type='payment',
        url=url,
        related_object=payment
    )

def create_agent_request_notification(admin_user, agent):
    """Create notification for new agent registration"""
    title = "New Agent Registration"
    message = f"A new agent {agent.user.get_full_name()} has registered and needs approval."
    url = f"/admin-panel/agents/{agent.id}/"
    
    return create_notification(
        user=admin_user,
        title=title,
        message=message,
        notification_type='admin',
        url=url,
        related_object=agent
    )
