from django.db import models
from django.conf import settings
from decimal import Decimal

class DashboardStats(models.Model):
    PERIOD_CHOICES = [
        ('daily', 'Daily'),
        ('weekly', 'Weekly'),
        ('monthly', 'Monthly'),
        ('yearly', 'Yearly'),
    ]
    
    date = models.DateField()
    period = models.CharField(max_length=20, choices=PERIOD_CHOICES)
    
    # User Statistics
    total_users = models.PositiveIntegerField(default=0)
    new_users = models.PositiveIntegerField(default=0)
    active_users = models.PositiveIntegerField(default=0)
    customer_users = models.PositiveIntegerField(default=0)
    agent_users = models.PositiveIntegerField(default=0)
    
    # Booking Statistics
    total_bookings = models.PositiveIntegerField(default=0)
    new_bookings = models.PositiveIntegerField(default=0)
    completed_bookings = models.PositiveIntegerField(default=0)
    cancelled_bookings = models.PositiveIntegerField(default=0)
    
    # Financial Statistics
    total_revenue = models.DecimalField(max_digits=15, decimal_places=2, default=0.00)
    booking_revenue = models.DecimalField(max_digits=15, decimal_places=2, default=0.00)
    commission_revenue = models.DecimalField(max_digits=15, decimal_places=2, default=0.00)
    agent_payouts = models.DecimalField(max_digits=15, decimal_places=2, default=0.00)
    
    # Requirements and Quotes
    total_requirements = models.PositiveIntegerField(default=0)
    new_requirements = models.PositiveIntegerField(default=0)
    total_quotes = models.PositiveIntegerField(default=0)
    new_quotes = models.PositiveIntegerField(default=0)
    
    # Agent Statistics
    total_agents = models.PositiveIntegerField(default=0)
    new_agents = models.PositiveIntegerField(default=0)
    verified_agents = models.PositiveIntegerField(default=0)
    active_agents = models.PositiveIntegerField(default=0)
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        unique_together = ['date', 'period']
        ordering = ['-date', '-period']
    
    def __str__(self):
        return f"Stats for {self.period} - {self.date}"

class SystemSettings(models.Model):
    CATEGORY_CHOICES = [
        ('general', 'General'),
        ('commission', 'Commission'),
        ('payment', 'Payment'),
        ('email', 'Email'),
        ('security', 'Security'),
        ('features', 'Features'),
    ]
    
    category = models.CharField(max_length=20, choices=CATEGORY_CHOICES)
    key = models.CharField(max_length=100)
    value = models.TextField()
    value_type = models.CharField(
        max_length=20,
        choices=[
            ('string', 'String'),
            ('integer', 'Integer'),
            ('float', 'Float'),
            ('boolean', 'Boolean'),
            ('json', 'JSON'),
        ],
        default='string'
    )
    description = models.TextField(blank=True, null=True)
    
    # Validation
    is_required = models.BooleanField(default=False)
    validation_regex = models.CharField(max_length=200, blank=True, null=True)
    min_value = models.FloatField(null=True, blank=True)
    max_value = models.FloatField(null=True, blank=True)
    
    # UI Configuration
    form_field = models.CharField(
        max_length=20,
        choices=[
            ('text', 'Text Input'),
            ('textarea', 'Text Area'),
            ('number', 'Number Input'),
            ('email', 'Email Input'),
            ('password', 'Password Input'),
            ('select', 'Select Dropdown'),
            ('checkbox', 'Checkbox'),
            ('radio', 'Radio Button'),
        ],
        default='text'
    )
    choices = models.JSONField(default=list, blank=True, help_text="For select/radio fields")
    
    # Access Control
    is_public = models.BooleanField(default=False)
    allowed_user_types = models.JSONField(default=list, blank=True)
    
    # Versioning
    version = models.PositiveIntegerField(default=1)
    last_modified_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, related_name='modified_settings')
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        unique_together = ['category', 'key']
        ordering = ['category', 'key']
    
    def __str__(self):
        return f"{self.category}.{self.key}"

