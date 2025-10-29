"""
URL configuration for users app.
"""

from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

router = DefaultRouter()
router.register(r'users', views.UserViewSet, basename='user')

urlpatterns = [
    # 认证相关
    path('register/', views.UserRegistrationView.as_view(), name='user-register'),
    path('login/', views.UserLoginView.as_view(), name='user-login'),
    path('logout/', views.UserLogoutView.as_view(), name='user-logout'),
    
    # 用户资料相关
    path('profile/', views.UserProfileView.as_view(), name='user-profile'),
    path('profile/update/', views.UserProfileView.as_view(), name='user-profile-update'),
    path('password/change/', views.UserPasswordChangeView.as_view(), name='user-password-change'),
    
    # 用户搜索
    path('search/', views.UserSearchView.as_view(), name='user-search'),
    
    # 关注相关
    path('follow/<int:user_id>/', views.UserFollowView.as_view(), name='user-follow'),
    path('unfollow/<int:user_id>/', views.UserFollowView.as_view(), name='user-unfollow'),
    path('followers/', views.UserFollowersView.as_view(), name='user-followers'),
    path('following/', views.UserFollowingView.as_view(), name='user-following'),
    
    # 包含视图集路由
    path('', include(router.urls)),
]