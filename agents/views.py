from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth import login, authenticate
from django.contrib import messages
from django.contrib.auth.models import User
from django.http import HttpResponse, JsonResponse
from django.views.decorators.http import require_POST
from django.utils import timezone
from django.db.models import Sum, Count, Q
from .models import Agent
from requirements.models import TravelRequirement
from quotes.models import Quote
from bookings.models import Booking
from django.shortcuts import get_object_or_404

def register(request):
    """Agent registration view"""
    if request.method == 'POST':
        try:
            # Get user data
            username = request.POST.get('username')
            email = request.POST.get('email')
            password = request.POST.get('password')
            confirm_password = request.POST.get('confirm_password')
            
            # Validate passwords match
            if password != confirm_password:
                messages.error(request, 'Passwords do not match')
                return render(request, 'agents/register.html')
            
            # Check if username or email already exists
            if User.objects.filter(username=username).exists():
                messages.error(request, 'Username already exists')
                return render(request, 'agents/register.html')
            
            if User.objects.filter(email=email).exists():
                messages.error(request, 'Email already exists')
                return render(request, 'agents/register.html')
            
            # Create user
            user = User.objects.create_user(
                username=username,
                email=email,
                password=password,
                first_name=request.POST.get('contact_person', ''),
                user_type='agent'
            )
            
            # Create agent profile
            agent = Agent.objects.create(
                user=user,
                company_name=request.POST.get('company_name'),
                company_type=request.POST.get('company_type'),
                registration_number=request.POST.get('registration_number'),
                established_year=request.POST.get('established_year'),
                contact_person=request.POST.get('contact_person'),
                contact_email=request.POST.get('contact_email'),
                contact_phone=request.POST.get('contact_phone'),
                website=request.POST.get('website', ''),
                company_description=request.POST.get('company_description'),
                address_line1=request.POST.get('address_line1'),
                address_line2=request.POST.get('address_line2', ''),
                city=request.POST.get('city'),
                state=request.POST.get('state'),
                postal_code=request.POST.get('postal_code'),
                country=request.POST.get('country'),
                verification_status='pending'
            )
            
            # Handle specializations
            specializations = request.POST.getlist('specializations')
            # Note: This would require a Specialization model to be properly implemented
            
            # Handle document uploads
            if 'gst_certificate' in request.FILES:
                agent.gst_certificate = request.FILES['gst_certificate']
            if 'pan_card' in request.FILES:
                agent.pan_card = request.FILES['pan_card']
            if 'trade_license' in request.FILES:
                agent.trade_license = request.FILES['trade_license']
            if 'iata_certificate' in request.FILES:
                agent.iata_certificate = request.FILES['iata_certificate']
            
            agent.save()
            
            # Log the user in
            user = authenticate(username=username, password=password)
            if user:
                login(request, user)
                messages.success(request, 'Registration successful! Your application is now under review.')
                return redirect('agents:verification_pending')
            
        except Exception as e:
            messages.error(request, f'An error occurred: {str(e)}')
    
    return render(request, 'agents/register.html', {'current_year': timezone.now().year})

def verification_pending(request):
    """Agent verification pending view"""
    try:
        agent = get_object_or_404(Agent, user=request.user)
        return render(request, 'agents/verification_pending.html', {'agent': agent})
    except:
        return redirect('agents:register')

def dashboard(request):
    """Agent dashboard view"""
    try:
        agent = get_object_or_404(Agent, user=request.user, user__user_type='agent')
        
        # Get real stats
        quotes = Quote.objects.filter(agent=agent)
        bookings = Booking.objects.filter(quote__agent=agent)
        
        # Calculate stats
        active_quotes = quotes.filter(status__in=['draft', 'submitted']).count()
        pending_bookings = bookings.filter(status='pending').count()
        total_bookings = bookings.count()
        total_revenue = bookings.filter(status='completed').aggregate(
            total=Sum('total_amount'))['total'] or 0
        
        # Calculate pending payout (2% commission on confirmed bookings)
        pending_payout = bookings.filter(status='confirmed').aggregate(
            total=Sum('agent_commission'))['total'] or 0
        
        # Get recent requirements
        recent_requirements = TravelRequirement.objects.filter(
            status='open'
        ).order_by('-created_at')[:5]
        
        # Get recent quotes
        recent_quotes = quotes.order_by('-created_at')[:5]
        
        context = {
            'agent': agent,
            'stats': {
                'active_quotes': active_quotes,
                'pending_bookings': pending_bookings,
                'total_bookings': total_bookings,
                'total_revenue': total_revenue,
                'pending_payout': pending_payout,
            },
            'recent_requirements': recent_requirements,
            'recent_quotes': recent_quotes,
        }
        
        return render(request, 'agents/dashboard.html', context)
        
    except Agent.DoesNotExist:
        return redirect('agents:register')
    except Exception as e:
        messages.error(request, f'An error occurred: {str(e)}')
        return redirect('agents:register')

