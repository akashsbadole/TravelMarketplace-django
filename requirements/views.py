from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import HttpResponse, JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.utils import timezone
from datetime import timedelta
from .models import TravelRequirement, ServiceType
from django.db.models import Q

def create(request):
    """Create travel requirement view"""
    if request.method == 'POST':
        try:
            # Get service type
            service_type_name = request.POST.get('service_type')
            if not service_type_name:
                messages.error(request, "Please select a service type.")
                service_types = ServiceType.objects.filter(is_active=True)
                return render(request, 'requirements/create.html', {
                    'service_types': service_types,
                    'user': request.user if request.user.is_authenticated else None,
                })
            
            # Get or create service type
            service_type, created = ServiceType.objects.get_or_create(
                name=service_type_name.title(),
                defaults={'is_active': True}
            )
            
            # Create requirement
            requirement = TravelRequirement.objects.create(
                user=request.user,
                service_type=service_type,
                title=f"{service_type_name.title()} to {request.POST.get('destination', 'Unknown')}",
                description=request.POST.get('description', ''),
                budget_min=request.POST.get('budget'),
                budget_max=request.POST.get('budget'),
                travel_date_start=timezone.now().date() + timedelta(days=30),
                travel_date_end=timezone.now().date() + timedelta(days=37),
                origin=request.POST.get('origin', ''),
                destination=request.POST.get('destination', ''),
                number_of_adults=int(request.POST.get('passengers', 1)),
                is_flexible_dates=request.POST.get('flexible') == 'true',
                status='open'
            )
            
            # Add service-specific details
            if service_type_name == 'flight':
                requirement.preferred_class = request.POST.get('class', 'economy')
                requirement.save()
            elif service_type_name == 'hotel':
                requirement.preferred_room_type = request.POST.get('room_type', 'standard')
                requirement.save()
            elif service_type_name == 'train':
                requirement.preferred_class = request.POST.get('class', 'sleeper')
                requirement.save()
            
            messages.success(request, "Your travel requirement has been posted successfully! Agents will contact you soon with quotes.")
            return redirect('dashboard:requirements')
            
        except Exception as e:
            messages.error(request, f"An error occurred: {str(e)}")
    
    # Get service types for form
    service_types = ServiceType.objects.filter(is_active=True)
    
    return render(request, 'requirements/create.html', {
        'service_types': service_types,
        'user': request.user if request.user.is_authenticated else None,
    })

@login_required
def detail(request, requirement_id):
    """View requirement detail view"""
    requirement = get_object_or_404(TravelRequirement, id=requirement_id)
    
    if requirement.user != request.user:
        return HttpResponse("Permission denied", status=403)
    
    context = {
        'requirement': requirement,
        'user': request.user,
    }
    
    return render(request, 'requirements/detail.html', context)

@login_required
def my_requirements(request):
    """User's requirements list view"""
    requirements = TravelRequirement.objects.filter(user=request.user).order_by('-created_at')
    
    context = {
        'requirements': requirements,
        'user': request.user,
    }
    
    return render(request, 'requirements/my_requirements.html', context)