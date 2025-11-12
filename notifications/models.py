from django.db import models
from django.conf import settings
from django.core.validators import MinValueValidator
from django.utils import timezone
import json

class Notification(models.Model):
    """Notification model"""
    NOTIFICATION_TYPES = [
        ('info', 'Information'),
        ('success', 'Success'),
        ('warning', 'Warning'),
        ('error', 'Error'),
        ('quote', 'Quote Update'),
        ('booking', 'Booking Update'),
        ('payment', 'Payment Update'),
        ('message', 'New Message'),
        ('admin', 'Admin Notification'),
    ]
    
    recipient = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='received_notifications')
    sender = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, related_name='sent_notifications')
    title = models.CharField(max_length=255)
    message = models.TextField()
    notification_type = models.CharField(max_length=20, choices=NOTIFICATION_TYPES, default='info')
    url = models.URLField(max_length=500, blank=True)
    is_read = models.BooleanField(default=False)
    read_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    # Related object for generic relationships
    content_type = models.CharField(max_length=50, blank=True, null=True)
    object_id = models.PositiveIntegerField(null=True, blank=True)
    
    # Additional data as JSON
    extra_data = models.JSONField(default=dict, blank=True)
    
    class Meta:
        db_table = 'notifications'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['recipient', 'is_read', 'created_at']),
            models.Index(fields=['recipient', 'created_at']),
            models.Index(fields=['content_type', 'object_id']),
        ]
    
    def __str__(self):
        return f"{self.title} - {self.recipient.username}"
    
    def mark_as_read(self):
        """Mark notification as read"""
        if not self.is_read:
            self.is_read = True
            self.read_at = timezone.now()
            self.save()
    
    def get_related_object(self):
        """Get the related object if exists"""
        if self.content_type and self.object_id:
            try:
                from django.apps import apps
                model = apps.get_model(self.content_type)
                return model.objects.get(pk=self.object_id)
            except:
                return None
        return None

class NotificationPreference(models.Model):
    """Notification preferences for users"""
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='notification_preferences')
    email_notifications = models.BooleanField(default=True)
    push_notifications = models.BooleanField(default=True)
    sms_notifications = models.BooleanField(default=False)
    quote_notifications = models.BooleanField(default=True)
    booking_notifications = models.BooleanField(default=True)
    message_notifications = models.BooleanField(default=True)
    
    # Daily digest settings
    daily_digest = models.BooleanField(default=False)
    digest_time = models.TimeField(default='09:00')
    
    # Notification frequency settings
    quiet_hours_enabled = models.BooleanField(default=False)
    quiet_hours_start = models.TimeField(default='22:00')
    quiet_hours_end = models.TimeField(default='08:00')
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'notification_preferences'
    
    def __str__(self):
        return f"Preferences for {self.user.username}"

class NotificationTemplate(models.Model):
    """Template for automated notifications"""
    name = models.CharField(max_length=255, unique=True)
    subject = models.CharField(max_length=255)
    body = models.TextField()
    notification_type = models.CharField(max_length=20, choices=Notification.NOTIFICATION_TYPES)
    is_active = models.BooleanField(default=True)
    
    # Template variables help
    variables = models.JSONField(default=dict, blank=True, help_text="Available template variables")
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'notification_templates'
    
    def __str__(self):
        return self.name
    
    def render_body(self, context):
        """Render template body with context"""
        from django.template import Template
        template = Template(self.body)
        return template.render(context)
    
    def render_subject(self, context):
        """Render template subject with context"""
        from django.template import Template
        template = Template(self.subject)
        return template.render(context)

class NotificationBatch(models.Model):
    """Batch notification for sending to multiple users"""
    title = models.CharField(max_length=255)
    message = models.TextField()
    notification_type = models.CharField(max_length=20, choices=Notification.NOTIFICATION_TYPES, default='info')
    url = models.URLField(max_length=500, blank=True)
    
    # Filter criteria for recipients
    user_filters = models.JSONField(default=dict, blank=True, help_text="Filters for selecting users")
    
    # Status tracking
    total_recipients = models.PositiveIntegerField(default=0)
    sent_count = models.PositiveIntegerField(default=0)
    failed_count = models.PositiveIntegerField(default=0)
    
    # Scheduling
    send_immediately = models.BooleanField(default=True)
    scheduled_at = models.DateTimeField(null=True, blank=True)
    sent_at = models.DateTimeField(null=True, blank=True)
    
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'notification_batches'
        ordering = ['-created_at']
    
    def __str__(self):
        return f"Batch: {self.title}"
    
    def get_recipients(self):
        """Get recipients based on filters"""
        from django.contrib.auth import get_user_model
        User = get_user_model()
        
        users = User.objects.all()
        
        # Apply filters if any
        if self.user_filters:
            # Filter by user type (agent/customer)
            if self.user_filters.get('user_type'):
                if self.user_filters['user_type'] == 'agents':
                    users = users.filter(agent__isnull=False)
                elif self.user_filters['user_type'] == 'customers':
                    users = users.filter(agent__isnull=True)
            
            # Filter by specific user IDs
            if self.user_filters.get('user_ids'):
                users = users.filter(id__in=self.user_filters['user_ids'])
            
            # Filter by registration date range
            if self.user_filters.get('registered_after'):
                from datetime import datetime
                date = datetime.fromisoformat(self.user_filters['registered_after'])
                users = users.filter(date_joined__gte=date)
            
            if self.user_filters.get('registered_before'):
                from datetime import datetime
                date = datetime.fromisoformat(self.user_filters['registered_before'])
                users = users.filter(date_joined__lte=date)
        
        return users
    
    def send_notifications(self):
        """Send notifications to all recipients"""
        users = self.get_recipients()
        self.total_recipients = users.count()
        self.sent_count = 0
        self.failed_count = 0
        
        for user in users:
            try:
                Notification.objects.create(
                    recipient=user,
                    title=self.title,
                    message=self.message,
                    notification_type=self.notification_type,
                    url=self.url,
                    extra_data={'batch_id': self.id}
                )
                self.sent_count += 1
            except Exception as e:
                self.failed_count += 1
        
        self.sent_at = timezone.now()
        self.save()

class PushNotificationDevice(models.Model):
    """Push notification device registration"""
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='push_devices')
    device_token = models.CharField(max_length=255, unique=True)
    device_type = models.CharField(max_length=50)  # iOS, Android, Web
    device_name = models.CharField(max_length=255, blank=True)
    is_active = models.BooleanField(default=True)
    last_used = models.DateTimeField(auto_now=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'push_notification_devices'
        unique_together = ['user', 'device_token']
    
    def __str__(self):
        return f"{self.device_type} - {self.user.username}"
