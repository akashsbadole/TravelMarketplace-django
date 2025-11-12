from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import HttpResponse
from django.db.models import Sum
from django.utils import timezone
from decimal import Decimal
import time
from .models import Booking, BookingPayment
from quotes.models import Quote
from django.urls import reverse

@login_required
def list(request):
    """List of bookings view"""
    if hasattr(request.user, 'agent'):
        bookings_list = Booking.objects.filter(quote__customer=request.user)
    else:
        bookings_list = Booking.objects.filter(customer=request.user)
    
    context = {
        'bookings': bookings_list,
        'user': request.user,
    }
    
    return render(request, 'bookings/list.html', context)

@login_required
def create(request, quote_id):
    """Create booking from quote view"""
    quote = get_object_or_404(Quote, id=quote_id)
    
    if hasattr(request.user, 'agent'):
        messages.error(request, "Customers can create bookings, not agents.")
        return redirect('quotes:detail', quote_id=quote_id)
    
    if quote.status != 'accepted':
        messages.error(request, "You can only create bookings from accepted quotes.")
        return redirect('quotes:detail', quote_id=quote_id)
    
    if request.method == 'POST':
        # Get traveler details from form
        first_name = request.POST.get('first_name')
        last_name = request.POST.get('last_name')
        email = request.POST.get('email')
        phone = request.POST.get('phone')
        
        # Basic validation
        if not all([first_name, last_name, email, phone]):
            messages.error(request, "Please fill in all traveler details.")
            return render(request, 'bookings/create.html', {'quote': quote})
        
        # Create booking from quote
        booking = Booking.objects.create(
            quote=quote,
            customer=request.user,
            total_amount=quote.total_amount,
            status='pending',
            notes=f"Primary traveler: {first_name} {last_name}, Email: {email}, Phone: {phone}"
        )
        
        # Create booking details from quote items
        for item in quote.items.all():
            BookingDetail.objects.create(
                booking=booking,
                quote_item=item,
                quantity=item.quantity,
                price_per_unit=item.price_per_unit,
                subtotal=item.subtotal
            )
        
        # Update quote status
        quote.status = 'booked'
        quote.save()
        
        # Create notification for agent
        from notifications.models import Notification
        Notification.objects.create(
            user=quote.agent.user,
            title='New Booking Created',
            message=f'A new booking has been created from your quote for {quote.requirement.title}',
            notification_type='booking',
            related_object_id=booking.id,
            related_object_type='booking'
        )
        
        messages.success(request, "Booking created successfully! Please complete the payment to confirm.")
        return redirect('bookings:payment', booking_id=booking.id)
    
    context = {
        'quote': quote,
        'user': request.user,
    }
    
    return render(request, 'bookings/create.html', context)

@login_required
def detail(request, booking_id):
    """Booking detail view"""
    booking = get_object_or_404(Booking, id=booking_id)
    
    # Check permissions
    if (hasattr(request.user, 'agent') and booking.quote.customer.user != request.user) or \
       (not hasattr(request.user, 'agent') and booking.customer != request.user):
        return HttpResponse("Permission denied", status=403)
    
    context = {
        'booking': booking,
        'user': request.user,
    }
    
    return render(request, 'bookings/detail.html', context)

@login_required
def payment(request, booking_id):
    """Payment view for booking"""
    booking = get_object_or_404(Booking, id=booking_id)
    
    # Check permissions
    if booking.customer != request.user:
        return HttpResponse("Permission denied", status=403)
    
    if booking.status != 'pending':
        messages.error(request, "This booking cannot be paid for.")
        return redirect('bookings:detail', booking_id=booking_id)
    
    # Handle PayPal payment processing
    if request.method == 'POST':
        payment_method = request.POST.get('payment_method')
        
        if payment_method == 'paypal':
            # Create PayPal payment
            # In a real implementation, you would use PayPal SDK here
            # For now, we'll simulate the payment process
            
            # Create payment record
            payment = BookingPayment.objects.create(
                booking=booking,
                payment_method='PayPal',
                transaction_id=f"PAYPAL-{booking.id}-{int(time.time())}",
                amount=booking.total_amount,
                status='completed',
                payment_date=timezone.now()
            )
            
            # Update booking status
            booking.status = 'paid'
            booking.save()
            
            # Confirm booking
            booking.confirm_booking()
            
            # Create notification for customer
            from notifications.models import Notification
            Notification.objects.create(
                user=request.user,
                title='Payment Successful',
                message=f'Your payment of ₹{booking.total_amount} for booking #{booking.id} has been processed successfully.',
                notification_type='payment',
                related_object_id=booking.id,
                related_object_type='booking'
            )
            
            messages.success(request, "Payment processed successfully!")
            return redirect('bookings:confirmation', booking_id=booking.id)
        
        elif payment_method == 'card':
            # Process card payment
            # In a real implementation, you would integrate with a payment gateway like Stripe
            # For now, we'll simulate the payment process
            
            # Create payment record
            payment = BookingPayment.objects.create(
                booking=booking,
                payment_method='Credit/Debit Card',
                transaction_id=f"CARD-{booking.id}-{int(time.time())}",
                amount=booking.total_amount,
                status='completed',
                payment_date=timezone.now()
            )
            
            # Update booking status
            booking.status = 'paid'
            booking.save()
            
            # Confirm booking
            booking.confirm_booking()
            
            # Create notification for customer
            from notifications.models import Notification
            Notification.objects.create(
                user=request.user,
                title='Payment Successful',
                message=f'Your payment of ₹{booking.total_amount} for booking #{booking.id} has been processed successfully.',
                notification_type='payment',
                related_object_id=booking.id,
                related_object_type='booking'
            )
            
            messages.success(request, "Payment processed successfully!")
            return redirect('bookings:confirmation', booking_id=booking.id)
    
    context = {
        'booking': booking,
        'user': request.user,
    }
    
    return render(request, 'bookings/payment.html', context)

@login_required
def confirmation(request, booking_id):
    """Payment confirmation view"""
    booking = get_object_or_404(Booking, id=booking_id)
    
    # Check permissions
    if booking.customer != request.user:
        return HttpResponse("Permission denied", status=403)
    
    context = {
        'booking': booking,
        'user': request.user,
    }
    
    return render(request, 'bookings/confirmation.html', context)