@login_required
def profile(request):
    """Agent profile view"""
    agent = get_object_or_404(Agent, user=request.user, user__user_type='agent')
    
    if request.method == 'POST':
        # Handle profile update
        pass
    
    return render(request, 'agents/profile.html', {'agent': agent})

@login_required
def requirements(request):
    """Browse requirements view"""
    # Get all requirements with filters
    requirements_list = TravelRequirement.objects.filter(status='open').order_by('-created_at')[:20]
    
    context = {
        'requirements': requirements_list,
        'service_types': ['Flight', 'Hotel', 'Bus', 'Train', 'Package'],
        'destinations': ['Paris', 'Tokyo', 'New York', 'Bali'],
        'budget_ranges': [
            {'min': 0, 'max': 1000, 'label': 'Under $1,000'},
            {'min': 1000, 'max': 5000, 'label': '$1,000 - $5,000'},
            {'min': 5000, 'max': 10000, 'label': '$5,000 - $10,000'},
            {'min': 10000, 'max': 50000, 'label': 'Over $10,000'},
        ],
    }
    
    return render(request, 'agents/requirements.html', context)

@login_required
def quotes(request):
    """Manage quotes view"""
    agent = get_object_or_404(Agent, user=request.user, user__user_type='agent')
    
    # Get real quotes with filters
    status_filter = request.GET.get('status')
    quotes_list = Quote.objects.filter(agent=agent)
    
    if status_filter:
        quotes_list = quotes_list.filter(status=status_filter)
    
    quotes_list = quotes_list.order_by('-created_at')
    
    context = {
        'agent': agent,
        'quotes': quotes_list,
        'status_options': ['draft', 'submitted', 'accepted', 'rejected', 'expired'],
        'current_status': status_filter,
    }
    
    return render(request, 'agents/quotes.html', context)

@login_required
def create_quote(request, requirement_id):
    """Create quote view"""
    requirement = get_object_or_404(TravelRequirement, id=requirement_id)
    agent = get_object_or_404(Agent, user=request.user, user__user_type='agent')
    
    if request.method == 'POST':
        try:
            # Create quote
            quote = Quote.objects.create(
                requirement=requirement,
                agent=agent,
                title=request.POST.get('title'),
                description=request.POST.get('description'),
                price=request.POST.get('price'),
                inclusions=request.POST.get('inclusions'),
                exclusions=request.POST.get('exclusions'),
                terms=request.POST.get('terms'),
                validity_date=request.POST.get('validity_date'),
                status='draft'
            )
            
            messages.success(request, 'Quote created successfully!')
            return redirect('agents:quotes')
            
        except Exception as e:
            messages.error(request, f'Error creating quote: {str(e)}')
    
    context = {
        'requirement': requirement,
        'agent': agent,
    }
    
    return render(request, 'agents/create_quote.html', context)

@login_required
def bookings(request):
    """Manage bookings view"""
    agent = get_object_or_404(Agent, user=request.user, user__user_type='agent')
    
    # Get real bookings with filters
    status_filter = request.GET.get('status')
    bookings_list = Booking.objects.filter(quote__agent=agent)
    
    if status_filter:
        bookings_list = bookings_list.filter(status=status_filter)
    
    bookings_list = bookings_list.order_by('-created_at')
    
    context = {
        'agent': agent,
        'bookings': bookings_list,
        'status_options': ['pending', 'confirmed', 'paid', 'completed', 'cancelled'],
        'current_status': status_filter,
    }
    
    return render(request, 'agents/bookings.html', context)

