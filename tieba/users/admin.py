"""
Admin configuration for users app.
"""

from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User, UserFollow


@admin.register(User)
class CustomUserAdmin(UserAdmin):
    """自定义用户管理"""
    
    list_display = [
        'username', 'email', 'phone', 'nickname', 'gender',
        'followers_count', 'following_count', 'posts_count', 'likes_count',
        'is_active', 'is_staff', 'created_at'
    ]
    list_filter = ['gender', 'is_active', 'is_staff', 'created_at']
    search_fields = ['username', 'email', 'phone', 'nickname']
    ordering = ['-created_at']
    
    fieldsets = UserAdmin.fieldsets + (
        ('个人信息', {
            'fields': (
                'nickname', 'avatar', 'bio', 'phone', 'website',
                'gender', 'birthday', 'location', 'interests'
            )
        }),
        ('社交账号', {
            'fields': ('weibo', 'wechat', 'qq', 'instagram')
        }),
        ('统计信息', {
            'fields': ('followers_count', 'following_count', 'posts_count', 'likes_count')
        }),
    )
    
    readonly_fields = ['followers_count', 'following_count', 'posts_count', 'likes_count']


@admin.register(UserFollow)
class UserFollowAdmin(admin.ModelAdmin):
    """用户关注管理"""
    
    list_display = ['follower', 'following', 'created_at']
    list_filter = ['created_at']
    search_fields = ['follower__username', 'following__username']
    ordering = ['-created_at']
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('follower', 'following')