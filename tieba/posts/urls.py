"""
URL configuration for posts app.
"""

from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

router = DefaultRouter()
router.register(r'posts', views.PostViewSet, basename='post')
router.register(r'comments', views.CommentViewSet, basename='comment')

urlpatterns = [
    # 用户帖子相关
    path('user/posts/', views.UserPostsView.as_view(), name='user-posts'),
    
    # 动态流
    path('feed/', views.FeedView.as_view(), name='feed'),
    
    # 包含视图集路由
    path('', include(router.urls)),
]