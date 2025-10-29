"""
Admin configuration for posts app.
"""

from django.contrib import admin
from .models import Post, PostImage, Comment, PostLike, CommentLike, PostCollection


class PostImageInline(admin.TabularInline):
    """帖子图片内联管理"""
    model = PostImage
    extra = 1


@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
    """帖子管理"""
    
    list_display = ['title', 'tieba', 'author', 'post_type', 'created_at']
    list_filter = ['tieba', 'post_type', 'created_at']
    search_fields = ['title', 'content']
    ordering = ['-created_at']
    
    fieldsets = (
        ('基本信息', {
            'fields': ('tieba', 'author', 'title', 'content', 'post_type')
        }),
        ('帖子设置', {
            'fields': ('is_anonymous',)
        }),
    )
    
    inlines = [PostImageInline]
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('tieba', 'author')


@admin.register(PostImage)
class PostImageAdmin(admin.ModelAdmin):
    """帖子图片管理"""
    
    list_display = ['post', 'image']
    list_filter = ['post']
    ordering = ['post']
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('post')


class CommentInline(admin.TabularInline):
    """评论内联管理"""
    model = Comment
    extra = 0
    readonly_fields = ['author', 'content', 'created_at']


@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    """评论管理"""
    
    list_display = ['post', 'author', 'content_preview', 'created_at']
    list_filter = ['post', 'created_at']
    search_fields = ['content']
    ordering = ['-created_at']
    
    fieldsets = (
        ('基本信息', {
            'fields': ('post', 'author', 'parent', 'content')
        }),
    )
    
    def content_preview(self, obj):
        return obj.content[:50] + '...' if len(obj.content) > 50 else obj.content
    content_preview.short_description = '内容预览'
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('post', 'author')


@admin.register(PostLike)
class PostLikeAdmin(admin.ModelAdmin):
    """帖子点赞管理"""
    
    list_display = ['post', 'user', 'created_at']
    list_filter = ['created_at']
    ordering = ['-created_at']
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('post', 'user')


@admin.register(CommentLike)
class CommentLikeAdmin(admin.ModelAdmin):
    """评论点赞管理"""
    
    list_display = ['comment', 'user', 'created_at']
    list_filter = ['created_at']
    ordering = ['-created_at']
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('comment', 'user')


@admin.register(PostCollection)
class PostCollectionAdmin(admin.ModelAdmin):
    """帖子收藏管理"""
    
    list_display = ['post', 'user', 'created_at']
    list_filter = ['created_at']
    ordering = ['-created_at']
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('post', 'user')