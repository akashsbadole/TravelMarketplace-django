from django.db import models
from django.conf import settings

class Agent(models.Model):
    VERIFICATION_STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('verified', 'Verified'),
        ('rejected', 'Rejected'),
        ('suspended', 'Suspended'),
    ]
    
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='agent')
    
    # Company Information
    company_name = models.CharField(max_length=200)
    company_registration_number = models.CharField(max_length=100, blank=True, null=True)
    gst_number = models.CharField(max_length=50, blank=True, null=True)
    pan_number = models.CharField(max_length=20, blank=True, null=True)
    
    # Business Details
    business_address = models.TextField()
    business_city = models.CharField(max_length=100)
    business_state = models.CharField(max_length=100)
    business_country = models.CharField(max_length=100)
    business_postal_code = models.CharField(max_length=20)
    business_phone = models.CharField(max_length=20)
    business_email = models.EmailField()
    
    # Agent Details
    contact_person_name = models.CharField(max_length=100)
    contact_person_designation = models.CharField(max_length=100)
    years_in_business = models.PositiveIntegerField(default=0)
    license_number = models.CharField(max_length=100, blank=True, null=True)
    
    # Specializations
    specializations = models.ManyToManyField('requirements.ServiceType', related_name='specialized_agents')
    destinations_served = models.TextField(help_text="Comma-separated list of destinations")
    
    # Verification
    verification_status = models.CharField(max_length=20, choices=VERIFICATION_STATUS_CHOICES, default='pending')
    verification_date = models.DateTimeField(null=True, blank=True)
    verification_notes = models.TextField(blank=True, null=True)
    
    # Documents
    gst_certificate = models.FileField(upload_to='agent_docs/gst/', blank=True, null=True)
    pan_card = models.FileField(upload_to='agent_docs/pan/', blank=True, null=True)
    trade_license = models.FileField(upload_to='agent_docs/license/', blank=True, null=True)
    company_logo = models.ImageField(upload_to='agent_logos/', blank=True, null=True)
    
    # Commission and Earnings
    commission_rate = models.DecimalField(max_digits=5, decimal_places=4, default=0.02, help_text="Decimal representation (e.g., 0.02 for 2%)")
    total_earnings = models.DecimalField(max_digits=12, decimal_places=2, default=0.00)
    pending_payout = models.DecimalField(max_digits=12, decimal_places=2, default=0.00)
    paid_out = models.DecimalField(max_digits=12, decimal_places=2, default=0.00)
    minimum_payout_threshold = models.DecimalField(max_digits=12, decimal_places=2, default=1000.00)
    
    # Bank Details for Payouts
    bank_account_number = models.CharField(max_length=50, blank=True, null=True)
    bank_name = models.CharField(max_length=200, blank=True, null=True)
    bank_branch = models.CharField(max_length=200, blank=True, null=True)
    bank_ifsc_code = models.CharField(max_length=20, blank=True, null=True)
    bank_account_holder_name = models.CharField(max_length=200, blank=True, null=True)
    
    # Performance Metrics
    total_bookings = models.PositiveIntegerField(default=0)
    active_bookings = models.PositiveIntegerField(default=0)
    completed_bookings = models.PositiveIntegerField(default=0)
    cancelled_bookings = models.PositiveIntegerField(default=0)
    average_rating = models.DecimalField(max_digits=3, decimal_places=2, default=0.00)
    total_reviews = models.PositiveIntegerField(default=0)
    
    # Status
    is_active = models.BooleanField(default=True)
    is_featured = models.BooleanField(default=False)
    featured_until = models.DateTimeField(null=True, blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.company_name} - {self.user.email}"
    
    def calculate_total_rating(self):
        """Calculate average rating from reviews"""
        reviews = self.reviews.all()
        if reviews.exists():
            total = sum(review.rating for review in reviews)
            self.average_rating = total / reviews.count()
            self.total_reviews = reviews.count()
            self.save()
        return self.average_rating

class AgentVerification(models.Model):
    agent = models.OneToOneField(Agent, on_delete=models.CASCADE, related_name='verification')
    reviewed_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True)
    review_date = models.DateTimeField(null=True, blank=True)
    admin_notes = models.TextField(blank=True, null=True)
    rejection_reason = models.TextField(blank=True, null=True)
    is_approved = models.BooleanField(null=True)  # True for approved, False for rejected, None for pending
    approved_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"Verification for {self.agent.company_name}"
