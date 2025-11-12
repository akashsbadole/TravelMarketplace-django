from django.db import models
from django.conf import settings

class Review(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
        ('flagged', 'Flagged'),
    ]
    
    # Core Information
    booking = models.OneToOneField('bookings.Booking', on_delete=models.CASCADE, related_name='booking_review')
    customer = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='reviews_given')
    agent = models.ForeignKey('agents.Agent', on_delete=models.CASCADE, related_name='reviews_received')
    
    # Review Content
    title = models.CharField(max_length=200)
    content = models.TextField()
    rating = models.PositiveIntegerField(choices=[(i, i) for i in range(1, 6)])  # 1-5 stars
    
    # Detailed Ratings (optional)
    communication_rating = models.PositiveIntegerField(choices=[(i, i) for i in range(1, 6)], null=True, blank=True)
    value_rating = models.PositiveIntegerField(choices=[(i, i) for i in range(1, 6)], null=True, blank=True)
    quality_rating = models.PositiveIntegerField(choices=[(i, i) for i in range(1, 6)], null=True, blank=True)
    punctuality_rating = models.PositiveIntegerField(choices=[(i, i) for i in range(1, 6)], null=True, blank=True)
    professionalism_rating = models.PositiveIntegerField(choices=[(i, i) for i in range(1, 6)], null=True, blank=True)
    
    # Service Specific Ratings
    service_type = models.ForeignKey('requirements.ServiceType', on_delete=models.CASCADE, related_name='reviews')
    
    # Review Status
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    is_verified = models.BooleanField(default=False)  # Verified as genuine travel experience
    is_featured = models.BooleanField(default=False)
    
    # Moderation
    moderated_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, related_name='moderated_reviews')
    moderated_at = models.DateTimeField(null=True, blank=True)
    moderation_notes = models.TextField(blank=True, null=True)
    rejection_reason = models.CharField(max_length=255, blank=True, null=True)
    
    # Response
    agent_response = models.TextField(blank=True, null=True)
    agent_response_date = models.DateTimeField(null=True, blank=True)
    
    # Metadata
    helpful_count = models.PositiveIntegerField(default=0)
    report_count = models.PositiveIntegerField(default=0)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['agent', 'rating']),
            models.Index(fields=['status']),
            models.Index(fields=['created_at']),
        ]
    
    def __str__(self):
        return f"Review for {self.agent.company_name} - {self.rating} stars"
    
    def calculate_average_rating(self):
        """Calculate average of all detailed ratings"""
        ratings = [
            self.communication_rating,
            self.value_rating,
            self.quality_rating,
            self.punctuality_rating,
            self.professionalism_rating
        ]
        ratings = [r for r in ratings if r is not None]
        return sum(ratings) / len(ratings) if ratings else self.rating

class ReviewHelpful(models.Model):
    review = models.ForeignKey(Review, on_delete=models.CASCADE, related_name='helpful_votes')
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='helpful_reviews')
    is_helpful = models.BooleanField(default=True)
    
    class Meta:
        unique_together = ['review', 'user']
    
    def __str__(self):
        return f"{self.user.email} found Review {self.review.id} helpful"

class ReviewReport(models.Model):
    REASON_CHOICES = [
        ('spam', 'Spam'),
        ('fake', 'Fake Review'),
        ('inappropriate', 'Inappropriate Content'),
        ('offensive', 'Offensive Language'),
        ('irrelevant', 'Irrelevant'),
        ('duplicate', 'Duplicate Review'),
    ]
    
    review = models.ForeignKey(Review, on_delete=models.CASCADE, related_name='reports')
    reporter = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='review_reports')
    reason = models.CharField(max_length=30, choices=REASON_CHOICES)
    description = models.TextField(blank=True, null=True)
    
    status = models.CharField(
        max_length=20,
        choices=[
            ('pending', 'Pending'),
            ('reviewed', 'Reviewed'),
            ('resolved', 'Resolved'),
            ('dismissed', 'Dismissed'),
        ],
        default='pending'
    )
    
    reviewed_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, related_name='reviewed_reports')
    reviewed_at = models.DateTimeField(null=True, blank=True)
    resolution_notes = models.TextField(blank=True, null=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        unique_together = ['review', 'reporter']
    
    def __str__(self):
        return f"Report on Review {self.review.id} by {self.reporter.email}"

class AgentRatingSummary(models.Model):
    agent = models.OneToOneField('agents.Agent', on_delete=models.CASCADE, related_name='rating_summary')
    service_type = models.ForeignKey('requirements.ServiceType', on_delete=models.CASCADE, related_name='agent_ratings')
    
    # Rating Summary
    total_reviews = models.PositiveIntegerField(default=0)
    average_rating = models.DecimalField(max_digits=3, decimal_places=2, default=0.00)
    
    # Detailed Averages
    avg_communication = models.DecimalField(max_digits=3, decimal_places=2, null=True, blank=True)
    avg_value = models.DecimalField(max_digits=3, decimal_places=2, null=True, blank=True)
    avg_quality = models.DecimalField(max_digits=3, decimal_places=2, null=True, blank=True)
    avg_punctuality = models.DecimalField(max_digits=3, decimal_places=2, null=True, blank=True)
    avg_professionalism = models.DecimalField(max_digits=3, decimal_places=2, null=True, blank=True)
    
    # Rating Distribution
    one_star_count = models.PositiveIntegerField(default=0)
    two_star_count = models.PositiveIntegerField(default=0)
    three_star_count = models.PositiveIntegerField(default=0)
    four_star_count = models.PositiveIntegerField(default=0)
    five_star_count = models.PositiveIntegerField(default=0)
    
    # Verification Stats
    verified_reviews_count = models.PositiveIntegerField(default=0)
    featured_reviews_count = models.PositiveIntegerField(default=0)
    
    last_updated = models.DateTimeField(auto_now=True)
    
    class Meta:
        unique_together = ['agent', 'service_type']
    
    def __str__(self):
        return f"Rating Summary for {self.agent.company_name} - {self.service_type.name}"
    
    def update_summary(self):
        """Update rating summary based on all reviews"""
        reviews = Review.objects.filter(agent=self.agent, service_type=self.service_type, status='approved')
        
        if not reviews.exists():
            self.total_reviews = 0
            self.average_rating = 0.00
            self.save()
            return
        
        # Basic stats
        self.total_reviews = reviews.count()
        self.average_rating = sum(review.rating for review in reviews) / self.total_reviews
        
        # Detailed averages
        comm_ratings = [r.communication_rating for r in reviews if r.communication_rating]
        val_ratings = [r.value_rating for r in reviews if r.value_rating]
        qual_ratings = [r.quality_rating for r in reviews if r.quality_rating]
        punct_ratings = [r.punctuality_rating for r in reviews if r.punctuality_rating]
        prof_ratings = [r.professionalism_rating for r in reviews if r.professionalism_rating]
        
        self.avg_communication = sum(comm_ratings) / len(comm_ratings) if comm_ratings else None
        self.avg_value = sum(val_ratings) / len(val_ratings) if val_ratings else None
        self.avg_quality = sum(qual_ratings) / len(qual_ratings) if qual_ratings else None
        self.avg_punctuality = sum(punct_ratings) / len(punct_ratings) if punct_ratings else None
        self.avg_professionalism = sum(prof_ratings) / len(prof_ratings) if prof_ratings else None
        
        # Rating distribution
        rating_counts = {1: 0, 2: 0, 3: 0, 4: 0, 5: 0}
        for review in reviews:
            rating_counts[review.rating] += 1
        
        self.one_star_count = rating_counts[1]
        self.two_star_count = rating_counts[2]
        self.three_star_count = rating_counts[3]
        self.four_star_count = rating_counts[4]
        self.five_star_count = rating_counts[5]
        
        # Verification stats
        self.verified_reviews_count = reviews.filter(is_verified=True).count()
        self.featured_reviews_count = reviews.filter(is_featured=True).count()
        
        self.save()

class ReviewTemplate(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True, null=True)
    
    # Template Content
    title_template = models.CharField(max_length=200, blank=True, null=True)
    content_template = models.TextField(blank=True, null=True)
    
    # Service Type Specific
    service_type = models.ForeignKey('requirements.ServiceType', on_delete=models.CASCADE, related_name='review_templates')
    
    # Rating Criteria (what to ask users to rate)
    rating_criteria = models.JSONField(
        default=dict,
        help_text="Dictionary of rating criteria with labels"
    )
    
    is_active = models.BooleanField(default=True)
    usage_count = models.PositiveIntegerField(default=0)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['name']
    
    def __str__(self):
        return f"{self.name} - {self.service_type.name}"
    
    def increment_usage(self):
        """Increment usage count"""
        self.usage_count += 1
        self.save(update_fields=['usage_count'])
