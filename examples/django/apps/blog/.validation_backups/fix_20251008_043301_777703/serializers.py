"""
DRF Serializers for Blog app.
"""

from rest_framework import serializers
from django.contrib.auth import get_user_model
from .models import Category, Tag, Post, Comment, PostLike, PostView

User = get_user_model()


class CategorySerializer(serializers.ModelSerializer):
    """Serializer for blog categories."""
    
    posts_count = serializers.IntegerField(read_only=True)
    children = serializers.SerializerMethodField()
    
    class Meta:
        model = Category
        fields = [
            'id', 'name', 'slug', 'description', 'color',
            'meta_title', 'meta_description', 'parent',
            'posts_count', 'children', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'slug', 'posts_count', 'created_at', 'updated_at']
    
    def get_children(self, obj):
        if obj.children.exists():
            return CategorySerializer(obj.children.all(), many=True).data
        return []


class TagSerializer(serializers.ModelSerializer):
    """Serializer for blog tags."""
    
    posts_count = serializers.IntegerField(read_only=True)
    
    class Meta:
        model = Tag
        fields = ['id', 'name', 'slug', 'description', 'posts_count', 'created_at']
        read_only_fields = ['id', 'slug', 'posts_count', 'created_at']


class AuthorSerializer(serializers.ModelSerializer):
    """Serializer for post authors."""
    
    full_name = serializers.CharField(read_only=True)
    
    class Meta:
        model = User
        fields = ['id', 'username', 'first_name', 'last_name', 'full_name', 'avatar']


class CommentSerializer(serializers.ModelSerializer):
    """Serializer for blog comments."""
    
    author = AuthorSerializer(read_only=True)
    replies = serializers.SerializerMethodField()
    can_edit = serializers.SerializerMethodField()
    
    class Meta:
        model = Comment
        fields = [
            'id', 'content', 'author', 'parent', 'is_approved',
            'likes_count', 'replies', 'can_edit',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'author', 'is_approved', 'likes_count', 'created_at', 'updated_at']
    
    def get_replies(self, obj):
        if obj.replies.filter(is_approved=True).exists():
            return CommentSerializer(obj.replies.filter(is_approved=True), many=True, context=self.context).data
        return []
    
    def get_can_edit(self, obj):
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            return obj.author == request.user or request.user.is_staff
        return False


class PostLikeSerializer(serializers.ModelSerializer):
    """Serializer for post likes."""
    
    user = AuthorSerializer(read_only=True)
    
    class Meta:
        model = PostLike
        fields = ['id', 'user', 'reaction', 'created_at']
        read_only_fields = ['id', 'user', 'created_at']


class PostListSerializer(serializers.ModelSerializer):
    """Serializer for post list view."""
    
    author = AuthorSerializer(read_only=True)
    category = CategorySerializer(read_only=True)
    tags = TagSerializer(many=True, read_only=True)
    
    class Meta:
        model = Post
        fields = [
            'id', 'title', 'slug', 'excerpt', 'author', 'category', 'tags',
            'status', 'is_featured', 'featured_image', 'featured_image_alt',
            'views_count', 'likes_count', 'comments_count', 'shares_count',
            'published_at', 'created_at', 'updated_at'
        ]


class PostDetailSerializer(serializers.ModelSerializer):
    """Serializer for post detail view."""
    
    author = AuthorSerializer(read_only=True)
    category = CategorySerializer(read_only=True)
    tags = TagSerializer(many=True, read_only=True)
    comments = serializers.SerializerMethodField()
    user_reaction = serializers.SerializerMethodField()
    can_edit = serializers.SerializerMethodField()
    
    class Meta:
        model = Post
        fields = [
            'id', 'title', 'slug', 'content', 'excerpt', 'author',
            'category', 'tags', 'status', 'is_featured', 'allow_comments',
            'meta_title', 'meta_description', 'meta_keywords',
            'featured_image', 'featured_image_alt',
            'views_count', 'likes_count', 'comments_count', 'shares_count',
            'published_at', 'created_at', 'updated_at',
            'comments', 'user_reaction', 'can_edit'
        ]
    
    def get_comments(self, obj):
        if obj.allow_comments:
            comments = obj.comments.filter(is_approved=True, parent=None)
            return CommentSerializer(comments, many=True, context=self.context).data
        return []
    
    def get_user_reaction(self, obj):
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            try:
                like = obj.likes.get(user=request.user)
                return like.reaction
            except PostLike.DoesNotExist:
                pass
        return None
    
    def get_can_edit(self, obj):
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            return obj.author == request.user or request.user.is_staff
        return False


class PostCreateSerializer(serializers.ModelSerializer):
    """Serializer for post creation."""
    
    tags = serializers.PrimaryKeyRelatedField(queryset=Tag.objects.all(), many=True, required=False)
    
    class Meta:
        model = Post
        fields = [
            'title', 'content', 'excerpt', 'category', 'tags',
            'status', 'is_featured', 'allow_comments',
            'meta_title', 'meta_description', 'meta_keywords',
            'featured_image', 'featured_image_alt'
        ]
    
    def create(self, validated_data):
        tags = validated_data.pop('tags', [])
        post = Post.objects.create(author=self.context['request'].user, **validated_data)
        post.tags.set(tags)
        return post


class PostUpdateSerializer(serializers.ModelSerializer):
    """Serializer for post updates."""
    
    tags = serializers.PrimaryKeyRelatedField(queryset=Tag.objects.all(), many=True, required=False)
    
    class Meta:
        model = Post
        fields = [
            'title', 'content', 'excerpt', 'category', 'tags',
            'status', 'is_featured', 'allow_comments',
            'meta_title', 'meta_description', 'meta_keywords',
            'featured_image', 'featured_image_alt'
        ]
    
    def update(self, instance, validated_data):
        tags = validated_data.pop('tags', None)
        
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        
        if tags is not None:
            instance.tags.set(tags)
        
        return instance


class BlogStatsSerializer(serializers.Serializer):
    """Serializer for blog statistics."""
    
    total_posts = serializers.IntegerField()
    published_posts = serializers.IntegerField()
    draft_posts = serializers.IntegerField()
    total_comments = serializers.IntegerField()
    total_views = serializers.IntegerField()
    total_likes = serializers.IntegerField()
    popular_posts = PostListSerializer(many=True)
    recent_posts = PostListSerializer(many=True)
    top_categories = CategorySerializer(many=True)
    top_tags = TagSerializer(many=True)
