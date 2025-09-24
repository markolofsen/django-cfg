"""
Admin configuration for Blog app.
"""

from django.contrib import admin
from unfold.admin import ModelAdmin, TabularInline
from .models import Category, Tag, Post, Comment, PostLike, PostView


@admin.register(Category)
class CategoryAdmin(ModelAdmin):
    """Admin for blog categories."""
    
    list_display = ['name', 'parent', 'posts_count', 'created_at']
    list_filter = ['parent', 'created_at']
    search_fields = ['name', 'description']
    prepopulated_fields = {'slug': ('name',)}
    readonly_fields = ['posts_count', 'created_at', 'updated_at']
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('name', 'slug', 'description', 'color', 'parent')
        }),
        ('SEO', {
            'fields': ('meta_title', 'meta_description'),
            'classes': ('collapse',)
        }),
        ('Statistics', {
            'fields': ('posts_count',),
            'classes': ('collapse',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )


@admin.register(Tag)
class TagAdmin(ModelAdmin):
    """Admin for blog tags."""
    
    list_display = ['name', 'posts_count', 'created_at']
    search_fields = ['name', 'description']
    prepopulated_fields = {'slug': ('name',)}
    readonly_fields = ['posts_count', 'created_at']


class CommentInline(TabularInline):
    """Inline for post comments."""
    model = Comment
    extra = 0
    readonly_fields = ['author', 'created_at', 'likes_count']
    fields = ['author', 'content', 'is_approved', 'created_at', 'likes_count']


@admin.register(Post)
class PostAdmin(ModelAdmin):
    """Admin for blog posts."""
    
    list_display = ['title', 'author', 'category', 'status', 'is_featured', 'views_count', 'published_at']
    list_filter = ['status', 'is_featured', 'category', 'tags', 'created_at', 'published_at']
    search_fields = ['title', 'content', 'excerpt']
    prepopulated_fields = {'slug': ('title',)}
    readonly_fields = ['views_count', 'likes_count', 'comments_count', 'shares_count', 'created_at', 'updated_at']
    date_hierarchy = 'published_at'
    inlines = [CommentInline]
    
    fieldsets = (
        ('Content', {
            'fields': ('title', 'slug', 'content', 'excerpt')
        }),
        ('Classification', {
            'fields': ('author', 'category', 'tags')
        }),
        ('Settings', {
            'fields': ('status', 'is_featured', 'allow_comments')
        }),
        ('SEO', {
            'fields': ('meta_title', 'meta_description', 'meta_keywords'),
            'classes': ('collapse',)
        }),
        ('Media', {
            'fields': ('featured_image', 'featured_image_alt'),
            'classes': ('collapse',)
        }),
        ('Statistics', {
            'fields': ('views_count', 'likes_count', 'comments_count', 'shares_count'),
            'classes': ('collapse',)
        }),
        ('Timestamps', {
            'fields': ('published_at', 'created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    filter_horizontal = ['tags']


@admin.register(Comment)
class CommentAdmin(ModelAdmin):
    """Admin for blog comments."""
    
    list_display = ['post', 'author', 'content_preview', 'is_approved', 'likes_count', 'created_at']
    list_filter = ['is_approved', 'is_flagged', 'created_at']
    search_fields = ['content', 'author__username', 'post__title']
    readonly_fields = ['likes_count', 'ip_address', 'user_agent', 'created_at', 'updated_at']
    date_hierarchy = 'created_at'
    
    fieldsets = (
        ('Comment', {
            'fields': ('post', 'author', 'parent', 'content')
        }),
        ('Moderation', {
            'fields': ('is_approved', 'is_flagged')
        }),
        ('Statistics', {
            'fields': ('likes_count',),
            'classes': ('collapse',)
        }),
        ('Request Info', {
            'fields': ('ip_address', 'user_agent'),
            'classes': ('collapse',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def content_preview(self, obj):
        return obj.content[:50] + '...' if len(obj.content) > 50 else obj.content
    content_preview.short_description = 'Content Preview'


@admin.register(PostLike)
class PostLikeAdmin(ModelAdmin):
    """Admin for post likes."""
    
    list_display = ['post', 'user', 'reaction', 'created_at']
    list_filter = ['reaction', 'created_at']
    search_fields = ['post__title', 'user__username']
    readonly_fields = ['created_at']


@admin.register(PostView)
class PostViewAdmin(ModelAdmin):
    """Admin for post views."""
    
    list_display = ['post', 'user', 'ip_address', 'created_at']
    list_filter = ['created_at']
    search_fields = ['post__title', 'user__username', 'ip_address']
    readonly_fields = ['created_at']
    date_hierarchy = 'created_at'