class AdminActivity(models.Model):
    ACTION_CHOICES = [
        ('create', 'Created'),
        ('update', 'Updated'),
        ('delete', 'Deleted'),
        ('approve', 'Approved'),
        ('reject', 'Rejected'),
        ('login', 'Login'),
        ('logout', 'Logout'),
        ('export', 'Export'),
        ('import', 'Import'),
    ]
    
    OBJECT_TYPE_CHOICES = [
        ('user', 'User'),
        ('agent', 'Agent'),
        ('requirement', 'Requirement'),
        ('quote', 'Quote'),
        ('booking', 'Booking'),
        ('payment', 'Payment'),
        ('review', 'Review'),
        ('setting', 'Setting'),
        ('page', 'Page'),
    ]
    
    admin_user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='admin_activities')
    action = models.CharField(max_length=20, choices=ACTION_CHOICES)
    object_type = models.CharField(max_length=20, choices=OBJECT_TYPE_CHOICES)
    object_id = models.PositiveIntegerField(null=True, blank=True)
    object_repr = models.CharField(max_length=200, blank=True, null=True)
    
    # Details
    description = models.TextField(blank=True, null=True)
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    user_agent = models.TextField(blank=True, null=True)
    
    # Changes (for update actions)
    old_values = models.JSONField(null=True, blank=True)
    new_values = models.JSONField(null=True, blank=True)
    
    # Status
    is_success = models.BooleanField(default=True)
    error_message = models.TextField(blank=True, null=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['admin_user', 'created_at']),
            models.Index(fields=['action']),
            models.Index(fields=['object_type']),
            models.Index(fields=['created_at']),
        ]
    
    def __str__(self):
        return f"{self.admin_user.email} {self.action} {self.object_type}"

class SystemAlert(models.Model):
    SEVERITY_CHOICES = [
        ('info', 'Info'),
        ('warning', 'Warning'),
        ('error', 'Error'),
        ('critical', 'Critical'),
    ]
    
    TYPE_CHOICES = [
        ('system', 'System'),
        ('security', 'Security'),
        ('performance', 'Performance'),
        ('business', 'Business'),
        ('maintenance', 'Maintenance'),
    ]
    
    title = models.CharField(max_length=200)
    message = models.TextField()
    severity = models.CharField(max_length=20, choices=SEVERITY_CHOICES)
    alert_type = models.CharField(max_length=20, choices=TYPE_CHOICES)
    
    # Status
    is_active = models.BooleanField(default=True)
    is_acknowledged = models.BooleanField(default=False)
    acknowledged_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, related_name='acknowledged_alerts')
    acknowledged_at = models.DateTimeField(null=True, blank=True)
    
    # Resolution
    is_resolved = models.BooleanField(default=False)
    resolved_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, related_name='resolved_alerts')
    resolved_at = models.DateTimeField(null=True, blank=True)
    resolution_notes = models.TextField(blank=True, null=True)
    
    # Metadata
    source = models.CharField(max_length=100, blank=True, null=True)
    metadata = models.JSONField(default=dict, blank=True)
    
    # Notifications
    email_sent = models.BooleanField(default=False)
    sms_sent = models.BooleanField(default=False)
    push_sent = models.BooleanField(default=False)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['severity', 'is_active']),
            models.Index(fields=['alert_type']),
            models.Index(fields=['created_at']),
        ]
    
    def __str__(self):
        return f"{self.severity.upper()}: {self.title}"

class DataExport(models.Model):
    EXPORT_TYPE_CHOICES = [
        ('users', 'Users'),
        ('agents', 'Agents'),
        ('bookings', 'Bookings'),
        ('payments', 'Payments'),
        ('reviews', 'Reviews'),
        ('analytics', 'Analytics'),
    ]
    
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('processing', 'Processing'),
        ('completed', 'Completed'),
        ('failed', 'Failed'),
    ]
    
    export_type = models.CharField(max_length=20, choices=EXPORT_TYPE_CHOICES)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    
    # Filters and Parameters
    filters = models.JSONField(default=dict, blank=True)
    date_from = models.DateField(null=True, blank=True)
    date_to = models.DateField(null=True, blank=True)
    format = models.CharField(
        max_length=10,
        choices=[
            ('csv', 'CSV'),
            ('xlsx', 'Excel'),
            ('json', 'JSON'),
            ('pdf', 'PDF'),
        ],
        default='csv'
    )
    
    # Results
    file = models.FileField(upload_to='exports/', null=True, blank=True)
    record_count = models.PositiveIntegerField(null=True, blank=True)
    
    # Request Info
    requested_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='data_exports')
    
    # Processing
    started_at = models.DateTimeField(null=True, blank=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    processing_time = models.FloatField(null=True, blank=True)
    error_message = models.TextField(blank=True, null=True)
    
    # Email Notification
    email_notification = models.BooleanField(default=True)
    email_sent = models.BooleanField(default=False)
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.export_type} Export - {self.requested_by.email}"

