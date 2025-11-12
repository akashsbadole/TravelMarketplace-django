from django.shortcuts import render, redirect
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import HttpResponse
from .models import User, UserProfile
from .forms import UserRegistrationForm, UserLoginForm

def register(request):
    """User registration view"""
    if request.method == 'POST':
        form = UserRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()
            # Create user profile
            UserProfile.objects.create(user=user)
            messages.success(request, 'Registration successful! Please log in.')
            return redirect('users:login')
    else:
        form = UserRegistrationForm()
    
    return render(request, 'users/register.html', {'form': form})

def login_view(request):
    """User login view"""
    if request.method == 'POST':
        form = UserLoginForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']
            user = authenticate(request, username=username, password=password)
            if user is not None:
                login(request, user)
                if user.user_type == 'customer':
                    return redirect('users:dashboard')
                elif user.user_type == 'agent':
                    return redirect('agents:dashboard')
                else:
                    return redirect('admin_panel:dashboard')
            else:
                messages.error(request, 'Invalid username or password.')
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        form = UserLoginForm()
    
    return render(request, 'users/login.html', {'form': form})

def logout_view(request):
    """User logout view"""
    logout(request)
    messages.success(request, 'You have been logged out successfully.')
    return redirect('pages:home')

@login_required
def dashboard(request):
    """User dashboard view"""
    context = {
        'user': request.user,
        'active_bookings': 0,  # Mock data
        'total_bookings': 0,
        'active_requirements': 0,
        'total_requirements': 0,
        'unread_notifications': 3,
    }
    
    if request.user.user_type == 'customer':
        return render(request, 'users/customer_dashboard.html', context)
    else:
        return redirect('agents:dashboard')

@login_required
def profile(request):
    """User profile view"""
    profile, created = UserProfile.objects.get_or_create(user=request.user)
    
    if request.method == 'POST':
        # Handle profile update
        pass
    
    return render(request, 'users/profile.html', {'profile': profile})

@login_required
def settings(request):
    """User settings view"""
    return render(request, 'users/settings.html')
