from django.db import models
from django.conf import settings

class AIConversation(models.Model):
    STATUS_CHOICES = [
        ('active', 'Active'),
        ('completed', 'Completed'),
        ('archived', 'Archived'),
    ]
    
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='ai_conversations')
    
    # Conversation Details
    title = models.CharField(max_length=200, blank=True, null=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='active')
    
    # Context and Preferences
    travel_preferences = models.JSONField(default=dict, blank=True)
    conversation_context = models.JSONField(default=dict, blank=True)
    
    # Related Objects (optional)
    requirement = models.ForeignKey('requirements.TravelRequirement', on_delete=models.CASCADE, null=True, blank=True, related_name='ai_conversations')
    
    # Analytics
    message_count = models.PositiveIntegerField(default=0)
    last_message_at = models.DateTimeField(null=True, blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-last_message_at', '-created_at']
    
    def __str__(self):
        return f"AI Conversation with {self.user.email}"
    
    def generate_title(self):
        """Generate title from first few messages"""
        messages = self.messages.all()[:3]
        if messages:
            first_message = messages.first()
            if len(first_message.content) > 50:
                return first_message.content[:47] + "..."
            return first_message.content
        return "New Conversation"

class AIMessage(models.Model):
    SENDER_CHOICES = [
        ('user', 'User'),
        ('ai', 'AI Assistant'),
    ]
    
    MESSAGE_TYPE_CHOICES = [
        ('text', 'Text'),
        ('image', 'Image'),
        ('file', 'File'),
        ('suggestion', 'Suggestion'),
        ('itinerary', 'Itinerary'),
    ]
    
    conversation = models.ForeignKey(AIConversation, on_delete=models.CASCADE, related_name='messages')
    sender = models.CharField(max_length=10, choices=SENDER_CHOICES)
    message_type = models.CharField(max_length=20, choices=MESSAGE_TYPE_CHOICES, default='text')
    
    # Content
    content = models.TextField()
    raw_response = models.TextField(blank=True, null=True, help_text="Raw AI response before processing")
    
    # AI Processing
    processing_time = models.FloatField(null=True, blank=True)
    token_count = models.PositiveIntegerField(null=True, blank=True)
    model_used = models.CharField(max_length=50, blank=True, null=True)
    temperature = models.FloatField(null=True, blank=True)
    
    # Attachments
    image = models.ForeignKey('media.MediaFile', on_delete=models.SET_NULL, null=True, blank=True, related_name='ai_messages')
    
    # User Actions
    is_liked = models.BooleanField(default=False)
    is_disliked = models.BooleanField(default=False)
    is_bookmarked = models.BooleanField(default=False)
    user_feedback = models.TextField(blank=True, null=True)
    
    # Suggestions (for AI messages)
    suggestions = models.JSONField(default=list, blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['created_at']
    
    def __str__(self):
        return f"{self.sender}: {self.content[:50]}..."

class AISuggestion(models.Model):
    TYPE_CHOICES = [
        ('destination', 'Destination'),
        ('activity', 'Activity'),
        ('accommodation', 'Accommodation'),
        ('transportation', 'Transportation'),
        ('restaurant', 'Restaurant'),
        ('attraction', 'Attraction'),
    ]
    
    conversation = models.ForeignKey(AIConversation, on_delete=models.CASCADE, related_name='suggestions')
    message = models.ForeignKey(AIMessage, on_delete=models.CASCADE, related_name='suggestion_items')
    
    suggestion_type = models.CharField(max_length=20, choices=TYPE_CHOICES)
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True, null=True)
    
    # Location
    location_name = models.CharField(max_length=200, blank=True, null=True)
    latitude = models.DecimalField(max_digits=10, decimal_places=8, null=True, blank=True)
    longitude = models.DecimalField(max_digits=11, decimal_places=8, null=True, blank=True)
    
    # Pricing
    estimated_price = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    currency = models.CharField(max_length=3, default='USD')
    price_range = models.CharField(max_length=50, blank=True, null=True)
    
    # Media
    image = models.ForeignKey('media.MediaFile', on_delete=models.SET_NULL, null=True, blank=True, related_name='suggestions')
    
    # External Links
    booking_url = models.URLField(blank=True, null=True)
    more_info_url = models.URLField(blank=True, null=True)
    
    # User Interaction
    is_saved = models.BooleanField(default=False)
    is_booked = models.BooleanField(default=False)
    view_count = models.PositiveIntegerField(default=0)
    
    # AI Confidence
    confidence_score = models.FloatField(null=True, blank=True)
    relevance_score = models.FloatField(null=True, blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-confidence_score', '-created_at']
    
    def __str__(self):
        return f"{self.title} - {self.get_suggestion_type_display()}"

class AITravelPlan(models.Model):
    STATUS_CHOICES = [
        ('draft', 'Draft'),
        ('generated', 'Generated'),
        ('customized', 'Customized'),
        ('finalized', 'Finalized'),
        ('booked', 'Booked'),
    ]
    
    conversation = models.ForeignKey(AIConversation, on_delete=models.CASCADE, related_name='travel_plans')
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='ai_travel_plans')
    
    # Plan Details
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True, null=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='draft')
    
    # Travel Information
    origin = models.CharField(max_length=200, blank=True, null=True)
    destination = models.CharField(max_length=200)
    start_date = models.DateField(null=True, blank=True)
    end_date = models.DateField(null=True, blank=True)
    duration_days = models.PositiveIntegerField(null=True, blank=True)
    
    # Travelers
    number_of_adults = models.PositiveIntegerField(default=1)
    number_of_children = models.PositiveIntegerField(default=0)
    number_of_infants = models.PositiveIntegerField(default=0)
    
    # Budget
    budget_min = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    budget_max = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    currency = models.CharField(max_length=3, default='USD')
    
    # Preferences
    travel_style = models.CharField(
        max_length=50,
        choices=[
            ('budget', 'Budget'),
            ('mid_range', 'Mid-Range'),
            ('luxury', 'Luxury'),
        ],
        blank=True,
        null=True
    )
    accommodation_type = models.CharField(
        max_length=50,
        choices=[
            ('hotel', 'Hotel'),
            ('hostel', 'Hostel'),
            ('apartment', 'Apartment'),
            ('resort', 'Resort'),
            ('vacation_rental', 'Vacation Rental'),
        ],
        blank=True,
        null=True
    )
    
    # Plan Content
    itinerary = models.JSONField(default=dict, blank=True)
    recommendations = models.JSONField(default=list, blank=True)
    estimated_total_cost = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True)
    
    # Conversion to Requirement
    converted_to_requirement = models.BooleanField(default=False)
    converted_requirement = models.ForeignKey('requirements.TravelRequirement', on_delete=models.SET_NULL, null=True, blank=True, related_name='ai_travel_plans')
    
    # Analytics
    view_count = models.PositiveIntegerField(default=0)
    share_count = models.PositiveIntegerField(default=0)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return f"AI Travel Plan: {self.title}"

