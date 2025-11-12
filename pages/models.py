from django.db import models
from django.conf import settings

class Page(models.Model):
    STATUS_CHOICES = [
        ('draft', 'Draft'),
        ('published', 'Published'),
        ('archived', 'Archived'),
    ]
    
    PAGE_TYPE_CHOICES = [
        ('static', 'Static Page'),
        ('landing', 'Landing Page'),
        ('blog', 'Blog Post'),
        ('help', 'Help Article'),
        ('faq', 'FAQ'),
        ('terms', 'Terms & Conditions'),
        ('privacy', 'Privacy Policy'),
        ('about', 'About Us'),
        ('contact', 'Contact Us'),
    ]
    
    title = models.CharField(max_length=200)
    slug = models.SlugField(max_length=200, unique=True)
    page_type = models.CharField(max_length=20, choices=PAGE_TYPE_CHOICES, default='static')
    
    # Content
    content = models.TextField()
    excerpt = models.TextField(blank=True, null=True)
    
    # SEO
    meta_title = models.CharField(max_length=200, blank=True, null=True)
    meta_description = models.CharField(max_length=300, blank=True, null=True)
    meta_keywords = models.CharField(max_length=500, blank=True, null=True)
    
    # Status and Publishing
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='draft')
    is_featured = models.BooleanField(default=False)
    show_in_menu = models.BooleanField(default=False)
    menu_order = models.PositiveIntegerField(default=0)
    
    # Authorship
    author = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='authored_pages')
    
    # Featured Image
    featured_image = models.ForeignKey('media.MediaFile', on_delete=models.SET_NULL, null=True, blank=True, related_name='featured_pages')
    
    # Template and Layout
    template = models.CharField(max_length=100, default='default.html')
    custom_css = models.TextField(blank=True, null=True)
    custom_js = models.TextField(blank=True, null=True)
    
    # Publishing Schedule
    published_at = models.DateTimeField(null=True, blank=True)
    expires_at = models.DateTimeField(null=True, blank=True)
    
    # Access Control
    is_public = models.BooleanField(default=True)
    requires_login = models.BooleanField(default=False)
    allowed_user_types = models.CharField(
        max_length=100,
        choices=[
            ('all', 'All Users'),
            ('customers', 'Customers Only'),
            ('agents', 'Agents Only'),
            ('admins', 'Admins Only'),
        ],
        default='all'
    )
    
    # Analytics
    view_count = models.PositiveIntegerField(default=0)
    share_count = models.PositiveIntegerField(default=0)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['slug']),
            models.Index(fields=['status']),
            models.Index(fields=['page_type']),
            models.Index(fields=['published_at']),
        ]
    
    def __str__(self):
        return self.title
    
    def get_absolute_url(self):
        return f"/pages/{self.slug}/"
    
    def increment_views(self):
        """Increment view count"""
        self.view_count += 1
        self.save(update_fields=['view_count'])

