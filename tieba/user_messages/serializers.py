"""
User messages serializers for tieba project.
"""

from rest_framework import serializers
from .models import Message, Notification, MessageSession, NotificationSettings
from users.serializers import UserSerializer


class MessageSerializer(serializers.ModelSerializer):
    """私信序列化器"""
    
    sender_info = UserSerializer(source='sender', read_only=True)
    receiver_info = UserSerializer(source='receiver', read_only=True)
    
    class Meta:
        model = Message
        fields = [
            'id', 'session', 'sender', 'sender_info', 'receiver', 'receiver_info',
            'content', 'message_type', 'is_read', 'created_at'
        ]
        read_only_fields = ['id', 'created_at']


class MessageCreateSerializer(serializers.ModelSerializer):
    """私信创建序列化器"""
    
    class Meta:
        model = Message
        fields = ['receiver', 'content', 'message_type']
    
    def create(self, validated_data):
        request = self.context.get('request')
        receiver = validated_data['receiver']
        
        # 获取或创建会话
        session = MessageSession.objects.filter(
            participants=request.user
        ).filter(
            participants=receiver
        ).first()
        
        if not session:
            session = MessageSession.objects.create()
            session.participants.add(request.user, receiver)
        
        validated_data['sender'] = request.user
        validated_data['session'] = session
        
        return super().create(validated_data)


class NotificationSerializer(serializers.ModelSerializer):
    """系统通知序列化器"""
    
    sender_info = UserSerializer(source='sender', read_only=True)
    
    class Meta:
        model = Notification
        fields = [
            'id', 'recipient', 'sender', 'sender_info', 'notification_type',
            'title', 'content', 'related_object_type', 'related_object_id',
            'is_read', 'created_at'
        ]
        read_only_fields = ['id', 'created_at']


class MessageSessionSerializer(serializers.ModelSerializer):
    """消息会话序列化器"""
    
    participants_info = UserSerializer(source='participants', many=True, read_only=True)
    last_message = serializers.SerializerMethodField()
    unread_count = serializers.SerializerMethodField()
    
    class Meta:
        model = MessageSession
        fields = [
            'id', 'participants', 'participants_info', 'last_message',
            'unread_count', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']
    
    def get_last_message(self, obj):
        last_message = obj.messages.order_by('-created_at').first()
        if last_message:
            return MessageSerializer(last_message).data
        return None
    
    def get_unread_count(self, obj):
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            return obj.messages.filter(
                receiver=request.user, is_read=False
            ).count()
        return 0


class NotificationSettingsSerializer(serializers.ModelSerializer):
    """通知设置序列化器"""
    
    class Meta:
        model = NotificationSettings
        fields = [
            'id', 'user', 'enable_private_message', 'enable_system_notification',
            'enable_like_notification', 'enable_comment_notification',
            'enable_follow_notification', 'enable_tieba_notification',
            'email_notification', 'push_notification', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'user', 'created_at', 'updated_at']


class ConversationSerializer(serializers.Serializer):
    """对话序列化器"""
    
    session = MessageSessionSerializer()
    messages = MessageSerializer(many=True)


class NotificationListSerializer(serializers.ModelSerializer):
    """通知列表序列化器"""
    
    sender_info = UserSerializer(source='sender', read_only=True)
    
    class Meta:
        model = Notification
        fields = [
            'id', 'sender', 'sender_info', 'notification_type',
            'title', 'content', 'is_read', 'created_at'
        ]
        read_only_fields = ['id', 'created_at']


class MessageListSerializer(serializers.ModelSerializer):
    """消息列表序列化器"""
    
    sender_info = UserSerializer(source='sender', read_only=True)
    receiver_info = UserSerializer(source='receiver', read_only=True)
    
    class Meta:
        model = Message
        fields = [
            'id', 'sender', 'sender_info', 'receiver', 'receiver_info',
            'content', 'message_type', 'is_read', 'created_at'
        ]
        read_only_fields = ['id', 'created_at']