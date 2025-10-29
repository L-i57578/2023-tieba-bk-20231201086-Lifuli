"""
Admin configuration for tiebas app.
"""

from django.contrib import admin
from .models import TiebaCategory, Tieba, TiebaMember, TiebaFollow


@admin.register(TiebaCategory)
class TiebaCategoryAdmin(admin.ModelAdmin):
    """贴吧分类管理"""
    
    list_display = ['name', 'description']
    search_fields = ['name', 'description']


@admin.register(Tieba)
class TiebaAdmin(admin.ModelAdmin):
    """贴吧管理"""
    
    list_display = ['name', 'category', 'creator']
    search_fields = ['name', 'description']
    
    fieldsets = (
        ('基本信息', {
            'fields': ('name', 'description', 'category', 'creator')
        }),
        ('图片设置', {
            'fields': ('avatar', 'banner')
        }),
        ('贴吧设置', {
            'fields': ('rules', 'tags')
        }),
    )
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('category', 'creator')


@admin.register(TiebaMember)
class TiebaMemberAdmin(admin.ModelAdmin):
    """贴吧成员管理"""
    
    list_display = ['tieba', 'user', 'role', 'level', 'experience', 'joined_at']
    list_filter = ['role', 'level', 'joined_at']
    search_fields = ['tieba__name', 'user__username']
    ordering = ['-joined_at']
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('tieba', 'user')


@admin.register(TiebaFollow)
class TiebaFollowAdmin(admin.ModelAdmin):
    """贴吧关注管理"""
    
    list_display = ['user', 'tieba', 'created_at']
    list_filter = ['created_at']
    search_fields = ['user__username', 'tieba__name']
    ordering = ['-created_at']
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('user', 'tieba')