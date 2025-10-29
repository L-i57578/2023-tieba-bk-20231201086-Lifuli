"""
Tieba models for tieba project.
"""

from django.db import models
from django.contrib.auth import get_user_model

User = get_user_model()


class TiebaCategory(models.Model):
    """贴吧分类模型"""
    
    name = models.CharField(max_length=50, unique=True, verbose_name='分类名称')
    description = models.TextField(max_length=200, blank=True, verbose_name='分类描述')
    icon = models.CharField(max_length=50, blank=True, verbose_name='分类图标')
    sort_order = models.PositiveIntegerField(default=0, verbose_name='排序')
    is_active = models.BooleanField(default=True, verbose_name='是否启用')
    
    class Meta:
        verbose_name = '贴吧分类'
        verbose_name_plural = '贴吧分类'
        ordering = ['sort_order', 'id']
    
    def __str__(self):
        return self.name


class Tieba(models.Model):
    """贴吧模型"""
    
    name = models.CharField(max_length=50, unique=True, verbose_name='贴吧名称')
    description = models.TextField(max_length=500, blank=True, verbose_name='贴吧描述')
    avatar = models.ImageField(upload_to='tieba_avatars/', blank=True, null=True, verbose_name='贴吧头像')
    banner = models.ImageField(upload_to='tieba_banners/', blank=True, null=True, verbose_name='贴吧横幅')
    
    # 分类信息
    category = models.ForeignKey(
        TiebaCategory, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True,
        related_name='tiebas',
        verbose_name='所属分类'
    )
    
    # 创建者和管理员
    creator = models.ForeignKey(
        User, 
        on_delete=models.CASCADE, 
        related_name='created_tiebas',
        verbose_name='创建者'
    )
    admins = models.ManyToManyField(
        User, 
        related_name='managed_tiebas',
        blank=True,
        verbose_name='管理员'
    )
    
    # 统计信息
    members_count = models.PositiveIntegerField(default=0, verbose_name='成员数')
    posts_count = models.PositiveIntegerField(default=0, verbose_name='帖子数')
    today_posts_count = models.PositiveIntegerField(default=0, verbose_name='今日帖子数')
    
    # 贴吧设置
    is_public = models.BooleanField(default=True, verbose_name='是否公开')
    join_need_approve = models.BooleanField(default=False, verbose_name='加入需要审核')
    post_need_approve = models.BooleanField(default=False, verbose_name='发帖需要审核')
    
    # 时间戳
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='更新时间')
    
    class Meta:
        verbose_name = '贴吧'
        verbose_name_plural = '贴吧'
        ordering = ['-members_count', '-created_at']
    
    def __str__(self):
        return self.name


class TiebaMember(models.Model):
    """贴吧成员模型"""
    
    ROLE_CHOICES = [
        ('member', '普通成员'),
        ('admin', '管理员'),
        ('owner', '吧主'),
    ]
    
    tieba = models.ForeignKey(
        Tieba, 
        on_delete=models.CASCADE, 
        related_name='members',
        verbose_name='贴吧'
    )
    user = models.ForeignKey(
        User, 
        on_delete=models.CASCADE, 
        related_name='tieba_memberships',
        verbose_name='用户'
    )
    role = models.CharField(
        max_length=10, 
        choices=ROLE_CHOICES, 
        default='member',
        verbose_name='角色'
    )
    
    # 成员信息
    nickname_in_tieba = models.CharField(max_length=50, blank=True, verbose_name='贴吧内昵称')
    level = models.PositiveIntegerField(default=1, verbose_name='等级')
    experience = models.PositiveIntegerField(default=0, verbose_name='经验值')
    
    # 时间戳
    joined_at = models.DateTimeField(auto_now_add=True, verbose_name='加入时间')
    last_active_at = models.DateTimeField(auto_now=True, verbose_name='最后活跃时间')
    
    class Meta:
        verbose_name = '贴吧成员'
        verbose_name_plural = '贴吧成员'
        unique_together = ('tieba', 'user')
    
    def __str__(self):
        return f'{self.user} 在 {self.tieba}'


class TiebaFollow(models.Model):
    """用户关注贴吧模型"""
    
    user = models.ForeignKey(
        User, 
        on_delete=models.CASCADE, 
        related_name='tieba_follows',
        verbose_name='用户'
    )
    tieba = models.ForeignKey(
        Tieba, 
        on_delete=models.CASCADE, 
        related_name='followers',
        verbose_name='贴吧'
    )
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='关注时间')
    
    class Meta:
        verbose_name = '贴吧关注'
        verbose_name_plural = '贴吧关注'
        unique_together = ('user', 'tieba')
    
    def __str__(self):
        return f'{self.user} 关注 {self.tieba}'