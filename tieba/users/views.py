"""
User views for tieba project.
"""

from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required
from django.db.models import Q
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from rest_framework import status, viewsets, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.views import APIView
from .models import User, UserFollow
from .serializers import UserSerializer, UserRegistrationSerializer, UserLoginSerializer


class UserRegistrationView(APIView):
    """用户注册视图"""
    
    permission_classes = [permissions.AllowAny]
    
    def post(self, request):
        serializer = UserRegistrationSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            
            # 自动登录用户
            login(request, user)
            
            return Response({
                'success': True,
                'message': '注册成功',
                'user': UserSerializer(user).data
            }, status=status.HTTP_201_CREATED)
        
        return Response({
            'success': False,
            'message': '注册失败',
            'errors': serializer.errors
        }, status=status.HTTP_400_BAD_REQUEST)


class UserLoginView(APIView):
    """用户登录视图"""
    
    permission_classes = [permissions.AllowAny]
    
    def post(self, request):
        serializer = UserLoginSerializer(data=request.data)
        if serializer.is_valid():
            username = serializer.validated_data['username']
            password = serializer.validated_data['password']
            remember = serializer.validated_data.get('remember', False)
            
            # 验证用户
            user = authenticate(username=username, password=password)
            
            if user is not None:
                login(request, user)
                
                # 设置会话过期时间
                if not remember:
                    request.session.set_expiry(0)  # 浏览器关闭时过期
                else:
                    request.session.set_expiry(1209600)  # 2周
                
                return Response({
                    'success': True,
                    'message': '登录成功',
                    'user': UserSerializer(user).data
                })
            else:
                return Response({
                    'success': False,
                    'message': '用户名或密码错误'
                }, status=status.HTTP_400_BAD_REQUEST)
        
        return Response({
            'success': False,
            'message': '输入数据无效',
            'errors': serializer.errors
        }, status=status.HTTP_400_BAD_REQUEST)


class UserLogoutView(APIView):
    """用户登出视图"""
    
    def post(self, request):
        logout(request)
        return Response({
            'success': True,
            'message': '登出成功'
        })


class UserProfileView(APIView):
    """用户个人资料视图"""
    
    def get(self, request):
        user = request.user
        serializer = UserSerializer(user)
        return Response({
            'success': True,
            'user': serializer.data
        })
    
    def put(self, request):
        user = request.user
        serializer = UserSerializer(user, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response({
                'success': True,
                'message': '资料更新成功',
                'user': serializer.data
            })
        
        return Response({
            'success': False,
            'message': '资料更新失败',
            'errors': serializer.errors
        }, status=status.HTTP_400_BAD_REQUEST)


class UserFollowView(APIView):
    """用户关注/取消关注视图"""
    
    def post(self, request, user_id):
        try:
            target_user = User.objects.get(id=user_id)
        except User.DoesNotExist:
            return Response({
                'success': False,
                'message': '用户不存在'
            }, status=status.HTTP_404_NOT_FOUND)
        
        if request.user == target_user:
            return Response({
                'success': False,
                'message': '不能关注自己'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        follow, created = UserFollow.objects.get_or_create(
            follower=request.user,
            following=target_user
        )
        
        if created:
            # 更新关注数
            request.user.following_count += 1
            target_user.followers_count += 1
            request.user.save()
            target_user.save()
            
            return Response({
                'success': True,
                'message': '关注成功',
                'is_following': True
            })
        else:
            # 取消关注
            follow.delete()
            
            # 更新关注数
            request.user.following_count -= 1
            target_user.followers_count -= 1
            request.user.save()
            target_user.save()
            
            return Response({
                'success': True,
                'message': '取消关注成功',
                'is_following': False
            })


class UserSearchView(APIView):
    """用户搜索视图"""
    
    def get(self, request):
        query = request.GET.get('q', '').strip()
        if not query:
            return Response({
                'success': False,
                'message': '请输入搜索关键词'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        users = User.objects.filter(
            models.Q(username__icontains=query) |
            models.Q(nickname__icontains=query)
        )[:20]
        
        serializer = UserSerializer(users, many=True)
        return Response({
            'success': True,
            'users': serializer.data
        })


class UserViewSet(viewsets.ModelViewSet):
    """用户视图集"""
    
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    
    @action(detail=True, methods=['get'])
    def followers(self, request, pk=None):
        """获取用户的粉丝列表"""
        user = self.get_object()
        followers = user.followers.all()
        serializer = UserSerializer(followers, many=True)
        return Response({
            'success': True,
            'followers': serializer.data
        })
    
    @action(detail=True, methods=['get'])
    def following(self, request, pk=None):
        """获取用户的关注列表"""
        user = self.get_object()
        following = user.following.all()
        serializer = UserSerializer(following, many=True)
        return Response({
            'success': True,
            'following': serializer.data
        })
    
    @action(detail=True, methods=['get'])
    def tiebas(self, request, pk=None):
        """获取用户加入的贴吧列表"""
        user = self.get_object()
        tiebas = user.tieba_memberships.all()
        from tiebas.serializers import TiebaMemberSerializer
        serializer = TiebaMemberSerializer(tiebas, many=True)
        return Response({
            'success': True,
            'tiebas': serializer.data
        })


class UserFollowersView(APIView):
    """用户粉丝列表视图"""
    
    def get(self, request, user_id):
        try:
            user = User.objects.get(id=user_id)
        except User.DoesNotExist:
            return Response({
                'success': False,
                'message': '用户不存在'
            }, status=status.HTTP_404_NOT_FOUND)
        
        followers = user.followers.all()
        serializer = UserSerializer([f.follower for f in followers], many=True)
        
        return Response({
            'success': True,
            'followers': serializer.data,
            'count': followers.count()
        })


class UserFollowingView(APIView):
    """用户关注列表视图"""
    
    def get(self, request, user_id):
        try:
            user = User.objects.get(id=user_id)
        except User.DoesNotExist:
            return Response({
                'success': False,
                'message': '用户不存在'
            }, status=status.HTTP_404_NOT_FOUND)
        
        following = user.following.all()
        serializer = UserSerializer([f.following for f in following], many=True)
        
        return Response({
            'success': True,
            'following': serializer.data,
            'count': following.count()
        })


class UserPasswordChangeView(APIView):
    """用户密码修改视图"""
    
    def post(self, request):
        user = request.user
        
        # 验证当前密码
        current_password = request.data.get('current_password')
        if not user.check_password(current_password):
            return Response({
                'success': False,
                'message': '当前密码错误'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # 验证新密码
        new_password = request.data.get('new_password')
        confirm_password = request.data.get('confirm_password')
        
        if not new_password or not confirm_password:
            return Response({
                'success': False,
                'message': '新密码和确认密码不能为空'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        if new_password != confirm_password:
            return Response({
                'success': False,
                'message': '新密码和确认密码不一致'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        if len(new_password) < 6:
            return Response({
                'success': False,
                'message': '密码长度不能少于6位'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # 设置新密码
        user.set_password(new_password)
        user.save()
        
        return Response({
            'success': True,
            'message': '密码修改成功'
        })