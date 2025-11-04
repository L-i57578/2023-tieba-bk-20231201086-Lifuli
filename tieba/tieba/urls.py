"""
URL configuration for tieba project.
"""

from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from . import views

urlpatterns = [
    # 前端页面路由
    path('', views.HomeView.as_view(), name='home'),
    path('tieba-square/', views.TiebaSquareView.as_view(), name='tieba_square'),
    path('profile/', views.UserProfileView.as_view(), name='user_profile'),
    path('profile/edit/', views.EditProfileView.as_view(), name='edit_profile'),
    path('publish/', views.PublishCenterView.as_view(), name='publish_center'),
    path('messages/', views.MessagesView.as_view(), name='messages'),
    path('login/', views.LoginView.as_view(), name='login'),
    path('logout/', views.LogoutView.as_view(), name='logout'),
    path('register/', views.RegisterView.as_view(), name='register'),
    path('search/', views.GlobalSearchView.as_view(), name='global_search'),
    path('post/<int:pk>/', views.PostDetailView.as_view(), name='post_detail'),
    path('tieba/<int:pk>/', views.TiebaDetailView.as_view(), name='tieba_detail'),
    
    # API路由
    path('admin/', admin.site.urls),
    path('api/auth/', include('users.urls')),
    path('api/tiebas/', include('tiebas.urls')),
    path('api/posts/', include('posts.urls')),
    path('api/messages/', include('user_messages.urls')),
]

# 错误处理页面
handler404 = views.custom_404_view
handler500 = views.custom_500_view

# Serve static files during development
if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)