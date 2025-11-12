from django.db import models
from django.conf import settings

class MediaFile(models.Model):
    FILE_TYPE_CHOICES = [
        ('image', 'Image'),
        ('video', 'Video'),
        ('document', 'Document'),
        ('audio', 'Audio'),
        ('other', 'Other'),
    ]
    
    CATEGORY_CHOICES = [
        ('agent_logo', 'Agent Logo'),
        ('agent_document', 'Agent Document'),
        ('requirement_attachment', 'Requirement Attachment'),
        ('quote_attachment', 'Quote Attachment'),
        ('booking_document', 'Booking Document'),
        ('message_attachment', 'Message Attachment'),
        ('review_photo', 'Review Photo'),
        ('profile_picture', 'Profile Picture'),
        ('banner_image', 'Banner Image'),
        ('general', 'General'),
    ]
    
    # File Information
    file = models.FileField(upload_to='media_files/')
    filename = models.CharField(max_length=255)
    original_filename = models.CharField(max_length=255)
    file_type = models.CharField(max_length=20, choices=FILE_TYPE_CHOICES)
    category = models.CharField(max_length=30, choices=CATEGORY_CHOICES, default='general')
    
    # File Properties
    file_size = models.PositiveIntegerField()
    mime_type = models.CharField(max_length=100)
    width = models.PositiveIntegerField(null=True, blank=True)  # For images/videos
    height = models.PositiveIntegerField(null=True, blank=True)  # For images/videos
    duration = models.PositiveIntegerField(null=True, blank=True)  # For videos/audio
    
    # Descriptive Information
    title = models.CharField(max_length=200, blank=True, null=True)
    description = models.TextField(blank=True, null=True)
    alt_text = models.CharField(max_length=255, blank=True, null=True)
    
    # Ownership and Permissions
    uploaded_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='uploaded_files')
    owner = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, null=True, blank=True, related_name='owned_files')
    is_public = models.BooleanField(default=False)
    
    # Related Objects (optional)
    agent = models.ForeignKey('agents.Agent', on_delete=models.CASCADE, null=True, blank=True, related_name='media_files')
    requirement = models.ForeignKey('requirements.TravelRequirement', on_delete=models.CASCADE, null=True, blank=True, related_name='media_files')
    quote = models.ForeignKey('quotes.Quote', on_delete=models.CASCADE, null=True, blank=True, related_name='media_files')
    booking = models.ForeignKey('bookings.Booking', on_delete=models.CASCADE, null=True, blank=True, related_name='media_files')
    review = models.ForeignKey('reviews.Review', on_delete=models.CASCADE, null=True, blank=True, related_name='media_files')
    
    # Processing
    is_processed = models.BooleanField(default=False)
    thumbnail = models.ImageField(upload_to='thumbnails/', blank=True, null=True)
    processing_error = models.TextField(blank=True, null=True)
    
    # Status
    is_active = models.BooleanField(default=True)
    is_deleted = models.BooleanField(default=False)
    deleted_at = models.DateTimeField(null=True, blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['uploaded_by', 'category']),
            models.Index(fields=['file_type']),
            models.Index(fields=['created_at']),
        ]
    
    def __str__(self):
        return f"{self.filename} - {self.uploaded_by.email}"
    
    def get_file_size_display(self):
        """Return human-readable file size"""
        size = self.file_size
        for unit in ['B', 'KB', 'MB', 'GB']:
            if size < 1024:
                return f"{size:.1f} {unit}"
            size /= 1024
        return f"{size:.1f} TB"

class MediaCollection(models.Model):
    name = models.CharField(max_length=200)
    description = models.TextField(blank=True, null=True)
    
    # Collection Type
    collection_type = models.CharField(
        max_length=50,
        choices=[
            ('agent_portfolio', 'Agent Portfolio'),
            ('destination_gallery', 'Destination Gallery'),
            ('service_showcase', 'Service Showcase'),
            ('testimonials', 'Testimonials'),
            ('general', 'General'),
        ],
        default='general'
    )
    
    # Ownership
    owner = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='media_collections')
    agent = models.ForeignKey('agents.Agent', on_delete=models.CASCADE, null=True, blank=True, related_name='media_collections')
    
    # Files
    files = models.ManyToManyField(MediaFile, related_name='collections')
    
    # Settings
    is_public = models.BooleanField(default=False)
    is_featured = models.BooleanField(default=False)
    
    # Metadata
    cover_image = models.ForeignKey(MediaFile, on_delete=models.SET_NULL, null=True, blank=True, related_name='cover_for_collections')
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.name} - {self.owner.email}"

class MediaTag(models.Model):
    name = models.CharField(max_length=100, unique=True)
    slug = models.SlugField(max_length=100, unique=True)
    description = models.TextField(blank=True, null=True)
    
    # Usage tracking
    usage_count = models.PositiveIntegerField(default=0)
    
    # Hierarchy
    parent = models.ForeignKey('self', on_delete=models.CASCADE, null=True, blank=True, related_name='children')
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['name']
        verbose_name_plural = 'Media Tags'
    
    def __str__(self):
        return self.name

class MediaFileTag(models.Model):
    media_file = models.ForeignKey(MediaFile, on_delete=models.CASCADE, related_name='tags')
    tag = models.ForeignKey(MediaTag, on_delete=models.CASCADE, related_name='tagged_files')
    
    class Meta:
        unique_together = ['media_file', 'tag']
    
    def __str__(self):
        return f"{self.media_file.filename} - {self.tag.name}"

class ImageOptimization(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('processing', 'Processing'),
        ('completed', 'Completed'),
        ('failed', 'Failed'),
    ]
    
    original_file = models.ForeignKey(MediaFile, on_delete=models.CASCADE, related_name='optimizations')
    
    # Optimized versions
    thumbnail_small = models.ImageField(upload_to='optimized/thumbnails/', blank=True, null=True)
    thumbnail_medium = models.ImageField(upload_to='optimized/thumbnails/', blank=True, null=True)
    thumbnail_large = models.ImageField(upload_to='optimized/thumbnails/', blank=True, null=True)
    
    webp_version = models.ImageField(upload_to='optimized/webp/', blank=True, null=True)
    compressed_version = models.ImageField(upload_to='optimized/compressed/', blank=True, null=True)
    
    # Optimization settings
    quality = models.PositiveIntegerField(default=85)
    max_width = models.PositiveIntegerField(null=True, blank=True)
    max_height = models.PositiveIntegerField(null=True, blank=True)
    
    # Processing info
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    original_size = models.PositiveIntegerField()
    optimized_size = models.PositiveIntegerField(null=True, blank=True)
    compression_ratio = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    
    processing_time = models.FloatField(null=True, blank=True)
    error_message = models.TextField(blank=True, null=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    
    def __str__(self):
        return f"Optimization for {self.original_file.filename}"
    
    def calculate_compression_ratio(self):
        """Calculate compression ratio percentage"""
        if self.original_size and self.optimized_size:
            ratio = ((self.original_size - self.optimized_size) / self.original_size) * 100
            self.compression_ratio = round(ratio, 2)
            return self.compression_ratio
        return None
