"""
Admin configuration for user_messages app.
"""

from django.contrib import admin
from .models import Message, Notification, MessageSession, NotificationSettings


@admin.register(Message)
class MessageAdmin(admin.ModelAdmin):
    """私信管理"""
    
    list_display = ['sender', 'receiver', 'content_preview', 'is_read', 'created_at']
    list_filter = ['message_type', 'is_read', 'created_at']
    search_fields = ['content', 'sender__username', 'receiver__username']
    ordering = ['-created_at']
    
    fieldsets = (
        ('基本信息', {
            'fields': ('sender', 'receiver', 'message_type', 'content')
        }),
        ('状态管理', {
            'fields': ('is_read',)
        }),
    )
    
    def content_preview(self, obj):
        return obj.content[:50] + '...' if len(obj.content) > 50 else obj.content
    content_preview.short_description = '内容预览'
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('sender', 'receiver')


class MessageInline(admin.TabularInline):
    """消息内联管理"""
    model = Message
    extra = 0
    readonly_fields = ['sender', 'receiver', 'content', 'created_at']


@admin.register(MessageSession)
class MessageSessionAdmin(admin.ModelAdmin):
    """消息会话管理"""
    
    list_display = ['id', 'user1', 'user2', 'created_at', 'updated_at']
    list_filter = ['created_at']
    ordering = ['-updated_at']
    
    fieldsets = (
        ('会话信息', {
            'fields': ('user1', 'user2')
        }),
        ('会话统计', {
            'fields': ('unread_count_user1', 'unread_count_user2', 'last_message')
        }),
    )


@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    """系统通知管理"""
    
    list_display = [
        'user', 'notification_type', 'title',
        'is_read', 'created_at'
    ]
    list_filter = ['notification_type', 'is_read', 'created_at']
    search_fields = ['title', 'content', 'user__username']
    ordering = ['-created_at']
    
    fieldsets = (
        ('基本信息', {
            'fields': ('user', 'notification_type', 'title', 'content')
        }),
        ('关联对象', {
            'fields': ('related_post', 'related_comment', 'related_user')
        }),
        ('状态管理', {
            'fields': ('is_read',)
        }),
    )
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('user')


@admin.register(NotificationSettings)
class NotificationSettingsAdmin(admin.ModelAdmin):
    """通知设置管理"""
    
    list_display = ['user']
    search_fields = ['user__username']
    
    fieldsets = (
        ('用户设置', {
            'fields': ('user',)
        }),
        ('通知类型', {
            'fields': (
                'enable_private_message', 'enable_system_notification',
                'enable_like_notification', 'enable_comment_notification',
                'enable_follow_notification', 'enable_tieba_notification'
            )
        }),
        ('通知方式', {
            'fields': ('email_notification', 'push_notification')
        }),
    )
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('user')