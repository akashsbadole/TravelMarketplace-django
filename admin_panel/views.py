from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from django.http import JsonResponse, HttpResponse
from django.views.decorators.http import require_http_methods
from django.utils import timezone
from django.db.models import Count, Sum, Avg, Q
from django.contrib.auth.models import User
from datetime import datetime, timedelta
import json

from users.models import UserProfile
from agents.models import Agent
from requirements.models import TravelRequirement
from quotes.models import Quote
from bookings.models import Booking
from .models import DashboardStats, SystemSettings, AdminActivity, SystemAlert, DataExport, GlobalSettings

def is_admin(user):
    """Check if user is admin"""
    return user.is_authenticated and (user.is_superuser or user.user_type == 'admin')

@login_required
@user_passes_test(is_admin)
def dashboard(request):
    """Admin dashboard view"""
    # Get current stats
    from django.utils import timezone
    today = timezone.now().date()
    thirty_days_ago = today - timedelta(days=30)
    
    # User stats
    total_users = User.objects.filter(user_type='customer').count()
    new_users = User.objects.filter(
        user_type='customer',
        date_joined__gte=thirty_days_ago
    ).count()
    total_agents = Agent.objects.count()
    new_agents = Agent.objects.filter(created_at__gte=thirty_days_ago).count()
    verified_agents = Agent.objects.filter(verification_status='verified').count()
    
    # Booking stats
    total_bookings = Booking.objects.count()
    new_bookings = Booking.objects.filter(created_at__gte=thirty_days_ago).count()
    completed_bookings = Booking.objects.filter(status='completed').count()
    
    # Financial stats
    total_revenue = Booking.objects.filter(
        status='completed'
    ).aggregate(total=Sum('total_amount'))['total'] or 0
    commission_revenue = Booking.objects.filter(
        status='completed'
    ).aggregate(total=Sum('platform_commission'))['total'] or 0
    
    # Requirements and quotes
    total_requirements = TravelRequirement.objects.count()
    new_requirements = TravelRequirement.objects.filter(
        created_at__gte=thirty_days_ago
    ).count()
    total_quotes = Quote.objects.count()
    
    context = {
        'stats': {
            'total_users': total_users,
            'new_users': new_users,
            'total_agents': total_agents,
            'new_agents': new_agents,
            'verified_agents': verified_agents,
            'total_bookings': total_bookings,
            'new_bookings': new_bookings,
            'completed_bookings': completed_bookings,
            'total_revenue': total_revenue,
            'commission_revenue': commission_revenue,
            'total_requirements': total_requirements,
            'new_requirements': new_requirements,
            'total_quotes': total_quotes,
        },
        'recent_activities': AdminActivity.objects.select_related('admin_user').order_by('-created_at')[:10],
        'system_alerts': SystemAlert.objects.filter(
            is_active=True,
            is_acknowledged=False
        ).order_by('-created_at')[:5],
    }
    
    return render(request, 'admin_panel/dashboard.html', context)

@login_required
@user_passes_test(is_admin)
def manage_users(request):
    """Manage users view"""
    user_type = request.GET.get('type', 'customer')
    status = request.GET.get('status', 'all')
    search = request.GET.get('search', '')
    
    users = User.objects.filter(user_type=user_type)
    
    if status != 'all':
        if status == 'active':
            users = users.filter(is_active=True)
        elif status == 'inactive':
            users = users.filter(is_active=False)
    
    if search:
        users = users.filter(
            Q(username__icontains=search) |
            Q(email__icontains=search) |
            Q(first_name__icontains=search) |
            Q(last_name__icontains=search)
        )
    
    if user_type == 'customer':
        users = users.select_related('profile')
    elif user_type == 'agent':
        users = users.select_related('agent')
    
    context = {
        'users': users,
        'user_type': user_type,
        'status': status,
        'search': search,
    }
    
    return render(request, 'admin_panel/manage_users.html', context)

@login_required
@user_passes_test(is_admin)
def manage_agents(request):
    """Manage agents view with verification workflow"""
    status = request.GET.get('status', 'all')
    
    agents = Agent.objects.select_related('user')
    
    if status != 'all':
        agents = agents.filter(verification_status=status)
    
    context = {
        'agents': agents,
        'status': status,
    }
    
    return render(request, 'admin_panel/manage_agents.html', context)

