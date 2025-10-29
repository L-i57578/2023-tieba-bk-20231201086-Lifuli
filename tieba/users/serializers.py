"""
User serializers for tieba project.
"""

from django.contrib.auth import authenticate
from django.contrib.auth.password_validation import validate_password
from rest_framework import serializers
from rest_framework.validators import UniqueValidator
from .models import User


class UserRegistrationSerializer(serializers.ModelSerializer):
    """用户注册序列化器"""
    
    password = serializers.CharField(
        write_only=True,
        required=True,
        validators=[validate_password],
        style={'input_type': 'password'}
    )
    password2 = serializers.CharField(
        write_only=True,
        required=True,
        style={'input_type': 'password'}
    )
    
    class Meta:
        model = User
        fields = [
            'username', 'password', 'password2', 'email', 'phone',
            'nickname', 'gender', 'birthday', 'location', 'bio'
        ]
        extra_kwargs = {
            'username': {
                'validators': [UniqueValidator(queryset=User.objects.all())]
            },
            'email': {
                'validators': [UniqueValidator(queryset=User.objects.all())]
            },
            'phone': {
                'validators': [UniqueValidator(queryset=User.objects.all())]
            }
        }
    
    def validate(self, attrs):
        if attrs['password'] != attrs['password2']:
            raise serializers.ValidationError({"password": "两次输入的密码不一致"})
        return attrs
    
    def create(self, validated_data):
        validated_data.pop('password2')
        user = User.objects.create_user(**validated_data)
        return user


class UserLoginSerializer(serializers.Serializer):
    """用户登录序列化器"""
    
    username = serializers.CharField(required=True)
    password = serializers.CharField(
        required=True,
        style={'input_type': 'password'}
    )
    remember = serializers.BooleanField(default=False, required=False)
    
    def validate(self, attrs):
        username = attrs.get('username')
        password = attrs.get('password')
        
        if username and password:
            user = authenticate(username=username, password=password)
            if not user:
                raise serializers.ValidationError('用户名或密码错误')
            attrs['user'] = user
        else:
            raise serializers.ValidationError('用户名和密码不能为空')
        
        return attrs


class UserSerializer(serializers.ModelSerializer):
    """用户信息序列化器"""
    
    class Meta:
        model = User
        fields = [
            'id', 'username', 'nickname', 'avatar', 'bio',
            'email', 'phone', 'website', 'gender', 'birthday', 'location',
            'weibo', 'wechat', 'qq', 'instagram', 'interests',
            'followers_count', 'following_count', 'posts_count', 'likes_count',
            'created_at', 'updated_at'
        ]
        read_only_fields = [
            'id', 'followers_count', 'following_count', 'posts_count', 'likes_count',
            'created_at', 'updated_at'
        ]
    
    def to_representation(self, instance):
        data = super().to_representation(instance)
        
        # 处理头像URL
        if instance.avatar:
            data['avatar'] = instance.avatar.url
        else:
            data['avatar'] = None
        
        # 处理日期格式
        if instance.birthday:
            data['birthday'] = instance.birthday.strftime('%Y-%m-%d')
        
        return data


class UserProfileUpdateSerializer(serializers.ModelSerializer):
    """用户资料更新序列化器"""
    
    class Meta:
        model = User
        fields = [
            'nickname', 'avatar', 'bio', 'email', 'phone', 'website',
            'gender', 'birthday', 'location', 'weibo', 'wechat', 'qq',
            'instagram', 'interests'
        ]
    
    def validate_email(self, value):
        if value and User.objects.filter(email=value).exclude(id=self.instance.id).exists():
            raise serializers.ValidationError('该邮箱已被使用')
        return value
    
    def validate_phone(self, value):
        if value and User.objects.filter(phone=value).exclude(id=self.instance.id).exists():
            raise serializers.ValidationError('该手机号已被使用')
        return value


class UserPasswordChangeSerializer(serializers.Serializer):
    """用户密码修改序列化器"""
    
    old_password = serializers.CharField(required=True, style={'input_type': 'password'})
    new_password = serializers.CharField(
        required=True,
        validators=[validate_password],
        style={'input_type': 'password'}
    )
    new_password2 = serializers.CharField(required=True, style={'input_type': 'password'})
    
    def validate_old_password(self, value):
        user = self.context['request'].user
        if not user.check_password(value):
            raise serializers.ValidationError('原密码错误')
        return value
    
    def validate(self, attrs):
        if attrs['new_password'] != attrs['new_password2']:
            raise serializers.ValidationError({"new_password": "两次输入的新密码不一致"})
        return attrs


class UserFollowSerializer(serializers.ModelSerializer):
    """用户关注序列化器"""
    
    follower = UserSerializer(read_only=True)
    following = UserSerializer(read_only=True)
    
    class Meta:
        model = User
        fields = ['follower', 'following', 'created_at']