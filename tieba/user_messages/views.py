"""
User messages views for tieba project.
"""

from django.db.models import Q
from rest_framework import viewsets, status, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.views import APIView
from .models import Message, Notification, MessageSession, NotificationSettings
from .serializers import (
    MessageSerializer, MessageCreateSerializer, NotificationSerializer,
    MessageSessionSerializer, NotificationSettingsSerializer,
    ConversationSerializer, NotificationListSerializer, MessageListSerializer
)


class MessageViewSet(viewsets.ModelViewSet):
    """私信视图集"""
    
    queryset = Message.objects.all()
    permission_classes = [permissions.IsAuthenticated]
    
    def get_serializer_class(self):
        if self.action == 'create':
            return MessageCreateSerializer
        return MessageSerializer
    
    def get_queryset(self):
        # 用户只能看到自己发送或接收的消息
        return self.queryset.filter(
            Q(sender=self.request.user) | Q(receiver=self.request.user)
        ).order_by('-created_at')
    
    @action(detail=True, methods=['post'])
    def mark_read(self, request, pk=None):
        """标记消息为已读"""
        message = self.get_object()
        
        if message.receiver != request.user:
            return Response(
                {'error': '没有权限操作此消息'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        message.is_read = True
        message.save()
        
        serializer = self.get_serializer(message)
        return Response(serializer.data)
    
    @action(detail=False, methods=['post'])
    def mark_all_read(self, request):
        """标记所有消息为已读"""
        Message.objects.filter(receiver=request.user, is_read=False).update(is_read=True)
        return Response({'message': '所有消息已标记为已读'})


class MessageSessionViewSet(viewsets.ModelViewSet):
    """消息会话视图集"""
    
    queryset = MessageSession.objects.all()
    serializer_class = MessageSessionSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        # 用户只能看到自己参与的会话
        return self.queryset.filter(participants=self.request.user).order_by('-updated_at')
    
    @action(detail=True, methods=['get'])
    def messages(self, request, pk=None):
        """获取会话中的消息"""
        session = self.get_object()
        
        # 检查用户是否有权限访问此会话
        if request.user not in session.participants.all():
            return Response(
                {'error': '没有权限访问此会话'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        messages = session.messages.all().order_by('created_at')
        serializer = MessageListSerializer(messages, many=True)
        
        # 标记会话中的未读消息为已读
        session.messages.filter(receiver=request.user, is_read=False).update(is_read=True)
        
        return Response(serializer.data)
    
    @action(detail=True, methods=['post'])
    def send_message(self, request, pk=None):
        """在会话中发送消息"""
        session = self.get_object()
        
        # 检查用户是否有权限在此会话中发送消息
        if request.user not in session.participants.all():
            return Response(
                {'error': '没有权限在此会话中发送消息'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        # 获取接收者（会话中的另一个参与者）
        receiver = session.participants.exclude(id=request.user.id).first()
        if not receiver:
            return Response(
                {'error': '会话参与者无效'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        serializer = MessageCreateSerializer(
            data=request.data,
            context={'request': request}
        )
        
        if serializer.is_valid():
            # 设置会话和接收者
            serializer.validated_data['session'] = session
            serializer.validated_data['receiver'] = receiver
            message = serializer.save()
            
            # 更新会话时间
            session.save()
            
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class NotificationViewSet(viewsets.ModelViewSet):
    """系统通知视图集"""
    
    queryset = Notification.objects.all()
    serializer_class = NotificationSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        # 用户只能看到自己的通知
        return self.queryset.filter(recipient=self.request.user).order_by('-created_at')
    
    def get_serializer_class(self):
        if self.action == 'list':
            return NotificationListSerializer
        return NotificationSerializer
    
    @action(detail=True, methods=['post'])
    def mark_read(self, request, pk=None):
        """标记通知为已读"""
        notification = self.get_object()
        
        if notification.recipient != request.user:
            return Response(
                {'error': '没有权限操作此通知'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        notification.is_read = True
        notification.save()
        
        serializer = self.get_serializer(notification)
        return Response(serializer.data)
    
    @action(detail=False, methods=['post'])
    def mark_all_read(self, request):
        """标记所有通知为已读"""
        Notification.objects.filter(recipient=request.user, is_read=False).update(is_read=True)
        return Response({'message': '所有通知已标记为已读'})
    
    @action(detail=False, methods=['get'])
    def unread_count(self, request):
        """获取未读通知数量"""
        count = Notification.objects.filter(
            recipient=request.user, is_read=False
        ).count()
        return Response({'unread_count': count})


class NotificationSettingsViewSet(viewsets.ModelViewSet):
    """通知设置视图集"""
    
    queryset = NotificationSettings.objects.all()
    serializer_class = NotificationSettingsSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        # 用户只能看到自己的设置
        return self.queryset.filter(user=self.request.user)
    
    def perform_create(self, serializer):
        # 确保每个用户只有一个设置记录
        if NotificationSettings.objects.filter(user=self.request.user).exists():
            return Response(
                {'error': '通知设置已存在'},
                status=status.HTTP_400_BAD_REQUEST
            )
        serializer.save(user=self.request.user)


class ConversationView(APIView):
    """对话视图"""
    
    permission_classes = [permissions.IsAuthenticated]
    
    def get(self, request, user_id):
        """获取与指定用户的对话"""
        from users.models import User
        
        try:
            other_user = User.objects.get(id=user_id)
        except User.DoesNotExist:
            return Response(
                {'error': '用户不存在'},
                status=status.HTTP_404_NOT_FOUND
            )
        
        # 获取或创建会话
        session = MessageSession.objects.filter(
            participants=request.user
        ).filter(
            participants=other_user
        ).first()
        
        if not session:
            session = MessageSession.objects.create()
            session.participants.add(request.user, other_user)
        
        # 获取会话中的消息
        messages = session.messages.all().order_by('created_at')
        
        session_serializer = MessageSessionSerializer(session)
        messages_serializer = MessageListSerializer(messages, many=True)
        
        # 标记未读消息为已读
        session.messages.filter(receiver=request.user, is_read=False).update(is_read=True)
        
        return Response({
            'session': session_serializer.data,
            'messages': messages_serializer.data
        })


class MessageStatsView(APIView):
    """消息统计视图"""
    
    permission_classes = [permissions.IsAuthenticated]
    
    def get(self, request):
        """获取消息统计信息"""
        # 未读私信数量
        unread_messages_count = Message.objects.filter(
            receiver=request.user, is_read=False
        ).count()
        
        # 未读通知数量
        unread_notifications_count = Notification.objects.filter(
            recipient=request.user, is_read=False
        ).count()
        
        # 会话数量
        sessions_count = MessageSession.objects.filter(participants=request.user).count()
        
        return Response({
            'unread_messages_count': unread_messages_count,
            'unread_notifications_count': unread_notifications_count,
            'sessions_count': sessions_count
        })