@login_required
@user_passes_test(is_admin)
@require_http_methods(["POST"])
def verify_agent(request, agent_id):
    """Verify or reject agent"""
    agent = get_object_or_404(Agent, id=agent_id)
    action = request.POST.get('action')
    reason = request.POST.get('reason', '')
    
    if action == 'approve':
        agent.verification_status = 'verified'
        agent.verified_at = timezone.now()
        agent.verified_by = request.user
        messages.success(request, f'Agent {agent.company_name} has been verified successfully.')
        
        # Create notification
        from notifications.views import create_notification
        create_notification(
            user=agent.user,
            title='Agent Application Approved',
            message='Congratulations! Your agent application has been approved. You can now start receiving requirements and submitting quotes.',
            notification_type='success',
            sender=request.user
        )
        
    elif action == 'reject':
        agent.verification_status = 'rejected'
        agent.rejection_reason = reason
        agent.rejected_at = timezone.now()
        agent.rejected_by = request.user
        messages.success(request, f'Agent {agent.company_name} has been rejected.')
        
        # Create notification
        from notifications.views import create_notification
        create_notification(
            user=agent.user,
            title='Agent Application Rejected',
            message=f'Your agent application has been rejected. Reason: {reason}',
            notification_type='error',
            sender=request.user
        )
    
    agent.save()
    
    # Log activity
    AdminActivity.objects.create(
        admin_user=request.user,
        action='approve' if action == 'approve' else 'reject',
        object_type='agent',
        object_id=agent.id,
        object_repr=str(agent),
        description=f'{action.capitalize()}ed agent: {agent.company_name}'
    )
    
    return redirect('admin_panel:manage_agents')

@login_required
@user_passes_test(is_admin)
def commission_management(request):
    """Commission management view"""
    global_settings = GlobalSettings.get_settings()
    
    if request.method == 'POST':
        # Update commission settings
        global_settings.agent_commission_rate = request.POST.get('agent_commission_rate')
        global_settings.customer_commission_rate = request.POST.get('customer_commission_rate')
        global_settings.minimum_payout_threshold = request.POST.get('minimum_payout_threshold')
        global_settings.save()
        
        messages.success(request, 'Commission settings updated successfully.')
        
        # Log activity
        AdminActivity.objects.create(
            admin_user=request.user,
            action='update',
            object_type='setting',
            object_repr='Commission Settings',
            description='Updated commission rates and thresholds'
        )
    
    # Get commission statistics
    from django.db.models import Sum
    total_agent_commissions = Booking.objects.filter(
        status='completed'
    ).aggregate(total=Sum('agent_commission'))['total'] or 0
    
    total_platform_commissions = Booking.objects.filter(
        status='completed'
    ).aggregate(total=Sum('platform_commission'))['total'] or 0
    
    pending_payouts = Booking.objects.filter(
        status='confirmed'
    ).aggregate(total=Sum('agent_commission'))['total'] or 0
    
    context = {
        'global_settings': global_settings,
        'total_agent_commissions': total_agent_commissions,
        'total_platform_commissions': total_platform_commissions,
        'pending_payouts': pending_payouts,
    }
    
    return render(request, 'admin_panel/commission_management.html', context)

@login_required
@user_passes_test(is_admin)
def payout_management(request):
    """Payout management view"""
    status = request.GET.get('status', 'pending')
    
    # Get payouts (would need Payout model)
    # For now, simulate with booking data
    confirmed_bookings = Booking.objects.filter(status='confirmed')
    
    context = {
        'payouts': [],  # Would be from Payout model
        'confirmed_bookings': confirmed_bookings,
        'total_pending': confirmed_bookings.aggregate(
            total=Sum('agent_commission')
        )['total'] or 0,
        'status': status,
    }
    
    return render(request, 'admin_panel/payout_management.html', context)

@login_required
@user_passes_test(is_admin)
def dispute_management(request):
    """Dispute management view"""
    status = request.GET.get('status', 'all')
    
    bookings = Booking.objects.filter(
        dispute_status__isnull=False
    ).select_related('quote__agent', 'quote__requirement__user')
    
    if status != 'all':
        bookings = bookings.filter(dispute_status=status)
    
    context = {
        'bookings': bookings,
        'status': status,
    }
    
    return render(request, 'admin_panel/dispute_management.html', context)

