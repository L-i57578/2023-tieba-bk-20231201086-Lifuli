"""
Tieba serializers for tieba project.
"""

from rest_framework import serializers
from .models import TiebaCategory, Tieba, TiebaMember, TiebaFollow
from users.serializers import UserSerializer


class TiebaCategorySerializer(serializers.ModelSerializer):
    """贴吧分类序列化器"""
    
    class Meta:
        model = TiebaCategory
        fields = ['id', 'name', 'description', 'icon', 'created_at']
        read_only_fields = ['id', 'created_at']


class TiebaSerializer(serializers.ModelSerializer):
    """贴吧序列化器"""
    
    category_name = serializers.CharField(source='category.name', read_only=True)
    owner_username = serializers.CharField(source='owner.username', read_only=True)
    
    class Meta:
        model = Tieba
        fields = [
            'id', 'name', 'description', 'avatar', 'banner', 'category', 'category_name',
            'owner', 'owner_username', 'rules', 'tags', 'member_count', 'post_count',
            'today_post_count', 'is_private', 'is_official', 'status', 'created_at', 'updated_at'
        ]
        read_only_fields = [
            'id', 'member_count', 'post_count', 'today_post_count', 'created_at', 'updated_at'
        ]
    
    def to_representation(self, instance):
        data = super().to_representation(instance)
        
        # 处理图片URL
        if instance.avatar:
            data['avatar'] = instance.avatar.url
        else:
            data['avatar'] = None
            
        if instance.banner:
            data['banner'] = instance.banner.url
        else:
            data['banner'] = None
        
        return data


class TiebaCreateSerializer(serializers.ModelSerializer):
    """贴吧创建序列化器"""
    
    class Meta:
        model = Tieba
        fields = ['name', 'description', 'avatar', 'banner', 'category', 'rules', 'tags']
    
    def validate_name(self, value):
        if Tieba.objects.filter(name=value).exists():
            raise serializers.ValidationError('贴吧名称已存在')
        return value


class TiebaMemberSerializer(serializers.ModelSerializer):
    """贴吧成员序列化器"""
    
    user_info = UserSerializer(source='user', read_only=True)
    tieba_name = serializers.CharField(source='tieba.name', read_only=True)
    
    class Meta:
        model = TiebaMember
        fields = [
            'id', 'user', 'user_info', 'tieba', 'tieba_name', 'role',
            'level', 'experience', 'joined_at', 'last_active_at'
        ]
        read_only_fields = ['id', 'joined_at', 'last_active_at']


class TiebaFollowSerializer(serializers.ModelSerializer):
    """贴吧关注序列化器"""
    
    user_info = UserSerializer(source='user', read_only=True)
    tieba_info = TiebaSerializer(source='tieba', read_only=True)
    
    class Meta:
        model = TiebaFollow
        fields = ['id', 'user', 'user_info', 'tieba', 'tieba_info', 'created_at']
        read_only_fields = ['id', 'created_at']


class TiebaDetailSerializer(serializers.ModelSerializer):
    """贴吧详情序列化器"""
    
    category_name = serializers.CharField(source='category.name', read_only=True)
    owner_info = UserSerializer(source='owner', read_only=True)
    is_member = serializers.SerializerMethodField()
    is_following = serializers.SerializerMethodField()
    member_role = serializers.SerializerMethodField()
    
    class Meta:
        model = Tieba
        fields = [
            'id', 'name', 'description', 'avatar', 'banner', 'category', 'category_name',
            'owner', 'owner_info', 'rules', 'tags', 'member_count', 'post_count',
            'today_post_count', 'is_private', 'is_official', 'status',
            'is_member', 'is_following', 'member_role', 'created_at', 'updated_at'
        ]
        read_only_fields = [
            'id', 'member_count', 'post_count', 'today_post_count', 'created_at', 'updated_at'
        ]
    
    def get_is_member(self, obj):
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            return TiebaMember.objects.filter(
                tieba=obj, user=request.user
            ).exists()
        return False
    
    def get_is_following(self, obj):
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            return TiebaFollow.objects.filter(
                tieba=obj, user=request.user
            ).exists()
        return False
    
    def get_member_role(self, obj):
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            member = TiebaMember.objects.filter(
                tieba=obj, user=request.user
            ).first()
            return member.role if member else None
        return None