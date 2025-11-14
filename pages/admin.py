from django.contrib import admin
from .models import Page, PageSection, BlogCategory, BlogPost, BlogTag, BlogComment, FAQ, Destination

@admin.register(Page)
class PageAdmin(admin.ModelAdmin):
    list_display = ('title', 'page_type', 'status', 'author', 'created_at')
    list_filter = ('page_type', 'status', 'is_featured', 'created_at')
    search_fields = ('title', 'content')
    prepopulated_fields = {'slug': ('title',)}
    date_hierarchy = 'created_at'

@admin.register(PageSection)
class PageSectionAdmin(admin.ModelAdmin):
    list_display = ('page', 'section_type', 'title', 'order', 'is_active')
    list_filter = ('section_type', 'is_active')
    search_fields = ('page__title', 'title', 'content')

@admin.register(BlogCategory)
class BlogCategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'parent', 'post_count', 'color')
    prepopulated_fields = {'slug': ('name',)}
    search_fields = ('name', 'description')

@admin.register(BlogPost)
class BlogPostAdmin(admin.ModelAdmin):
    list_display = ('title', 'category', 'author', 'status', 'is_featured', 'published_at')
    list_filter = ('status', 'is_featured', 'is_pinned', 'category', 'published_at')
    search_fields = ('title', 'content')
    prepopulated_fields = {'slug': ('title',)}
    date_hierarchy = 'published_at'

@admin.register(BlogTag)
class BlogTagAdmin(admin.ModelAdmin):
    list_display = ('name', 'post_count')
    prepopulated_fields = {'slug': ('name',)}
    search_fields = ('name', 'description')

@admin.register(BlogComment)
class BlogCommentAdmin(admin.ModelAdmin):
    list_display = ('post', 'author_name', 'status', 'created_at')
    list_filter = ('status', 'created_at')
    search_fields = ('content', 'author_name', 'author_email')
    date_hierarchy = 'created_at'

@admin.register(FAQ)
class FAQAdmin(admin.ModelAdmin):
    list_display = ('question', 'category', 'order', 'is_featured', 'is_active')
    list_filter = ('category', 'is_featured', 'is_active')
    search_fields = ('question', 'answer')

@admin.register(Destination)
class DestinationAdmin(admin.ModelAdmin):
    list_display = ('name', 'country', 'region', 'average_rating', 'price_range', 'is_featured', 'is_active')
    list_filter = ('region', 'best_time_to_visit', 'price_range', 'is_featured', 'is_active')
    search_fields = ('name', 'country', 'city', 'description')
    prepopulated_fields = {'slug': ('name',)}
    readonly_fields = ('view_count', 'requirements_count', 'created_at', 'updated_at')
    date_hierarchy = 'created_at'
    fieldsets = (
        ('Basic Information', {
            'fields': ('name', 'slug', 'country', 'city', 'region', 'description')
        }),
        ('Media', {
            'fields': ('image_url', 'gallery_images')
        }),
        ('Travel Information', {
            'fields': ('popular_attractions', 'best_time_to_visit', 'average_rating', 'price_range')
        }),
        ('Statistics', {
            'fields': ('requirements_count', 'view_count')
        }),
        ('Status', {
            'fields': ('is_featured', 'is_active')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )