"""
Tieba views for tieba project.
"""

from django.db.models import Q
from rest_framework import viewsets, status, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.views import APIView
from .models import TiebaCategory, Tieba, TiebaMember, TiebaFollow
from .serializers import (
    TiebaCategorySerializer, TiebaSerializer, TiebaCreateSerializer,
    TiebaMemberSerializer, TiebaFollowSerializer, TiebaDetailSerializer
)
from users.models import User


class TiebaCategoryViewSet(viewsets.ModelViewSet):
    """贴吧分类视图集"""
    
    queryset = TiebaCategory.objects.all()
    serializer_class = TiebaCategorySerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]


class TiebaViewSet(viewsets.ModelViewSet):
    """贴吧视图集"""
    
    queryset = Tieba.objects.all()
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    
    def get_serializer_class(self):
        if self.action == 'create':
            return TiebaCreateSerializer
        elif self.action == 'retrieve':
            return TiebaDetailSerializer
        return TiebaSerializer
    
    def perform_create(self, serializer):
        serializer.save(owner=self.request.user)
    
    @action(detail=True, methods=['post'])
    def join(self, request, pk=None):
        """加入贴吧"""
        tieba = self.get_object()
        
        if TiebaMember.objects.filter(tieba=tieba, user=request.user).exists():
            return Response({'error': '已经是该贴吧成员'}, status=status.HTTP_400_BAD_REQUEST)
        
        member = TiebaMember.objects.create(
            tieba=tieba,
            user=request.user,
            role='member'
        )
        
        # 更新贴吧成员数量
        tieba.member_count = TiebaMember.objects.filter(tieba=tieba).count()
        tieba.save()
        
        serializer = TiebaMemberSerializer(member)
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    
    @action(detail=True, methods=['post'])
    def leave(self, request, pk=None):
        """退出贴吧"""
        tieba = self.get_object()
        
        member = TiebaMember.objects.filter(tieba=tieba, user=request.user).first()
        if not member:
            return Response({'error': '不是该贴吧成员'}, status=status.HTTP_400_BAD_REQUEST)
        
        member.delete()
        
        # 更新贴吧成员数量
        tieba.member_count = TiebaMember.objects.filter(tieba=tieba).count()
        tieba.save()
        
        return Response({'message': '已退出贴吧'}, status=status.HTTP_200_OK)
    
    @action(detail=True, methods=['post'])
    def follow(self, request, pk=None):
        """关注贴吧"""
        tieba = self.get_object()
        
        if TiebaFollow.objects.filter(tieba=tieba, user=request.user).exists():
            return Response({'error': '已经关注该贴吧'}, status=status.HTTP_400_BAD_REQUEST)
        
        follow = TiebaFollow.objects.create(tieba=tieba, user=request.user)
        serializer = TiebaFollowSerializer(follow)
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    
    @action(detail=True, methods=['post'])
    def unfollow(self, request, pk=None):
        """取消关注贴吧"""
        tieba = self.get_object()
        
        follow = TiebaFollow.objects.filter(tieba=tieba, user=request.user).first()
        if not follow:
            return Response({'error': '未关注该贴吧'}, status=status.HTTP_400_BAD_REQUEST)
        
        follow.delete()
        return Response({'message': '已取消关注'}, status=status.HTTP_200_OK)
    
    @action(detail=False, methods=['get'])
    def search(self, request):
        """搜索贴吧"""
        query = request.query_params.get('q', '')
        category_id = request.query_params.get('category', None)
        
        queryset = self.get_queryset()
        
        if query:
            queryset = queryset.filter(
                Q(name__icontains=query) | Q(description__icontains=query)
            )
        
        if category_id:
            queryset = queryset.filter(category_id=category_id)
        
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def popular(self, request):
        """热门贴吧"""
        queryset = self.get_queryset().order_by('-member_count')[:20]
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def recommended(self, request):
        """推荐贴吧"""
        # 简单的推荐算法：基于用户兴趣标签
        if request.user.is_authenticated:
            user_interests = request.user.interests or []
            if user_interests:
                queryset = self.get_queryset().filter(
                    tags__overlap=user_interests
                ).order_by('-member_count')[:10]
            else:
                queryset = self.get_queryset().order_by('-member_count')[:10]
        else:
            queryset = self.get_queryset().order_by('-member_count')[:10]
        
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)


class TiebaMemberViewSet(viewsets.ModelViewSet):
    """贴吧成员视图集"""
    
    queryset = TiebaMember.objects.all()
    serializer_class = TiebaMemberSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        queryset = super().get_queryset()
        tieba_id = self.request.query_params.get('tieba_id')
        if tieba_id:
            queryset = queryset.filter(tieba_id=tieba_id)
        return queryset
    
    @action(detail=True, methods=['post'])
    def promote(self, request, pk=None):
        """提升成员权限"""
        member = self.get_object()
        
        # 检查当前用户是否有权限
        current_user_member = TiebaMember.objects.filter(
            tieba=member.tieba, user=request.user
        ).first()
        
        if not current_user_member or current_user_member.role not in ['admin', 'owner']:
            return Response(
                {'error': '没有权限执行此操作'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        if member.role == 'member':
            member.role = 'moderator'
        elif member.role == 'moderator':
            member.role = 'admin'
        
        member.save()
        serializer = self.get_serializer(member)
        return Response(serializer.data)
    
    @action(detail=True, methods=['post'])
    def demote(self, request, pk=None):
        """降低成员权限"""
        member = self.get_object()
        
        # 检查当前用户是否有权限
        current_user_member = TiebaMember.objects.filter(
            tieba=member.tieba, user=request.user
        ).first()
        
        if not current_user_member or current_user_member.role not in ['admin', 'owner']:
            return Response(
                {'error': '没有权限执行此操作'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        if member.role == 'admin':
            member.role = 'moderator'
        elif member.role == 'moderator':
            member.role = 'member'
        
        member.save()
        serializer = self.get_serializer(member)
        return Response(serializer.data)


class UserTiebasView(APIView):
    """用户贴吧相关视图"""
    
    permission_classes = [permissions.IsAuthenticated]
    
    def get(self, request):
        """获取用户加入的贴吧"""
        members = TiebaMember.objects.filter(user=request.user)
        serializer = TiebaMemberSerializer(members, many=True)
        return Response(serializer.data)
    
    def post(self, request):
        """获取用户关注的贴吧"""
        follows = TiebaFollow.objects.filter(user=request.user)
        serializer = TiebaFollowSerializer(follows, many=True)
        return Response(serializer.data)