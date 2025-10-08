"""
DRF Views for Blog app.
"""

from rest_framework import viewsets, status, permissions, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from django.db.models import Count, Q, F
from django.utils import timezone
from datetime import timedelta
from drf_spectacular.utils import extend_schema, extend_schema_view, OpenApiParameter, OpenApiTypes
from django_filters.rest_framework import DjangoFilterBackend

from .models import Category, Tag, Post, Comment, PostLike, PostView
from .serializers import (
    BlogCategorySerializer, TagSerializer, PostListSerializer, PostDetailSerializer,
    PostCreateSerializer, PostUpdateSerializer, CommentSerializer,
    PostLikeSerializer, BlogStatsSerializer
)


@extend_schema_view(
    list=extend_schema(
        summary="List categories",
        description="Get a list of all blog categories",
        tags=["Blog - Categories"]
    ),
    create=extend_schema(
        summary="Create category",
        description="Create a new blog category",
        tags=["Blog - Categories"]
    ),
    retrieve=extend_schema(
        summary="Get category",
        description="Get details of a specific category",
        tags=["Blog - Categories"]
    ),
    update=extend_schema(
        summary="Update category",
        description="Update category information",
        tags=["Blog - Categories"]
    ),
    destroy=extend_schema(
        summary="Delete category",
        description="Delete a category",
        tags=["Blog - Categories"]
    ),
)
class CategoryViewSet(viewsets.ModelViewSet):
    """ViewSet for blog categories."""

    queryset = Category.objects.annotate(
        published_posts_count=Count('posts', filter=Q(posts__status='published'))
    ).prefetch_related('children')
    serializer_class = BlogCategorySerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    lookup_field = 'slug'
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['name', 'description']
    ordering_fields = ['name', 'posts_count', 'created_at']
    ordering = ['name']


@extend_schema_view(
    list=extend_schema(
        summary="List tags",
        description="Get a list of all blog tags",
        tags=["Blog - Tags"]
    ),
    create=extend_schema(
        summary="Create tag",
        description="Create a new blog tag",
        tags=["Blog - Tags"]
    ),
)
class TagViewSet(viewsets.ModelViewSet):
    """ViewSet for blog tags."""
    
    queryset = Tag.objects.annotate(
        published_posts_count=Count('posts', filter=Q(posts__status='published'))
    )
    serializer_class = TagSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    lookup_field = 'slug'
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['name', 'description']
    ordering_fields = ['name', 'posts_count', 'created_at']
    ordering = ['name']


@extend_schema_view(
    list=extend_schema(
        summary="List posts",
        description="Get a paginated list of blog posts",
        tags=["Blog - Posts"]
    ),
    create=extend_schema(
        summary="Create post",
        description="Create a new blog post",
        tags=["Blog - Posts"]
    ),
    retrieve=extend_schema(
        summary="Get post",
        description="Get detailed information about a specific post",
        tags=["Blog - Posts"]
    ),
    update=extend_schema(
        summary="Update post",
        description="Update post information",
        tags=["Blog - Posts"]
    ),
    destroy=extend_schema(
        summary="Delete post",
        description="Delete a blog post",
        tags=["Blog - Posts"]
    ),
)
class PostViewSet(viewsets.ModelViewSet):
    """ViewSet for blog posts."""
    
    # Note: 'author' removed from select_related for multi-database compatibility
    # Author (User) is in 'default' DB, Post is in 'blog_db' - SQLite can't JOIN across DBs
    queryset = Post.objects.select_related('category').prefetch_related('tags')
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    lookup_field = 'slug'
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['status', 'category', 'tags', 'is_featured', 'author']
    search_fields = ['title', 'content', 'excerpt']
    ordering_fields = ['published_at', 'created_at', 'views_count', 'likes_count']
    ordering = ['-published_at', '-created_at']
    
    def get_serializer_class(self):
        if self.action == 'list':
            return PostListSerializer
        elif self.action == 'create':
            return PostCreateSerializer
        elif self.action in ['update', 'partial_update']:
            return PostUpdateSerializer
        else:
            return PostDetailSerializer
    
    def get_queryset(self):
        queryset = super().get_queryset()
        
        # Filter published posts for non-staff users
        if not (self.request.user.is_authenticated and self.request.user.is_staff):
            queryset = queryset.filter(status='published')
        
        return queryset
    
    def retrieve(self, request, *args, **kwargs):
        """Override retrieve to track post views."""
        instance = self.get_object()
        
        # Track view
        PostView.objects.create(
            post=instance,
            user=request.user if request.user.is_authenticated else None,
            session_key=request.session.session_key,
            ip_address=request.META.get('REMOTE_ADDR', ''),
            user_agent=request.META.get('HTTP_USER_AGENT', ''),
            referrer=request.META.get('HTTP_REFERER', '')
        )
        
        # Update views count
        Post.objects.filter(pk=instance.pk).update(views_count=F('views_count') + 1)
        
        serializer = self.get_serializer(instance)
        return Response(serializer.data)
    
    @extend_schema(
        summary="Get blog statistics",
        description="Get comprehensive blog statistics",
        responses={200: BlogStatsSerializer},
        tags=["Blog - Posts"]
    )
    @action(detail=False, methods=['get'])
    def stats(self, request):
        """Get blog statistics."""
        now = timezone.now()
        week_ago = now - timedelta(days=7)
        
        stats = {
            'total_posts': Post.objects.count(),
            'published_posts': Post.objects.filter(status='published').count(),
            'draft_posts': Post.objects.filter(status='draft').count(),
            'total_comments': Comment.objects.filter(is_approved=True).count(),
            'total_views': PostView.objects.count(),
            'total_likes': PostLike.objects.count(),
            'popular_posts': Post.objects.filter(status='published').order_by('-views_count')[:5],
            'recent_posts': Post.objects.filter(status='published').order_by('-published_at')[:5],
            'top_categories': Category.objects.annotate(
                published_posts=Count('posts', filter=Q(posts__status='published'))
            ).order_by('-published_posts')[:5],
            'top_tags': Tag.objects.annotate(
                published_posts=Count('posts', filter=Q(posts__status='published'))
            ).order_by('-published_posts')[:10]
        }
        
        serializer = BlogStatsSerializer(stats)
        return Response(serializer.data)
    
    @extend_schema(
        summary="Like/unlike post",
        description="Toggle like status for a post",
        tags=["Blog - Posts"]
    )
    @action(detail=True, methods=['post'], permission_classes=[permissions.IsAuthenticated])
    def like(self, request, slug=None):
        """Like or unlike a post."""
        post = self.get_object()
        reaction = request.data.get('reaction', 'like')
        
        like, created = PostLike.objects.get_or_create(
            post=post,
            user=request.user,
            defaults={'reaction': reaction}
        )
        
        if not created:
            if like.reaction == reaction:
                # Remove like if same reaction
                like.delete()
                Post.objects.filter(pk=post.pk).update(likes_count=F('likes_count') - 1)
                return Response({'status': 'unliked'})
            else:
                # Update reaction
                like.reaction = reaction
                like.save()
                return Response({'status': 'reaction_updated', 'reaction': reaction})
        else:
            # New like
            Post.objects.filter(pk=post.pk).update(likes_count=F('likes_count') + 1)
            return Response({'status': 'liked', 'reaction': reaction})
    
    @extend_schema(
        summary="Get post likes",
        description="Get all likes for a post",
        responses={200: PostLikeSerializer(many=True)},
        tags=["Blog - Posts"]
    )
    @action(detail=True, methods=['get'])
    def likes(self, request, slug=None):
        """Get post likes."""
        post = self.get_object()
        # Note: 'user' removed from select_related for multi-database compatibility
        likes = post.likes.all()
        serializer = PostLikeSerializer(likes, many=True)
        return Response(serializer.data)
    
    @extend_schema(
        summary="Get featured posts",
        description="Get featured blog posts",
        tags=["Blog - Posts"]
    )
    @action(detail=False, methods=['get'])
    def featured(self, request):
        """Get featured posts."""
        posts = Post.objects.filter(status='published', is_featured=True).order_by('-published_at')
        serializer = PostListSerializer(posts, many=True, context={'request': request})
        return Response(serializer.data)


