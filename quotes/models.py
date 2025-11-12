from django.db import models
from django.conf import settings
from django.core.validators import MinValueValidator
from decimal import Decimal

class Quote(models.Model):
    """Travel Quote model"""
    STATUS_CHOICES = [
        ('draft', 'Draft'),
        ('submitted', 'Submitted'),
        ('accepted', 'Accepted'),
        ('rejected', 'Rejected'),
        ('expired', 'Expired'),
        ('booked', 'Booked'),
    ]
    
    requirement = models.ForeignKey('requirements.TravelRequirement', on_delete=models.CASCADE)
    agent = models.ForeignKey('agents.Agent', on_delete=models.CASCADE, related_name='quotes')
    customer = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='received_quotes')
    total_amount = models.DecimalField(max_digits=10, decimal_places=2, validators=[MinValueValidator(Decimal('0.00'))])
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='draft')
    valid_until = models.DateTimeField()
    notes = models.TextField(blank=True)
    
    # Itinerary and details
    itinerary = models.TextField(blank=True, help_text="Detailed itinerary in rich text format")
    inclusions = models.TextField(blank=True, help_text="What's included in this quote")
    exclusions = models.TextField(blank=True, help_text="What's excluded from this quote")
    terms_and_conditions = models.TextField(blank=True, help_text="Terms and conditions for this quote")
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'quotes'
        ordering = ['-created_at']
    
    def __str__(self):
        return f"Quote #{self.id} - {self.requirement.title}"
    
    def accept_quote(self):
        """Accept the quote and update related objects"""
        self.status = 'accepted'
        self.save()
        
        # Create notification for agent
        from notifications.models import Notification
        Notification.objects.create(
            user=self.agent.user,
            title='Quote Accepted',
            message=f'Your quote for {self.requirement.title} has been accepted!',
            notification_type='quote',
            related_object_id=self.id,
            related_object_type='quote'
        )
        
        # Reject other quotes for this requirement
        other_quotes = Quote.objects.filter(
            requirement=self.requirement
        ).exclude(id=self.id)
        
        for quote in other_quotes:
            quote.status = 'rejected'
            quote.save()
            
            Notification.objects.create(
                user=quote.agent.user,
                title='Quote Rejected',
                message=f'Your quote for {quote.requirement.title} has been rejected (another quote was accepted).',
                notification_type='quote',
                related_object_id=quote.id,
                related_object_type='quote'
            )
    
    def reject_quote(self):
        """Reject the quote"""
        self.status = 'rejected'
        self.save()
        
        # Create notification for agent
        from notifications.models import Notification
        Notification.objects.create(
            user=self.agent.user,
            title='Quote Rejected',
            message=f'Your quote for {self.requirement.title} has been rejected.',
            notification_type='quote',
            related_object_id=self.id,
            related_object_type='quote'
        )
    
    def is_expired(self):
        """Check if quote is expired"""
        from django.utils import timezone
        return timezone.now() > self.valid_until
    
    def calculate_total(self):
        """Calculate total from quote items"""
        total = self.items.aggregate(total=models.Sum('subtotal'))['total'] or 0
        self.total_amount = total
        self.save()
        return total

class QuoteItem(models.Model):
    """Individual items within a quote"""
    quote = models.ForeignKey(Quote, on_delete=models.CASCADE, related_name='items')
    service_type = models.ForeignKey('requirements.ServiceType', on_delete=models.CASCADE)
    description = models.CharField(max_length=500)
    quantity = models.PositiveIntegerField(default=1)
    unit_price = models.DecimalField(max_digits=10, decimal_places=2, validators=[MinValueValidator(Decimal('0.00'))])
    subtotal = models.DecimalField(max_digits=10, decimal_places=2, validators=[MinValueValidator(Decimal('0.00'))])
    agent = models.ForeignKey('agents.Agent', on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'quote_items'
        ordering = ['id']
    
    def __str__(self):
        return f"{self.service_type.name} - {self.description}"
    
    def save(self, *args, **kwargs):
        self.subtotal = self.unit_price * self.quantity
        super().save(*args, **kwargs)