class BackupLog(models.Model):
    STATUS_CHOICES = [
        ('started', 'Started'),
        ('completed', 'Completed'),
        ('failed', 'Failed'),
        ('restoring', 'Restoring'),
        ('restored', 'Restored'),
    ]
    
    TYPE_CHOICES = [
        ('full', 'Full Backup'),
        ('incremental', 'Incremental'),
        ('database_only', 'Database Only'),
        ('media_only', 'Media Only'),
    ]
    
    backup_type = models.CharField(max_length=20, choices=TYPE_CHOICES)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='started')
    
    # File Information
    file_path = models.CharField(max_length=500, blank=True, null=True)
    file_size = models.BigIntegerField(null=True, blank=True)
    file_hash = models.CharField(max_length=64, blank=True, null=True)
    
    # Backup Details
    description = models.TextField(blank=True, null=True)
    includes_media = models.BooleanField(default=True)
    compression_enabled = models.BooleanField(default=True)
    
    # Timing
    started_at = models.DateTimeField(auto_now_add=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    duration = models.FloatField(null=True, blank=True)
    
    # Restoration
    restored_at = models.DateTimeField(null=True, blank=True)
    restored_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, related_name='restored_backups')
    
    # Error Handling
    error_message = models.TextField(blank=True, null=True)
    retry_count = models.PositiveIntegerField(default=0)
    
    # Automatic vs Manual
    is_automatic = models.BooleanField(default=True)
    initiated_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, related_name='initiated_backups')
    
    class Meta:
        ordering = ['-started_at']
    
    def __str__(self):
        return f"{self.backup_type} Backup - {self.started_at.date()}"

class GlobalSettings(models.Model):
    """Global settings for the marketplace platform"""
    
    # Commission Settings
    agent_commission_rate = models.DecimalField(
        max_digits=5, 
        decimal_places=4, 
        default=Decimal('0.0200'),
        help_text="Agent commission rate (e.g., 0.02 for 2%)"
    )
    customer_commission_rate = models.DecimalField(
        max_digits=5, 
        decimal_places=4, 
        default=Decimal('0.0100'),
        help_text="Customer commission rate (e.g., 0.01 for 1%)"
    )
    minimum_payout_threshold = models.DecimalField(
        max_digits=12, 
        decimal_places=2, 
        default=Decimal('1000.00'),
        help_text="Minimum amount before agent can request payout"
    )
    
    # Payment Settings
    payment_timeout_minutes = models.PositiveIntegerField(
        default=30,
        help_text="Minutes before payment times out"
    )
    refund_policy_days = models.PositiveIntegerField(
        default=7,
        help_text="Days within which refund can be requested"
    )
    
    # Booking Settings
    quote_validity_days = models.PositiveIntegerField(
        default=7,
        help_text="Number of days quotes remain valid"
    )
    auto_confirm_bookings = models.BooleanField(
        default=False,
        help_text="Automatically confirm bookings after payment"
    )
    
    # Platform Settings
    platform_fee_description = models.TextField(
        default="Platform service fee for connecting travelers with verified agents",
        help_text="Description shown to customers about platform fees"
    )
    support_email = models.EmailField(
        default="support@travelmarketplace.com",
        help_text="Customer support email"
    )
    support_phone = models.CharField(
        max_length=20,
        blank=True,
        null=True,
        help_text="Customer support phone"
    )
    
    # Feature Flags
    enable_ai_assistant = models.BooleanField(default=True)
    enable_reviews = models.BooleanField(default=True)
    enable_messaging = models.BooleanField(default=True)
    enable_notifications = models.BooleanField(default=True)
    
    # Maintenance Mode
    maintenance_mode = models.BooleanField(default=False)
    maintenance_message = models.TextField(
        blank=True,
        null=True,
        help_text="Message shown to users during maintenance"
    )
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = "Global Settings"
        verbose_name_plural = "Global Settings"
    
    def __str__(self):
        return "Global Settings"
    
    @classmethod
    def get_settings(cls):
        """Get or create global settings instance"""
        settings, created = cls.objects.get_or_create(pk=1)
        return settings
    
    def save(self, *args, **kwargs):
        """Ensure only one instance exists"""
        self.pk = 1
        super().save(*args, **kwargs)
