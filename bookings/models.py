from django.db import models
from django.conf import settings
from django.core.validators import MinValueValidator
from decimal import Decimal

class Booking(models.Model):
    """Travel Booking model"""
    STATUS_CHOICES = [
        ('pending', 'Pending Payment'),
        ('paid', 'Paid'),
        ('confirmed', 'Confirmed'),
        ('cancelled', 'Cancelled'),
        ('completed', 'Completed'),
    ]
    
    DISPUTE_STATUS_CHOICES = [
        ('none', 'None'),
        ('raised', 'Raised'),
        ('in-review', 'In Review'),
        ('resolved', 'Resolved'),
    ]
    
    quote = models.ForeignKey('quotes.Quote', on_delete=models.CASCADE)
    customer = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='bookings')
    total_amount = models.DecimalField(max_digits=10, decimal_places=2, validators=[MinValueValidator(Decimal('0.00'))])
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    
    # Commission fields
    agent_commission = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal('0.00'))
    customer_commission = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal('0.00'))
    platform_commission = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal('0.00'))
    agent_payout = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal('0.00'))
    
    # Dispute fields
    dispute_status = models.CharField(max_length=20, choices=DISPUTE_STATUS_CHOICES, default='none')
    dispute_reason = models.TextField(blank=True, null=True)
    dispute_resolution = models.TextField(blank=True, null=True)
    
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'bookings'
        ordering = ['-created_at']
    
    def __str__(self):
        return f"Booking #{self.id} - {self.quote.requirement.title}"
    
    def calculate_commission(self):
        """Calculate commission amounts based on global settings"""
        from admin_panel.models import GlobalSettings
        
        try:
            settings = GlobalSettings.objects.first()
            agent_commission_rate = settings.agent_commission_rate if settings else Decimal('0.02')
            customer_commission_rate = settings.customer_commission_rate if settings else Decimal('0.01')
        except:
            agent_commission_rate = Decimal('0.02')
            customer_commission_rate = Decimal('0.01')
        
        self.agent_commission = self.total_amount * agent_commission_rate
        self.customer_commission = self.total_amount * customer_commission_rate
        self.platform_commission = self.agent_commission + self.customer_commission
        self.agent_payout = self.total_amount - self.agent_commission
        
        self.save(update_fields=['agent_commission', 'customer_commission', 'platform_commission', 'agent_payout'])
        
        # Update agent earnings
        if hasattr(self.quote, 'agent') and self.quote.agent:
            agent = self.quote.agent
            agent.total_earnings += self.agent_payout
            agent.pending_payout += self.agent_payout
            agent.save()
    
    def save(self, *args, **kwargs):
        """Override save to calculate commission on first save"""
        is_new = self.pk is None
        super().save(*args, **kwargs)
        
        if is_new:
            self.calculate_commission()
    
    def confirm_booking(self):
        """Confirm booking and update statuses"""
        self.status = 'confirmed'
        self.save()
        
        # Update quote status
        self.quote.status = 'booked'
        self.quote.save()
        
        # Create notification for agent
        from notifications.models import Notification
        Notification.objects.create(
            user=self.quote.agent.user,
            title='New Booking Confirmed',
            message=f'Your quote for {self.quote.requirement.title} has been booked!',
            notification_type='booking',
            related_object_id=self.id,
            related_object_type='booking'
        )

class BookingPayment(models.Model):
    """Payment for booking model"""
    PAYMENT_STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('completed', 'Completed'),
        ('failed', 'Failed'),
        ('refunded', 'Refunded'),
    ]
    
    booking = models.ForeignKey(Booking, on_delete=models.CASCADE, related_name='payments')
    payment_method = models.CharField(max_length=50)  # PayPal, Stripe, etc.
    transaction_id = models.CharField(max_length=100, blank=True)
    amount = models.DecimalField(max_digits=10, decimal_places=2, validators=[MinValueValidator(Decimal('0.00'))])
    status = models.CharField(max_length=20, choices=PAYMENT_STATUS_CHOICES, default='pending')
    payment_date = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'booking_payments'
        ordering = ['-created_at']
    
    def __str__(self):
        return f"Payment #{self.id} - {self.booking.id}"

class BookingDetail(models.Model):
    """Details of booking items"""
    booking = models.ForeignKey(Booking, on_delete=models.CASCADE, related_name='details')
    quote_item = models.ForeignKey('quotes.QuoteItem', on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField()
    price_per_unit = models.DecimalField(max_digits=10, decimal_places=2)
    subtotal = models.DecimalField(max_digits=10, decimal_places=2)
    
    class Meta:
        db_table = 'booking_details'
        ordering = ['id']
    
    def __str__(self):
        return f"{self.quote_item.description} - {self.booking.id}"
