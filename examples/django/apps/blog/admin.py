"""
Admin configuration for Blog app using django-cfg admin system.
"""

from django.contrib import admin
from django.db.models import Count
from unfold.admin import ModelAdmin, TabularInline
from django_cfg.modules.django_admin import (
    OptimizedModelAdmin,
    DisplayMixin,
    StatusBadgeConfig,
    Icons,
    ActionVariant,
    display,
    action,
)

from .models import Category, Tag, Post, Comment, PostLike, PostView


@admin.register(Category)
class CategoryAdmin(OptimizedModelAdmin, DisplayMixin, ModelAdmin):
    """Admin for blog categories with django-cfg enhancements."""

    # Performance optimization
    select_related_fields = ['parent']

    # List configuration
    list_display = ['name_display', 'parent_display', 'posts_count_display', 'created_display']
    list_filter = ['parent', 'created_at']
    search_fields = ['name', 'description']
    prepopulated_fields = {'slug': ('name',)}
    readonly_fields = ['posts_count', 'created_at', 'updated_at']

    # Autocomplete
    autocomplete_fields = ['parent']

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

    @display(description="Category Name", ordering="name")
    def name_display(self, obj):
        """Display category name with color."""
        from django_cfg.modules.django_admin.utils.badges import StatusBadge
        return StatusBadge.create(
            text=obj.name,
            variant="info",
            config=StatusBadgeConfig(show_icons=False)
        )

    @display(description="Parent")
    def parent_display(self, obj):
        """Display parent category."""
        return obj.parent.name if obj.parent else "—"

    @display(description="Posts")
    def posts_count_display(self, obj):
        """Display posts count as badge."""
        return self.display_count_simple(obj, 'posts_count', 'posts')

    @display(description="Created")
    def created_display(self, obj):
        """Display created date."""
        return self.display_datetime_relative(obj, 'created_at')


@admin.register(Tag)
class TagAdmin(OptimizedModelAdmin, DisplayMixin, ModelAdmin):
    """Admin for blog tags with django-cfg enhancements."""

    # List configuration
    list_display = ['name_display', 'posts_count_display', 'created_display']
    search_fields = ['name', 'description']
    prepopulated_fields = {'slug': ('name',)}
    readonly_fields = ['posts_count', 'created_at']

    @display(description="Tag", ordering="name")
    def name_display(self, obj):
        """Display tag name as badge."""
        from django_cfg.modules.django_admin.utils.badges import StatusBadge
        return StatusBadge.create(
            text=obj.name,
            variant="primary"
        )

    @display(description="Posts")
    def posts_count_display(self, obj):
        """Display posts count."""
        return self.display_count_simple(obj, 'posts_count', 'posts')

    @display(description="Created")
    def created_display(self, obj):
        """Display created date."""
        return self.display_datetime_relative(obj, 'created_at')


class CommentInline(TabularInline):
    """Inline for post comments."""
    model = Comment
    extra = 0
    readonly_fields = ['author', 'created_at', 'likes_count']
    fields = ['author', 'content', 'is_approved', 'created_at', 'likes_count']


@admin.register(Post)
class PostAdmin(OptimizedModelAdmin, DisplayMixin, ModelAdmin):
    """Admin for blog posts with django-cfg enhancements."""

    # Performance optimization
    select_related_fields = ['author', 'category']

    # List configuration
    list_display = [
        'title_display',
        'author_display',
        'category_display',
        'status_display',
        'featured_display',
        'stats_display',
        'published_display'
    ]
    list_filter = ['status', 'is_featured', 'category', 'tags', 'created_at', 'published_at']
    search_fields = ['title', 'content', 'excerpt']
    prepopulated_fields = {'slug': ('title',)}
    readonly_fields = ['views_count', 'likes_count', 'comments_count', 'shares_count', 'created_at', 'updated_at']
    date_hierarchy = 'published_at'
    inlines = [CommentInline]
    filter_horizontal = ['tags']

    # Autocomplete
    autocomplete_fields = ['author', 'category']

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

    # Status configuration
    POST_STATUS_CONFIG = StatusBadgeConfig(
        custom_mappings={
            'draft': 'secondary',
            'published': 'success',
            'archived': 'warning'
        },
        show_icons=True
    )

    @display(description="Title", ordering="title")
    def title_display(self, obj):
        """Display post title."""
        return obj.title

    @display(description="Author", header=True)
    def author_display(self, obj):
        """Display author with avatar."""
        return self.display_user_with_avatar(obj, 'author')

    @display(description="Category")
    def category_display(self, obj):
        """Display category."""
        if not obj.category:
            return "—"
        from django_cfg.modules.django_admin.utils.badges import StatusBadge
        return StatusBadge.create(
            text=obj.category.name,
            variant="info"
        )

    @display(description="Status", label=True)
    def status_display(self, obj):
        """Display post status."""
        return self.display_status_auto(obj, 'status', self.POST_STATUS_CONFIG)

    @display(description="Featured")
    def featured_display(self, obj):
        """Display featured status."""
        from django_cfg.modules.django_admin.utils.badges import StatusBadge
        if obj.is_featured:
            return StatusBadge.create(
                text="★ Featured",
                variant="warning",
                config=StatusBadgeConfig(show_icons=False)
            )
        return "—"

    @display(description="Stats")
    def stats_display(self, obj):
        """Display statistics summary."""
        from django.utils.html import format_html
        return format_html(
            '<small>👁 {} | 💬 {} | ❤️ {}</small>',
            obj.views_count,
            obj.comments_count,
            obj.likes_count
        )

    @display(description="Published")
    def published_display(self, obj):
        """Display published date."""
        if not obj.published_at:
            return "—"
        return self.display_datetime_relative(obj, 'published_at')

    # Actions
    @action(description="Publish posts", variant=ActionVariant.SUCCESS)
    def publish_posts(self, request, queryset):
        """Publish selected posts."""
        from django.utils import timezone
        updated = queryset.update(status='published', published_at=timezone.now())
        self.message_user(request, f"Published {updated} posts.")

    @action(description="Archive posts", variant=ActionVariant.WARNING)
    def archive_posts(self, request, queryset):
        """Archive selected posts."""
        updated = queryset.update(status='archived')
        self.message_user(request, f"Archived {updated} posts.")

    @action(description="Feature posts", variant=ActionVariant.INFO)
    def feature_posts(self, request, queryset):
        """Mark posts as featured."""
        updated = queryset.update(is_featured=True)
        self.message_user(request, f"Marked {updated} posts as featured.")


