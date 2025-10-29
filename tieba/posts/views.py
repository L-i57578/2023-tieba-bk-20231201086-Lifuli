"""
Post views for tieba project.
"""

from django.db.models import Q
from rest_framework import viewsets, status, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.views import APIView
from .models import Post, PostImage, Comment, PostLike, CommentLike, PostCollection
from .serializers import (
    PostSerializer, PostCreateSerializer, PostDetailSerializer,
    CommentSerializer, CommentCreateSerializer,
    PostLikeSerializer, CommentLikeSerializer, PostCollectionSerializer
)
from tiebas.models import TiebaMember


class PostViewSet(viewsets.ModelViewSet):
    """帖子视图集"""
    
    queryset = Post.objects.all()
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    
    def get_serializer_class(self):
        if self.action == 'create':
            return PostCreateSerializer
        elif self.action == 'retrieve':
            return PostDetailSerializer
        return PostSerializer
    
    def get_queryset(self):
        queryset = super().get_queryset()
        
        # 过滤条件
        tieba_id = self.request.query_params.get('tieba_id')
        author_id = self.request.query_params.get('author_id')
        post_type = self.request.query_params.get('type')
        is_top = self.request.query_params.get('is_top')
        is_essence = self.request.query_params.get('is_essence')
        
        if tieba_id:
            queryset = queryset.filter(tieba_id=tieba_id)
        
        if author_id:
            queryset = queryset.filter(author_id=author_id)
        
        if post_type:
            queryset = queryset.filter(post_type=post_type)
        
        if is_top is not None:
            queryset = queryset.filter(is_top=is_top.lower() == 'true')
        
        if is_essence is not None:
            queryset = queryset.filter(is_essence=is_essence.lower() == 'true')
        
        return queryset.order_by('-is_top', '-is_essence', '-created_at')
    
    def perform_create(self, serializer):
        # 检查用户是否有权限在该贴吧发帖
        tieba = serializer.validated_data['tieba']
        
        if tieba.is_private:
            # 私有贴吧需要检查成员身份
            if not TiebaMember.objects.filter(tieba=tieba, user=self.request.user).exists():
                raise permissions.PermissionDenied('您不是该贴吧成员，无法发帖')
        
        serializer.save(author=self.request.user)
    
    @action(detail=True, methods=['post'])
    def like(self, request, pk=None):
        """点赞帖子"""
        post = self.get_object()
        
        if PostLike.objects.filter(post=post, user=request.user).exists():
            return Response({'error': '已经点赞过该帖子'}, status=status.HTTP_400_BAD_REQUEST)
        
        like = PostLike.objects.create(post=post, user=request.user)
        
        # 更新帖子点赞数
        post.like_count = PostLike.objects.filter(post=post).count()
        post.save()
        
        serializer = PostLikeSerializer(like)
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    
    @action(detail=True, methods=['post'])
    def unlike(self, request, pk=None):
        """取消点赞帖子"""
        post = self.get_object()
        
        like = PostLike.objects.filter(post=post, user=request.user).first()
        if not like:
            return Response({'error': '未点赞该帖子'}, status=status.HTTP_400_BAD_REQUEST)
        
        like.delete()
        
        # 更新帖子点赞数
        post.like_count = PostLike.objects.filter(post=post).count()
        post.save()
        
        return Response({'message': '已取消点赞'}, status=status.HTTP_200_OK)
    
    @action(detail=True, methods=['post'])
    def collect(self, request, pk=None):
        """收藏帖子"""
        post = self.get_object()
        
        if PostCollection.objects.filter(post=post, user=request.user).exists():
            return Response({'error': '已经收藏过该帖子'}, status=status.HTTP_400_BAD_REQUEST)
        
        collection = PostCollection.objects.create(post=post, user=request.user)
        serializer = PostCollectionSerializer(collection)
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    
    @action(detail=True, methods=['post'])
    def uncollect(self, request, pk=None):
        """取消收藏帖子"""
        post = self.get_object()
        
        collection = PostCollection.objects.filter(post=post, user=request.user).first()
        if not collection:
            return Response({'error': '未收藏该帖子'}, status=status.HTTP_400_BAD_REQUEST)
        
        collection.delete()
        return Response({'message': '已取消收藏'}, status=status.HTTP_200_OK)
    
    @action(detail=True, methods=['post'])
    def set_top(self, request, pk=None):
        """置顶帖子"""
        post = self.get_object()
        
        # 检查权限
        member = TiebaMember.objects.filter(
            tieba=post.tieba, user=request.user
        ).first()
        
        if not member or member.role not in ['admin', 'moderator', 'owner']:
            return Response(
                {'error': '没有权限执行此操作'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        post.is_top = True
        post.save()
        
        serializer = self.get_serializer(post)
        return Response(serializer.data)
    
    @action(detail=True, methods=['post'])
    def cancel_top(self, request, pk=None):
        """取消置顶"""
        post = self.get_object()
        
        # 检查权限
        member = TiebaMember.objects.filter(
            tieba=post.tieba, user=request.user
        ).first()
        
        if not member or member.role not in ['admin', 'moderator', 'owner']:
            return Response(
                {'error': '没有权限执行此操作'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        post.is_top = False
        post.save()
        
        serializer = self.get_serializer(post)
        return Response(serializer.data)
    
    @action(detail=True, methods=['post'])
    def set_essence(self, request, pk=None):
        """设为精华"""
        post = self.get_object()
        
        # 检查权限
        member = TiebaMember.objects.filter(
            tieba=post.tieba, user=request.user
        ).first()
        
        if not member or member.role not in ['admin', 'moderator', 'owner']:
            return Response(
                {'error': '没有权限执行此操作'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        post.is_essence = True
        post.save()
        
        serializer = self.get_serializer(post)
        return Response(serializer.data)
    
    @action(detail=True, methods=['post'])
    def cancel_essence(self, request, pk=None):
        """取消精华"""
        post = self.get_object()
        
        # 检查权限
        member = TiebaMember.objects.filter(
            tieba=post.tieba, user=request.user
        ).first()
        
        if not member or member.role not in ['admin', 'moderator', 'owner']:
            return Response(
                {'error': '没有权限执行此操作'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        post.is_essence = False
        post.save()
        
        serializer = self.get_serializer(post)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def search(self, request):
        """搜索帖子"""
        query = request.query_params.get('q', '')
        tieba_id = request.query_params.get('tieba_id')
        
        queryset = self.get_queryset()
        
        if query:
            queryset = queryset.filter(
                Q(title__icontains=query) | Q(content__icontains=query)
            )
        
        if tieba_id:
            queryset = queryset.filter(tieba_id=tieba_id)
        
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)


class CommentViewSet(viewsets.ModelViewSet):
    """评论视图集"""
    
    queryset = Comment.objects.all()
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    
    def get_serializer_class(self):
        if self.action == 'create':
            return CommentCreateSerializer
        return CommentSerializer
    
    def get_queryset(self):
        queryset = super().get_queryset()
        
        post_id = self.request.query_params.get('post_id')
        author_id = self.request.query_params.get('author_id')
        
        if post_id:
            queryset = queryset.filter(post_id=post_id)
        
        if author_id:
            queryset = queryset.filter(author_id=author_id)
        
        return queryset.order_by('-created_at')
    
    def perform_create(self, serializer):
        serializer.save(author=self.request.user)
    
    @action(detail=True, methods=['post'])
    def like(self, request, pk=None):
        """点赞评论"""
        comment = self.get_object()
        
        if CommentLike.objects.filter(comment=comment, user=request.user).exists():
            return Response({'error': '已经点赞过该评论'}, status=status.HTTP_400_BAD_REQUEST)
        
        like = CommentLike.objects.create(comment=comment, user=request.user)
        
        # 更新评论点赞数
        comment.like_count = CommentLike.objects.filter(comment=comment).count()
        comment.save()
        
        serializer = CommentLikeSerializer(like)
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    
    @action(detail=True, methods=['post'])
    def unlike(self, request, pk=None):
        """取消点赞评论"""
        comment = self.get_object()
        
        like = CommentLike.objects.filter(comment=comment, user=request.user).first()
        if not like:
            return Response({'error': '未点赞该评论'}, status=status.HTTP_400_BAD_REQUEST)
        
        like.delete()
        
        # 更新评论点赞数
        comment.like_count = CommentLike.objects.filter(comment=comment).count()
        comment.save()
        
        return Response({'message': '已取消点赞'}, status=status.HTTP_200_OK)


class UserPostsView(APIView):
    """用户帖子相关视图"""
    
    permission_classes = [permissions.IsAuthenticated]
    
    def get(self, request):
        """获取用户发布的帖子"""
        posts = Post.objects.filter(author=request.user)
        serializer = PostSerializer(posts, many=True)
        return Response(serializer.data)
    
    def post(self, request):
        """获取用户收藏的帖子"""
        collections = PostCollection.objects.filter(user=request.user)
        serializer = PostCollectionSerializer(collections, many=True)
        return Response(serializer.data)


class FeedView(APIView):
    """用户动态流视图"""
    
    permission_classes = [permissions.IsAuthenticated]
    
    def get(self, request):
        """获取用户动态流"""
        # 获取用户关注的贴吧
        followed_tiebas = request.user.tieba_follows.values_list('tieba_id', flat=True)
        
        # 获取用户关注的用户
        followed_users = request.user.following.values_list('following_id', flat=True)
        
        # 获取动态流帖子
        posts = Post.objects.filter(
            Q(tieba_id__in=followed_tiebas) | Q(author_id__in=followed_users)
        ).order_by('-created_at')[:50]
        
        serializer = PostSerializer(posts, many=True)
        return Response(serializer.data)