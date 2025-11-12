from django.db import models
from django.conf import settings

class ChatMessage(models.Model):
    """Chat message model"""
    SENDER_CHOICES = [
        ('customer', 'Customer'),
        ('agent', 'Agent'),
        ('ai', 'AI Assistant'),
    ('system', 'System'),
    ]
    
    booking = models.ForeignKey('bookings.Booking', on_delete=models.CASCADE, related_name='chat_messages')
    sender_type = models.CharField(max_length=20, choices=SENDER_CHOICES)
    content = models.TextField()
    sender_name = models.CharField(max_length=255)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'chat_messages'
        ordering = ['created_at']
    
    def __str__(self):
        return f"{self.sender_type}: {self.content[:50]}..."

class ChatAttachment(models.Model):
    """Attachment for chat messages"""
    message = models.ForeignKey(ChatMessage, on_delete=models.CASCADE, related_name='attachments')
    file = models.FileField(upload_to='chat_attachments/')
    file_name = models.CharField(max_length=255)
    file_size = models.PositiveIntegerField()
    file_type = models.CharField(max_length=50)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'chat_attachments'
    
    def __str__(self):
        return f"{self.file_name} - {self.message.id}"

class ChatThread(models.Model):
    """Chat thread model"""
    booking = models.OneToOneField('bookings.Booking', on_delete=models.CASCADE, related_name='chat_thread')
    is_active = models.BooleanField(default=True)
    last_message_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'chat_threads'
    
    def __str__(self):
        return f"Thread for Booking #{self.booking.id}"
    
    def get_last_message(self):
        """Get the last message in this thread"""
        return self.booking.chat_messages.last()

class ChatTypingIndicator(models.Model):
    """Typing indicator for chat"""
    booking = models.OneToOneField('bookings.Booking', on_delete=models.CASCADE, related_name='typing_indicator')
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    is_typing = models.BooleanField(default=False)
    last_seen = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'chat_typing_indicators'
        unique_together = ['booking', 'user']
    
    def __str__(self):
        return f"{self.user.username} - Booking #{self.booking.id}"