@extend_schema_view(
    list=extend_schema(
        summary="List comments",
        description="Get a list of comments",
        parameters=[
            OpenApiParameter(
                name='post_slug',
                description='Post slug for nested comments endpoint',
                required=False,
                type=OpenApiTypes.STR,
                location=OpenApiParameter.PATH
            )
        ],
        tags=["Blog - Comments"]
    ),
    create=extend_schema(
        summary="Create comment",
        description="Create a new comment",
        parameters=[
            OpenApiParameter(
                name='post_slug',
                description='Post slug for nested comments endpoint',
                required=False,
                type=OpenApiTypes.STR,
                location=OpenApiParameter.PATH
            )
        ],
        tags=["Blog - Comments"]
    ),
    retrieve=extend_schema(
        summary="Get comment",
        description="Get details of a specific comment",
        tags=["Blog - Comments"]
    ),
    update=extend_schema(
        summary="Update comment",
        description="Update comment content",
        tags=["Blog - Comments"]
    ),
    partial_update=extend_schema(
        summary="Partially update comment",
        description="Partially update comment content",
        tags=["Blog - Comments"]
    ),
    destroy=extend_schema(
        summary="Delete comment",
        description="Delete a comment",
        tags=["Blog - Comments"]
    ),
)
class CommentViewSet(viewsets.ModelViewSet):
    """ViewSet for blog comments."""
    
    # Note: 'author' removed from select_related for multi-database compatibility
    queryset = Comment.objects.select_related('post').prefetch_related('replies')
    serializer_class = CommentSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ['post', 'author', 'is_approved', 'parent']
    ordering_fields = ['created_at', 'likes_count']
    ordering = ['-created_at']
    
    def get_queryset(self):
        queryset = super().get_queryset()
        
        # Filter approved comments for non-staff users
        if not (self.request.user.is_authenticated and self.request.user.is_staff):
            queryset = queryset.filter(is_approved=True)
        
        return queryset
    
    def perform_create(self, serializer):
        """Set comment author and request info."""
        serializer.save(
            author=self.request.user,
            ip_address=self.request.META.get('REMOTE_ADDR'),
            user_agent=self.request.META.get('HTTP_USER_AGENT', '')
        )
        
        # Update post comments count
        post = serializer.instance.post
        Post.objects.filter(pk=post.pk).update(comments_count=F('comments_count') + 1)
    
    def perform_destroy(self, instance):
        """Update post comments count when deleting."""
        post = instance.post
        super().perform_destroy(instance)
        Post.objects.filter(pk=post.pk).update(comments_count=F('comments_count') - 1)
