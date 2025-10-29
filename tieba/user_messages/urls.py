"""
URL configuration for user_messages app.
"""

from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

router = DefaultRouter()
router.register(r'messages', views.MessageViewSet, basename='message')
router.register(r'sessions', views.MessageSessionViewSet, basename='session')
router.register(r'notifications', views.NotificationViewSet, basename='notification')
router.register(r'settings', views.NotificationSettingsViewSet, basename='settings')

urlpatterns = [
    # 对话相关
    path('conversation/<int:user_id>/', views.ConversationView.as_view(), name='conversation'),
    
    # 统计信息
    path('stats/', views.MessageStatsView.as_view(), name='message-stats'),
    
    # 包含视图集路由
    path('', include(router.urls)),
]