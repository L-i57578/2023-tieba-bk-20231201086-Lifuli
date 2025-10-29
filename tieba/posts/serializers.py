"""
Post serializers for tieba project.
"""

from rest_framework import serializers
from .models import Post, PostImage, Comment, PostLike, CommentLike, PostCollection
from users.serializers import UserSerializer
from tiebas.serializers import TiebaSerializer


class PostImageSerializer(serializers.ModelSerializer):
    """帖子图片序列化器"""
    
    class Meta:
        model = PostImage
        fields = ['id', 'image', 'description', 'order']
        read_only_fields = ['id']
    
    def to_representation(self, instance):
        data = super().to_representation(instance)
        if instance.image:
            data['image'] = instance.image.url
        return data


class CommentSerializer(serializers.ModelSerializer):
    """评论序列化器"""
    
    author_info = UserSerializer(source='author', read_only=True)
    like_count = serializers.IntegerField(read_only=True)
    is_liked = serializers.SerializerMethodField()
    
    class Meta:
        model = Comment
        fields = [
            'id', 'post', 'author', 'author_info', 'content', 'parent',
            'like_count', 'is_liked', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']
    
    def get_is_liked(self, obj):
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            return CommentLike.objects.filter(
                comment=obj, user=request.user
            ).exists()
        return False


class PostCreateSerializer(serializers.ModelSerializer):
    """帖子创建序列化器"""
    
    images = PostImageSerializer(many=True, required=False)
    
    class Meta:
        model = Post
        fields = [
            'tieba', 'title', 'content', 'post_type', 'images',
            'is_anonymous', 'is_top', 'is_essence'
        ]
    
    def create(self, validated_data):
        images_data = validated_data.pop('images', [])
        post = Post.objects.create(**validated_data)
        
        for image_data in images_data:
            PostImage.objects.create(post=post, **image_data)
        
        return post


class PostSerializer(serializers.ModelSerializer):
    """帖子序列化器"""
    
    author_info = UserSerializer(source='author', read_only=True)
    tieba_info = TiebaSerializer(source='tieba', read_only=True)
    images = PostImageSerializer(many=True, read_only=True)
    comment_count = serializers.IntegerField(read_only=True)
    like_count = serializers.IntegerField(read_only=True)
    is_liked = serializers.SerializerMethodField()
    is_collected = serializers.SerializerMethodField()
    
    class Meta:
        model = Post
        fields = [
            'id', 'tieba', 'tieba_info', 'author', 'author_info', 'title', 'content',
            'post_type', 'images', 'is_anonymous', 'is_top', 'is_essence',
            'comment_count', 'like_count', 'is_liked', 'is_collected',
            'view_count', 'created_at', 'updated_at'
        ]
        read_only_fields = [
            'id', 'comment_count', 'like_count', 'view_count', 'created_at', 'updated_at'
        ]
    
    def get_is_liked(self, obj):
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            return PostLike.objects.filter(
                post=obj, user=request.user
            ).exists()
        return False
    
    def get_is_collected(self, obj):
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            return PostCollection.objects.filter(
                post=obj, user=request.user
            ).exists()
        return False


class PostDetailSerializer(PostSerializer):
    """帖子详情序列化器"""
    
    comments = serializers.SerializerMethodField()
    
    class Meta(PostSerializer.Meta):
        fields = PostSerializer.Meta.fields + ['comments']
    
    def get_comments(self, obj):
        comments = Comment.objects.filter(post=obj, parent=None).order_by('-created_at')
        serializer = CommentSerializer(comments, many=True, context=self.context)
        return serializer.data


class PostLikeSerializer(serializers.ModelSerializer):
    """帖子点赞序列化器"""
    
    user_info = UserSerializer(source='user', read_only=True)
    post_info = PostSerializer(source='post', read_only=True)
    
    class Meta:
        model = PostLike
        fields = ['id', 'user', 'user_info', 'post', 'post_info', 'created_at']
        read_only_fields = ['id', 'created_at']


class CommentLikeSerializer(serializers.ModelSerializer):
    """评论点赞序列化器"""
    
    user_info = UserSerializer(source='user', read_only=True)
    comment_info = CommentSerializer(source='comment', read_only=True)
    
    class Meta:
        model = CommentLike
        fields = ['id', 'user', 'user_info', 'comment', 'comment_info', 'created_at']
        read_only_fields = ['id', 'created_at']


class PostCollectionSerializer(serializers.ModelSerializer):
    """帖子收藏序列化器"""
    
    user_info = UserSerializer(source='user', read_only=True)
    post_info = PostSerializer(source='post', read_only=True)
    
    class Meta:
        model = PostCollection
        fields = ['id', 'user', 'user_info', 'post', 'post_info', 'created_at']
        read_only_fields = ['id', 'created_at']


class CommentCreateSerializer(serializers.ModelSerializer):
    """评论创建序列化器"""
    
    class Meta:
        model = Comment
        fields = ['post', 'content', 'parent']
    
    def validate(self, attrs):
        # 检查父评论是否存在且属于同一个帖子
        parent = attrs.get('parent')
        if parent:
            if parent.post != attrs['post']:
                raise serializers.ValidationError('父评论必须属于同一个帖子')
        return attrs