class AIKnowledgeBase(models.Model):
    CATEGORY_CHOICES = [
        ('destination', 'Destination Info'),
        ('travel_tips', 'Travel Tips'),
        ('visa_requirements', 'Visa Requirements'),
        ('weather', 'Weather Information'),
        ('culture', 'Cultural Information'),
        ('transportation', 'Transportation'),
        ('accommodation', 'Accommodation'),
        ('activities', 'Activities'),
        ('safety', 'Safety Information'),
    ]
    
    category = models.CharField(max_length=30, choices=CATEGORY_CHOICES)
    title = models.CharField(max_length=200)
    content = models.TextField()
    
    # Location Specific
    country = models.CharField(max_length=100, blank=True, null=True)
    city = models.CharField(max_length=100, blank=True, null=True)
    region = models.CharField(max_length=100, blank=True, null=True)
    
    # Metadata
    tags = models.JSONField(default=list, blank=True)
    source = models.CharField(max_length=200, blank=True, null=True)
    last_updated = models.DateTimeField(null=True, blank=True)
    is_active = models.BooleanField(default=True)
    
    # AI Training
    embedding_vector = models.JSONField(null=True, blank=True, help_text="Vector embedding for similarity search")
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['category', 'title']
        indexes = [
            models.Index(fields=['category']),
            models.Index(fields=['country', 'city']),
        ]
    
    def __str__(self):
        return f"{self.title} - {self.get_category_display()}"

class AIAnalytics(models.Model):
    # Daily Analytics
    date = models.DateField(unique=True)
    
    # Usage Statistics
    total_conversations = models.PositiveIntegerField(default=0)
    total_messages = models.PositiveIntegerField(default=0)
    active_users = models.PositiveIntegerField(default=0)
    new_users = models.PositiveIntegerField(default=0)
    
    # AI Performance
    average_response_time = models.FloatField(default=0.0)
    total_tokens_used = models.PositiveIntegerField(default=0)
    success_rate = models.FloatField(default=0.0)
    
    # User Satisfaction
    satisfaction_score = models.FloatField(default=0.0)
    positive_feedback_count = models.PositiveIntegerField(default=0)
    negative_feedback_count = models.PositiveIntegerField(default=0)
    
    # Feature Usage
    travel_plans_generated = models.PositiveIntegerField(default=0)
    requirements_converted = models.PositiveIntegerField(default=0)
    suggestions_given = models.PositiveIntegerField(default=0)
    suggestions_accepted = models.PositiveIntegerField(default=0)
    
    # Error Tracking
    error_count = models.PositiveIntegerField(default=0)
    common_errors = models.JSONField(default=list, blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-date']
    
    def __str__(self):
        return f"AI Analytics for {self.date}"

class AIModelConfiguration(models.Model):
    model_name = models.CharField(max_length=100, unique=True)
    display_name = models.CharField(max_length=100)
    
    # API Configuration
    api_endpoint = models.URLField()
    api_key = models.CharField(max_length=500, blank=True, null=True)
    model_version = models.CharField(max_length=50, blank=True, null=True)
    
    # Parameters
    max_tokens = models.PositiveIntegerField(default=1000)
    temperature = models.FloatField(default=0.7)
    top_p = models.FloatField(default=1.0)
    frequency_penalty = models.FloatField(default=0.0)
    presence_penalty = models.FloatField(default=0.0)
    
    # Limits and Quotas
    requests_per_minute = models.PositiveIntegerField(default=60)
    requests_per_hour = models.PositiveIntegerField(default=3600)
    requests_per_day = models.PositiveIntegerField(default=86400)
    
    # Cost Information
    cost_per_1k_tokens_input = models.DecimalField(max_digits=10, decimal_places=6, default=0.001)
    cost_per_1k_tokens_output = models.DecimalField(max_digits=10, decimal_places=6, default=0.002)
    
    # Status
    is_active = models.BooleanField(default=False)
    is_primary = models.BooleanField(default=False)
    
    # Usage Statistics
    total_requests = models.PositiveIntegerField(default=0)
    total_tokens_used = models.PositiveIntegerField(default=0)
    total_cost = models.DecimalField(max_digits=12, decimal_places=6, default=0.000000)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-is_primary', '-is_active', 'display_name']
    
    def __str__(self):
        return f"{self.display_name} ({'Active' if self.is_active else 'Inactive'})"
