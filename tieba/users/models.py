"""
User models for tieba project.
"""

from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    """Custom user model for tieba."""
    
    # 基本信息
    nickname = models.CharField(max_length=50, blank=True, verbose_name='昵称')
    avatar = models.ImageField(upload_to='avatars/', blank=True, null=True, verbose_name='头像')
    bio = models.TextField(max_length=500, blank=True, verbose_name='个人简介')
    
    # 联系方式
    phone = models.CharField(max_length=15, blank=True, verbose_name='手机号')
    email = models.EmailField(blank=True, verbose_name='邮箱')
    website = models.URLField(blank=True, verbose_name='个人网站')
    
    # 社交账号
    weibo = models.CharField(max_length=100, blank=True, verbose_name='微博')
    wechat = models.CharField(max_length=100, blank=True, verbose_name='微信')
    qq = models.CharField(max_length=20, blank=True, verbose_name='QQ')
    instagram = models.CharField(max_length=100, blank=True, verbose_name='Instagram')
    
    # 个人资料
    gender = models.CharField(max_length=10, choices=[
        ('male', '男'),
        ('female', '女'),
        ('other', '其他')
    ], blank=True, verbose_name='性别')
    birthday = models.DateField(null=True, blank=True, verbose_name='生日')
    location = models.CharField(max_length=100, blank=True, verbose_name='地区')
    
    # 兴趣爱好
    interests = models.TextField(max_length=500, blank=True, verbose_name='兴趣爱好')
    
    # 统计信息
    followers_count = models.PositiveIntegerField(default=0, verbose_name='粉丝数')
    following_count = models.PositiveIntegerField(default=0, verbose_name='关注数')
    posts_count = models.PositiveIntegerField(default=0, verbose_name='帖子数')
    likes_count = models.PositiveIntegerField(default=0, verbose_name='获赞数')
    
    # 时间戳
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='更新时间')
    
    class Meta:
        verbose_name = '用户'
        verbose_name_plural = '用户'
    
    def __str__(self):
        return self.nickname or self.username
    
    def save(self, *args, **kwargs):
        # 如果没有设置昵称，使用用户名作为昵称
        if not self.nickname:
            self.nickname = self.username
        super().save(*args, **kwargs)


class UserFollow(models.Model):
    """用户关注关系模型"""
    
    follower = models.ForeignKey(
        User, 
        on_delete=models.CASCADE, 
        related_name='following',
        verbose_name='关注者'
    )
    following = models.ForeignKey(
        User, 
        on_delete=models.CASCADE, 
        related_name='followers',
        verbose_name='被关注者'
    )
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='关注时间')
    
    class Meta:
        verbose_name = '用户关注'
        verbose_name_plural = '用户关注'
        unique_together = ('follower', 'following')
    
    def __str__(self):
        return f'{self.follower} 关注 {self.following}'