@admin.register(Comment)
class CommentAdmin(OptimizedModelAdmin, DisplayMixin, ModelAdmin):
    """Admin for blog comments with django-cfg enhancements."""

    # Performance optimization
    select_related_fields = ['post', 'author']

    # List configuration
    list_display = [
        'post_display',
        'author_display',
        'content_preview',
        'status_display',
        'likes_count_display',
        'created_display'
    ]
    list_filter = ['is_approved', 'is_flagged', 'created_at']
    search_fields = ['content', 'author__username', 'post__title']
    readonly_fields = ['likes_count', 'ip_address', 'user_agent', 'created_at', 'updated_at']
    date_hierarchy = 'created_at'

    # Autocomplete
    autocomplete_fields = ['post', 'author', 'parent']

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

    @display(description="Post")
    def post_display(self, obj):
        """Display post title."""
        return obj.post.title[:50]

    @display(description="Author")
    def author_display(self, obj):
        """Display author."""
        return self.display_user_simple(obj, 'author')

    @display(description="Content")
    def content_preview(self, obj):
        """Display content preview."""
        return obj.content[:50] + '...' if len(obj.content) > 50 else obj.content

    @display(description="Status", label=True)
    def status_display(self, obj):
        """Display approval status."""
        config = StatusBadgeConfig(
            custom_mappings={
                True: 'success',
                False: 'warning'
            },
            show_icons=True
        )
        from django_cfg.modules.django_admin.utils.badges import StatusBadge
        if obj.is_flagged:
            return StatusBadge.create(text="Flagged", variant="danger")
        return StatusBadge.auto("Approved" if obj.is_approved else "Pending", config)

    @display(description="Likes")
    def likes_count_display(self, obj):
        """Display likes count."""
        return self.display_count_simple(obj, 'likes_count', 'likes')

    @display(description="Created")
    def created_display(self, obj):
        """Display created date."""
        return self.display_datetime_relative(obj, 'created_at')

    # Actions
    @action(description="Approve comments", variant=ActionVariant.SUCCESS)
    def approve_comments(self, request, queryset):
        """Approve selected comments."""
        updated = queryset.update(is_approved=True)
        self.message_user(request, f"Approved {updated} comments.")

    @action(description="Flag comments", variant=ActionVariant.DANGER)
    def flag_comments(self, request, queryset):
        """Flag selected comments."""
        updated = queryset.update(is_flagged=True)
        self.message_user(request, f"Flagged {updated} comments.")


@admin.register(PostLike)
class PostLikeAdmin(OptimizedModelAdmin, DisplayMixin, ModelAdmin):
    """Admin for post likes with django-cfg enhancements."""

    # Performance optimization
    select_related_fields = ['post', 'user']

    # List configuration
    list_display = ['post_display', 'user_display', 'reaction_display', 'created_display']
    list_filter = ['reaction', 'created_at']
    search_fields = ['post__title', 'user__username']
    readonly_fields = ['created_at']

    # Autocomplete
    autocomplete_fields = ['post', 'user']

    @display(description="Post")
    def post_display(self, obj):
        """Display post title."""
        return obj.post.title[:40]

    @display(description="User")
    def user_display(self, obj):
        """Display user."""
        return self.display_user_simple(obj, 'user')

    @display(description="Reaction", label=True)
    def reaction_display(self, obj):
        """Display reaction."""
        from django_cfg.modules.django_admin.utils.badges import StatusBadge
        return StatusBadge.create(text=obj.get_reaction_display(), variant="primary")

    @display(description="Created")
    def created_display(self, obj):
        """Display created date."""
        return self.display_datetime_relative(obj, 'created_at')


@admin.register(PostView)
class PostViewAdmin(OptimizedModelAdmin, DisplayMixin, ModelAdmin):
    """Admin for post views with django-cfg enhancements."""

    # Performance optimization
    select_related_fields = ['post', 'user']

    # List configuration
    list_display = ['post_display', 'user_display', 'ip_address', 'created_display']
    list_filter = ['created_at']
    search_fields = ['post__title', 'user__username', 'ip_address']
    readonly_fields = ['created_at']
    date_hierarchy = 'created_at'

    # Autocomplete
    autocomplete_fields = ['post', 'user']

    @display(description="Post")
    def post_display(self, obj):
        """Display post title."""
        return obj.post.title[:40]

    @display(description="User")
    def user_display(self, obj):
        """Display user."""
        if obj.user:
            return self.display_user_simple(obj, 'user')
        return "Anonymous"

    @display(description="Created")
    def created_display(self, obj):
        """Display created date."""
        return self.display_datetime_relative(obj, 'created_at')
