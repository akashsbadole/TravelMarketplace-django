from django.db import models
from django.conf import settings

class ServiceType(models.Model):
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True, null=True)
    icon = models.CharField(max_length=50, blank=True, null=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['name']
    
    def __str__(self):
        return self.name

class TravelRequirement(models.Model):
    STATUS_CHOICES = [
        ('draft', 'Draft'),
        ('open', 'Open'),
        ('closed', 'Closed'),
        ('expired', 'Expired'),
    ]
    
    PRIORITY_CHOICES = [
        ('low', 'Low'),
        ('medium', 'Medium'),
        ('high', 'High'),
        ('urgent', 'Urgent'),
    ]
    
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='requirements')
    service_type = models.ForeignKey(ServiceType, on_delete=models.CASCADE, related_name='requirements')
    
    # Basic Information
    title = models.CharField(max_length=200)
    description = models.TextField()
    budget_min = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    budget_max = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    currency = models.CharField(max_length=3, default='USD')
    
    # Travel Dates
    travel_date_start = models.DateField()
    travel_date_end = models.DateField()
    is_flexible_dates = models.BooleanField(default=False)
    flexibility_days = models.PositiveIntegerField(default=0)
    
    # Travelers Information
    number_of_adults = models.PositiveIntegerField(default=1)
    number_of_children = models.PositiveIntegerField(default=0)
    number_of_infants = models.PositiveIntegerField(default=0)
    traveler_ages = models.TextField(blank=True, null=True, help_text="Ages of children and infants")
    
    # Origin and Destination
    origin = models.CharField(max_length=200, help_text="City or airport code")
    destination = models.CharField(max_length=200, help_text="City or airport code")
    is_one_way = models.BooleanField(default=False)
    is_multi_city = models.BooleanField(default=False)
    multi_cities = models.TextField(blank=True, null=True, help_text="For multi-city trips")
    
    # Flight Specific Details (if applicable)
    preferred_airline = models.CharField(max_length=100, blank=True, null=True)
    preferred_class = models.CharField(
        max_length=20,
        choices=[
            ('economy', 'Economy'),
            ('business', 'Business'),
            ('first', 'First'),
            ('premium_economy', 'Premium Economy'),
        ],
        default='economy',
        blank=True,
        null=True
    )
    preferred_departure_time = models.TimeField(null=True, blank=True)
    preferred_arrival_time = models.TimeField(null=True, blank=True)
    
    # Hotel Specific Details (if applicable)
    hotel_star_rating_min = models.PositiveIntegerField(null=True, blank=True)
    hotel_star_rating_max = models.PositiveIntegerField(null=True, blank=True)
    preferred_room_type = models.CharField(
        max_length=50,
        choices=[
            ('standard', 'Standard'),
            ('deluxe', 'Deluxe'),
            ('suite', 'Suite'),
            ('family', 'Family Room'),
        ],
        default='standard',
        blank=True,
        null=True
    )
    meal_plan = models.CharField(
        max_length=20,
        choices=[
            ('room_only', 'Room Only'),
            ('breakfast', 'Breakfast Included'),
            ('half_board', 'Half Board'),
            ('full_board', 'Full Board'),
            ('all_inclusive', 'All Inclusive'),
        ],
        blank=True,
        null=True
    )
    
    # Additional Requirements
    additional_requirements = models.TextField(blank=True, null=True)
    special_needs = models.TextField(blank=True, null=True)
    
    # Status and Priority
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='open')
    priority = models.CharField(max_length=20, choices=PRIORITY_CHOICES, default='medium')
    
    # Deadlines
    quote_submission_deadline = models.DateTimeField(null=True, blank=True)
    booking_deadline = models.DateTimeField(null=True, blank=True)
    
    # Metadata
    is_public = models.BooleanField(default=True)
    views_count = models.PositiveIntegerField(default=0)
    quotes_count = models.PositiveIntegerField(default=0)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.title} - {self.user.email}"
    
    def increment_views(self):
        """Increment the views count"""
        self.views_count += 1
        self.save(update_fields=['views_count'])
    
    def increment_quotes(self):
        """Increment the quotes count"""
        self.quotes_count += 1
        self.save(update_fields=['quotes_count'])

class RequirementAttachment(models.Model):
    requirement = models.ForeignKey(TravelRequirement, on_delete=models.CASCADE, related_name='attachments')
    file = models.FileField(upload_to='requirement_attachments/')
    filename = models.CharField(max_length=255)
    file_size = models.PositiveIntegerField()
    file_type = models.CharField(max_length=50)
    description = models.CharField(max_length=255, blank=True, null=True)
    uploaded_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.requirement.title} - {self.filename}"

class RequirementResponse(models.Model):
    requirement = models.ForeignKey(TravelRequirement, on_delete=models.CASCADE, related_name='responses')
    agent = models.ForeignKey('agents.Agent', on_delete=models.CASCADE, related_name='requirement_responses')
    is_interested = models.BooleanField(default=True)
    notes = models.TextField(blank=True, null=True, help_text="Agent notes about this requirement")
    estimated_price = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    estimated_duration = models.CharField(max_length=100, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        unique_together = ['requirement', 'agent']
    
    def __str__(self):
        return f"{self.agent.company_name} - {self.requirement.title}"
