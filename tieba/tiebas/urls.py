"""
URL configuration for tiebas app.
"""

from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

router = DefaultRouter()
router.register(r'categories', views.TiebaCategoryViewSet, basename='category')
router.register(r'tiebas', views.TiebaViewSet, basename='tieba')
router.register(r'members', views.TiebaMemberViewSet, basename='member')

urlpatterns = [
    # 用户贴吧相关
    path('user/tiebas/', views.UserTiebasView.as_view(), name='user-tiebas'),
    
    # 包含视图集路由
    path('', include(router.urls)),
]