class PageSection(models.Model):
    SECTION_TYPE_CHOICES = [
        ('hero', 'Hero Section'),
        ('text', 'Text Block'),
        ('image', 'Image Gallery'),
        ('video', 'Video Section'),
        ('testimonials', 'Testimonials'),
        ('features', 'Features'),
        ('pricing', 'Pricing Tables'),
        ('cta', 'Call to Action'),
        ('form', 'Contact Form'),
        ('faq', 'FAQ Accordion'),
        ('stats', 'Statistics'),
        ('team', 'Team Members'),
        ('partners', 'Partners'),
    ]
    
    page = models.ForeignKey(Page, on_delete=models.CASCADE, related_name='sections')
    section_type = models.CharField(max_length=20, choices=SECTION_TYPE_CHOICES)
    title = models.CharField(max_length=200, blank=True, null=True)
    content = models.TextField(blank=True, null=True)
    
    # Configuration
    config = models.JSONField(default=dict, blank=True, help_text="Section-specific configuration")
    
    # Media
    background_image = models.ForeignKey('media.MediaFile', on_delete=models.SET_NULL, null=True, blank=True, related_name='background_sections')
    images = models.ManyToManyField('media.MediaFile', blank=True, related_name='gallery_sections')
    
    # Ordering and Display
    order = models.PositiveIntegerField(default=0)
    is_active = models.BooleanField(default=True)
    full_width = models.BooleanField(default=False)
    
    # Styling
    background_color = models.CharField(max_length=20, blank=True, null=True)
    text_color = models.CharField(max_length=20, blank=True, null=True)
    custom_classes = models.CharField(max_length=200, blank=True, null=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['order']
    
    def __str__(self):
        return f"{self.page.title} - {self.get_section_type_display()}"

class BlogCategory(models.Model):
    name = models.CharField(max_length=100, unique=True)
    slug = models.SlugField(max_length=100, unique=True)
    description = models.TextField(blank=True, null=True)
    
    # Visual
    color = models.CharField(max_length=7, default='#007bff')
    icon = models.CharField(max_length=50, blank=True, null=True)
    
    # Hierarchy
    parent = models.ForeignKey('self', on_delete=models.CASCADE, null=True, blank=True, related_name='children')
    
    # Stats
    post_count = models.PositiveIntegerField(default=0)
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['name']
        verbose_name_plural = 'Blog Categories'
    
    def __str__(self):
        return self.name

class BlogPost(models.Model):
    STATUS_CHOICES = [
        ('draft', 'Draft'),
        ('published', 'Published'),
        ('scheduled', 'Scheduled'),
        ('archived', 'Archived'),
    ]
    
    title = models.CharField(max_length=200)
    slug = models.SlugField(max_length=200, unique=True)
    content = models.TextField()
    excerpt = models.TextField(blank=True, null=True)
    
    # Category and Tags
    category = models.ForeignKey(BlogCategory, on_delete=models.CASCADE, related_name='posts')
    tags = models.ManyToManyField('BlogTag', blank=True, related_name='posts')
    
    # Author
    author = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='blog_posts')
    
    # Featured Image
    featured_image = models.ForeignKey('media.MediaFile', on_delete=models.SET_NULL, null=True, blank=True, related_name='blog_posts')
    
    # SEO
    meta_title = models.CharField(max_length=200, blank=True, null=True)
    meta_description = models.CharField(max_length=300, blank=True, null=True)
    meta_keywords = models.CharField(max_length=500, blank=True, null=True)
    
    # Status and Publishing
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='draft')
    is_featured = models.BooleanField(default=False)
    is_pinned = models.BooleanField(default=False)
    
    # Publishing Schedule
    published_at = models.DateTimeField(null=True, blank=True)
    
    # Reading Time
    reading_time_minutes = models.PositiveIntegerField(null=True, blank=True)
    
    # Analytics
    view_count = models.PositiveIntegerField(default=0)
    like_count = models.PositiveIntegerField(default=0)
    comment_count = models.PositiveIntegerField(default=0)
    share_count = models.PositiveIntegerField(default=0)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-published_at', '-created_at']
        indexes = [
            models.Index(fields=['slug']),
            models.Index(fields=['status']),
            models.Index(fields=['category']),
            models.Index(fields=['published_at']),
        ]
    
    def __str__(self):
        return self.title
    
    def get_absolute_url(self):
        return f"/blog/{self.slug}/"
    
    def calculate_reading_time(self):
        """Calculate estimated reading time (200 words per minute)"""
        word_count = len(self.content.split())
        self.reading_time_minutes = max(1, word_count // 200)
        return self.reading_time_minutes

class BlogTag(models.Model):
    name = models.CharField(max_length=100, unique=True)
    slug = models.SlugField(max_length=100, unique=True)
    description = models.TextField(blank=True, null=True)
    
    # Stats
    post_count = models.PositiveIntegerField(default=0)
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['name']
    
    def __str__(self):
        return self.name

class BlogComment(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
        ('spam', 'Spam'),
    ]
    
    post = models.ForeignKey(BlogPost, on_delete=models.CASCADE, related_name='comments')
    parent = models.ForeignKey('self', on_delete=models.CASCADE, null=True, blank=True, related_name='replies')
    
    # Comment Content
    author_name = models.CharField(max_length=100)
    author_email = models.EmailField()
    author_website = models.URLField(blank=True, null=True)
    content = models.TextField()
    
    # User (if logged in)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, null=True, blank=True, related_name='blog_comments')
    
    # Status and Moderation
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    moderated_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, related_name='moderated_comments')
    moderated_at = models.DateTimeField(null=True, blank=True)
    moderation_notes = models.TextField(blank=True, null=True)
    
    # Metadata
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    user_agent = models.TextField(blank=True, null=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['created_at']
    
    def __str__(self):
        return f"Comment by {self.author_name} on {self.post.title}"

class FAQ(models.Model):
    CATEGORY_CHOICES = [
        ('general', 'General'),
        ('booking', 'Booking'),
        ('payment', 'Payment'),
        ('agent', 'Agent'),
        ('technical', 'Technical'),
        ('account', 'Account'),
    ]
    
    question = models.CharField(max_length=300)
    answer = models.TextField()
    category = models.CharField(max_length=20, choices=CATEGORY_CHOICES, default='general')
    
    # Ordering and Display
    order = models.PositiveIntegerField(default=0)
    is_featured = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    
    # Analytics
    view_count = models.PositiveIntegerField(default=0)
    helpful_count = models.PositiveIntegerField(default=0)
    not_helpful_count = models.PositiveIntegerField(default=0)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['category', 'order']
        verbose_name_plural = 'FAQs'
    
    def __str__(self):
        return self.question
    
    def increment_views(self):
        """Increment view count"""
        self.view_count += 1
        self.save(update_fields=['view_count'])
    
    def mark_helpful(self, is_helpful=True):
        """Mark as helpful or not helpful"""
        if is_helpful:
            self.helpful_count += 1
        else:
            self.not_helpful_count += 1
        self.save()