@login_required
def earnings(request):
    """View earnings and payouts view"""
    agent = get_object_or_404(Agent, user=request.user, user__user_type='agent')
    
    # Calculate real stats
    bookings = Booking.objects.filter(quote__agent=agent)
    completed_bookings = bookings.filter(status='completed')
    confirmed_bookings = bookings.filter(status='confirmed')
    
    total_earnings = completed_bookings.aggregate(
        total=Sum('agent_commission'))['total'] or 0
    pending_payout = confirmed_bookings.aggregate(
        total=Sum('agent_commission'))['total'] or 0
    paid_out = total_earnings - pending_payout
    booking_count = completed_bookings.count()
    
    context = {
        'agent': agent,
        'stats': {
            'total_earnings': total_earnings,
            'pending_payout': pending_payout,
            'paid_out': paid_out,
            'commission_rate': agent.commission_rate or 2.0,
            'booking_count': booking_count,
        },
        'payout_history': [],  # Would implement Payout model
    }
    
    return render(request, 'agents/earnings.html', context)

@login_required
@require_POST
def request_payout(request):
    """Request payout view"""
    agent = get_object_or_404(Agent, user=request.user, user__user_type='agent')
    
    try:
        amount = float(request.POST.get('amount', 0))
        
        # Check minimum threshold
        if amount < agent.minimum_payout_threshold:
            messages.error(request, f'Minimum payout amount is ${agent.minimum_payout_threshold}')
            return redirect('agents:earnings')
        
        # Update bank details if provided
        if request.POST.get('bank_name'):
            agent.bank_name = request.POST.get('bank_name')
        if request.POST.get('bank_account_number'):
            agent.bank_account_number = request.POST.get('bank_account_number')
        if request.POST.get('bank_account_holder_name'):
            agent.bank_account_holder_name = request.POST.get('bank_account_holder_name')
        if request.POST.get('bank_ifsc_code'):
            agent.bank_ifsc_code = request.POST.get('bank_ifsc_code')
        
        agent.save()
        
        # Create payout request (would implement Payout model)
        messages.success(request, 'Payout request submitted successfully!')
        
    except Exception as e:
        messages.error(request, f'Error requesting payout: {str(e)}')
    
    return redirect('agents:earnings')

@login_required
def payout_history(request):
    """View payout history view"""
    agent = get_object_or_404(Agent, user=request.user, user__user_type='agent')
    
    # Would implement Payout model
    context = {
        'agent': agent,
        'payouts': [],  # Would get from Payout model
    }
    
    return render(request, 'agents/payout_history.html', context)

@login_required
def requirement_detail(request, requirement_id):
    """View requirement detail view"""
    requirement = get_object_or_404(TravelRequirement, id=requirement_id)
    agent = get_object_or_404(Agent, user=request.user, user__user_type='agent')
    
    # Check if agent has already quoted
    existing_quote = Quote.objects.filter(
        requirement=requirement,
        agent=agent
    ).first()
    
    context = {
        'requirement': requirement,
        'agent': agent,
        'existing_quote': existing_quote,
    }
    
    return render(request, 'agents/requirement_detail.html', context)

@login_required
def edit_quote(request, quote_id):
    """Edit quote view"""
    quote = get_object_or_404(Quote, id=quote_id, agent__user=request.user)
    
    if request.method == 'POST':
        try:
            quote.title = request.POST.get('title')
            quote.description = request.POST.get('description')
            quote.price = request.POST.get('price')
            quote.inclusions = request.POST.get('inclusions')
            quote.exclusions = request.POST.get('exclusions')
            quote.terms = request.POST.get('terms')
            quote.validity_date = request.POST.get('validity_date')
            
            quote.save()
            
            messages.success(request, 'Quote updated successfully!')
            return redirect('agents:quotes')
            
        except Exception as e:
            messages.error(request, f'Error updating quote: {str(e)}')
    
    context = {
        'quote': quote,
        'requirement': quote.requirement,
    }
    
    return render(request, 'agents/edit_quote.html', context)

@login_required
def booking_detail(request, booking_id):
    """View booking detail view"""
    booking = get_object_or_404(Booking, id=booking_id, quote__agent__user=request.user)
    
    context = {
        'booking': booking,
        'quote': booking.quote,
        'requirement': booking.quote.requirement,
    }
    
    return render(request, 'agents/booking_detail.html', context)

@login_required
@require_POST
def upload_documents(request, booking_id):
    """Upload documents for booking view"""
    booking = get_object_or_404(Booking, id=booking_id, quote__agent__user=request.user)
    
    try:
        if 'voucher' in request.FILES:
            booking.voucher = request.FILES['voucher']
        if 'ticket' in request.FILES:
            booking.ticket = request.FILES['ticket']
        
        booking.save()
        
        messages.success(request, 'Documents uploaded successfully!')
        
    except Exception as e:
        messages.error(request, f'Error uploading documents: {str(e)}')
    
    return redirect('agents:booking_detail', booking_id=booking_id)
