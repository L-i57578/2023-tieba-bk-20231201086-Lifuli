"""
User messages models for tieba project.
"""

from django.db import models
from django.contrib.auth import get_user_model

User = get_user_model()


class Message(models.Model):
    """私信消息模型"""
    
    MESSAGE_TYPE_CHOICES = [
        ('text', '文本消息'),
        ('image', '图片消息'),
        ('system', '系统消息'),
    ]
    
    sender = models.ForeignKey(
        User, 
        on_delete=models.CASCADE, 
        related_name='sent_messages',
        verbose_name='发送者'
    )
    receiver = models.ForeignKey(
        User, 
        on_delete=models.CASCADE, 
        related_name='received_messages',
        verbose_name='接收者'
    )
    
    # 消息内容
    message_type = models.CharField(
        max_length=10, 
        choices=MESSAGE_TYPE_CHOICES, 
        default='text',
        verbose_name='消息类型'
    )
    content = models.TextField(verbose_name='消息内容')
    image = models.ImageField(upload_to='message_images/', blank=True, null=True, verbose_name='图片')
    
    # 消息状态
    is_read = models.BooleanField(default=False, verbose_name='是否已读')
    is_deleted_by_sender = models.BooleanField(default=False, verbose_name='发送者删除')
    is_deleted_by_receiver = models.BooleanField(default=False, verbose_name='接收者删除')
    
    # 时间戳
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='发送时间')
    read_at = models.DateTimeField(null=True, blank=True, verbose_name='阅读时间')
    
    class Meta:
        verbose_name = '私信消息'
        verbose_name_plural = '私信消息'
        ordering = ['-created_at']
    
    def __str__(self):
        return f'{self.sender} -> {self.receiver}: {self.content[:50]}'


class Notification(models.Model):
    """系统通知模型"""
    
    NOTIFICATION_TYPE_CHOICES = [
        ('reply', '回复我的'),
        ('mention', '@我的'),
        ('like', '点赞我的'),
        ('follow', '关注我的'),
        ('system', '系统通知'),
        ('tieba', '贴吧通知'),
    ]
    
    user = models.ForeignKey(
        User, 
        on_delete=models.CASCADE, 
        related_name='notifications',
        verbose_name='接收用户'
    )
    
    # 通知内容
    notification_type = models.CharField(
        max_length=10, 
        choices=NOTIFICATION_TYPE_CHOICES, 
        verbose_name='通知类型'
    )
    title = models.CharField(max_length=200, verbose_name='通知标题')
    content = models.TextField(verbose_name='通知内容')
    
    # 关联对象
    related_post = models.ForeignKey(
        'posts.Post', 
        on_delete=models.CASCADE, 
        null=True, 
        blank=True,
        related_name='notifications',
        verbose_name='关联帖子'
    )
    related_comment = models.ForeignKey(
        'posts.Comment', 
        on_delete=models.CASCADE, 
        null=True, 
        blank=True,
        related_name='notifications',
        verbose_name='关联评论'
    )
    related_user = models.ForeignKey(
        User, 
        on_delete=models.CASCADE, 
        null=True, 
        blank=True,
        related_name='triggered_notifications',
        verbose_name='关联用户'
    )
    
    # 通知状态
    is_read = models.BooleanField(default=False, verbose_name='是否已读')
    is_deleted = models.BooleanField(default=False, verbose_name='是否删除')
    
    # 时间戳
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
    read_at = models.DateTimeField(null=True, blank=True, verbose_name='阅读时间')
    
    class Meta:
        verbose_name = '系统通知'
        verbose_name_plural = '系统通知'
        ordering = ['-created_at']
    
    def __str__(self):
        return f'{self.user}: {self.title}'


class MessageSession(models.Model):
    """消息会话模型"""
    
    user1 = models.ForeignKey(
        User, 
        on_delete=models.CASCADE, 
        related_name='message_sessions_as_user1',
        verbose_name='用户1'
    )
    user2 = models.ForeignKey(
        User, 
        on_delete=models.CASCADE, 
        related_name='message_sessions_as_user2',
        verbose_name='用户2'
    )
    
    # 会话信息
    unread_count_user1 = models.PositiveIntegerField(default=0, verbose_name='用户1未读消息数')
    unread_count_user2 = models.PositiveIntegerField(default=0, verbose_name='用户2未读消息数')
    last_message = models.ForeignKey(
        Message, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True,
        related_name='session_last_message',
        verbose_name='最后一条消息'
    )
    
    # 时间戳
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='更新时间')
    
    class Meta:
        verbose_name = '消息会话'
        verbose_name_plural = '消息会话'
        unique_together = ('user1', 'user2')
        ordering = ['-updated_at']
    
    def __str__(self):
        return f'{self.user1} 和 {self.user2} 的会话'


class NotificationSettings(models.Model):
    """用户通知设置模型"""
    
    user = models.OneToOneField(
        User, 
        on_delete=models.CASCADE, 
        related_name='notification_settings',
        verbose_name='用户'
    )
    
    # 通知开关
    email_notifications = models.BooleanField(default=True, verbose_name='邮件通知')
    push_notifications = models.BooleanField(default=True, verbose_name='推送通知')
    
    # 具体通知类型设置
    notify_on_reply = models.BooleanField(default=True, verbose_name='回复通知')
    notify_on_mention = models.BooleanField(default=True, verbose_name='@我通知')
    notify_on_like = models.BooleanField(default=True, verbose_name='点赞通知')
    notify_on_follow = models.BooleanField(default=True, verbose_name='关注通知')
    notify_on_system = models.BooleanField(default=True, verbose_name='系统通知')
    notify_on_tieba = models.BooleanField(default=True, verbose_name='贴吧通知')
    
    # 时间戳
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='更新时间')
    
    class Meta:
        verbose_name = '通知设置'
        verbose_name_plural = '通知设置'
    
    def __str__(self):
        return f'{self.user} 的通知设置'