@login_required
@user_passes_test(is_admin)
def analytics(request):
    """Analytics view"""
    period = request.GET.get('period', '30')
    
    try:
        days = int(period)
    except ValueError:
        days = 30
    
    start_date = timezone.now() - timedelta(days=days)
    
    # Get analytics data
    daily_stats = []
    for i in range(days):
        date = (timezone.now() - timedelta(days=i)).date()
        stats = DashboardStats.objects.filter(
            date=date,
            period='daily'
        ).first()
        
        if stats:
            daily_stats.append({
                'date': date,
                'users': stats.new_users,
                'bookings': stats.new_bookings,
                'revenue': float(stats.booking_revenue),
            })
        else:
            # Calculate from actual data if stats not available
            daily_stats.append({
                'date': date,
                'users': User.objects.filter(
                    user_type='customer',
                    date_joined__date=date
                ).count(),
                'bookings': Booking.objects.filter(
                    created_at__date=date
                ).count(),
                'revenue': float(Booking.objects.filter(
                    created_at__date=date,
                    status='completed'
                ).aggregate(total=Sum('total_amount'))['total'] or 0),
            })
    
    context = {
        'period': days,
        'daily_stats': daily_stats[::-1],  # Reverse to show oldest first
        'total_stats': {
            'users': User.objects.filter(
                user_type='customer',
                date_joined__gte=start_date
            ).count(),
            'bookings': Booking.objects.filter(
                created_at__gte=start_date
            ).count(),
            'revenue': Booking.objects.filter(
                created_at__gte=start_date,
                status='completed'
            ).aggregate(total=Sum('total_amount'))['total'] or 0,
        }
    }
    
    return render(request, 'admin_panel/analytics.html', context)

@login_required
@user_passes_test(is_admin)
def system_settings(request):
    """System settings view"""
    global_settings = GlobalSettings.get_settings()
    
    if request.method == 'POST':
        # Update global settings
        global_settings.platform_fee_description = request.POST.get('platform_fee_description')
        global_settings.support_email = request.POST.get('support_email')
        global_settings.support_phone = request.POST.get('support_phone')
        global_settings.payment_timeout_minutes = request.POST.get('payment_timeout_minutes')
        global_settings.refund_policy_days = request.POST.get('refund_policy_days')
        global_settings.quote_validity_days = request.POST.get('quote_validity_days')
        global_settings.auto_confirm_bookings = 'auto_confirm_bookings' in request.POST
        global_settings.enable_ai_assistant = 'enable_ai_assistant' in request.POST
        global_settings.enable_reviews = 'enable_reviews' in request.POST
        global_settings.enable_messaging = 'enable_messaging' in request.POST
        global_settings.enable_notifications = 'enable_notifications' in request.POST
        global_settings.save()
        
        messages.success(request, 'System settings updated successfully.')
        
        # Log activity
        AdminActivity.objects.create(
            admin_user=request.user,
            action='update',
            object_type='setting',
            object_repr='System Settings',
            description='Updated global system settings'
        )
    
    context = {
        'global_settings': global_settings,
    }
    
    return render(request, 'admin_panel/system_settings.html', context)

@login_required
@user_passes_test(is_admin)
def data_export(request):
    """Data export view"""
    if request.method == 'POST':
        export_type = request.POST.get('export_type')
        date_from = request.POST.get('date_from')
        date_to = request.POST.get('date_to')
        format_type = request.POST.get('format', 'csv')
        
        # Create export record
        export_record = DataExport.objects.create(
            export_type=export_type,
            date_from=datetime.strptime(date_from, '%Y-%m-%d').date() if date_from else None,
            date_to=datetime.strptime(date_to, '%Y-%m-%d').date() if date_to else None,
            format=format_type,
            requested_by=request.user,
            status='processing'
        )
        
        # Log activity
        AdminActivity.objects.create(
            admin_user=request.user,
            action='export',
            object_type='data',
            object_repr=f'{export_type.upper()} Export',
            description=f'Exported {export_type} data from {date_from} to {date_to}'
        )
        
        messages.success(request, f'Export request for {export_type} has been queued for processing.')
        return redirect('admin_panel:data_export')
    
    context = {
        'exports': DataExport.objects.filter(
            requested_by=request.user
        ).order_by('-created_at'),
    }
    
    return render(request, 'admin_panel/data_export.html', context)
