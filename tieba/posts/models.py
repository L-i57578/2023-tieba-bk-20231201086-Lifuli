"""
Post models for tieba project.
"""

from django.db import models
from django.contrib.auth import get_user_model

User = get_user_model()


class Post(models.Model):
    """帖子模型"""
    
    POST_TYPE_CHOICES = [
        ('normal', '普通帖子'),
        ('sticky', '置顶帖子'),
        ('essence', '精华帖子'),
        ('announcement', '公告'),
    ]
    
    title = models.CharField(max_length=200, verbose_name='帖子标题')
    content = models.TextField(verbose_name='帖子内容')
    
    # 关联信息
    author = models.ForeignKey(
        User, 
        on_delete=models.CASCADE, 
        related_name='posts',
        verbose_name='作者'
    )
    tieba = models.ForeignKey(
        'tiebas.Tieba', 
        on_delete=models.CASCADE, 
        related_name='posts',
        verbose_name='所属贴吧'
    )
    
    # 帖子类型和状态
    post_type = models.CharField(
        max_length=20, 
        choices=POST_TYPE_CHOICES, 
        default='normal',
        verbose_name='帖子类型'
    )
    is_published = models.BooleanField(default=True, verbose_name='是否发布')
    is_deleted = models.BooleanField(default=False, verbose_name='是否删除')
    
    # 统计信息
    views_count = models.PositiveIntegerField(default=0, verbose_name='浏览数')
    likes_count = models.PositiveIntegerField(default=0, verbose_name='点赞数')
    comments_count = models.PositiveIntegerField(default=0, verbose_name='评论数')
    shares_count = models.PositiveIntegerField(default=0, verbose_name='分享数')
    
    # 标签和分类
    tags = models.CharField(max_length=200, blank=True, verbose_name='标签')
    
    # 时间戳
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='更新时间')
    last_reply_at = models.DateTimeField(auto_now_add=True, verbose_name='最后回复时间')
    
    class Meta:
        verbose_name = '帖子'
        verbose_name_plural = '帖子'
        ordering = ['-last_reply_at', '-created_at']
        indexes = [
            models.Index(fields=['tieba', 'post_type', 'is_published']),
            models.Index(fields=['author', 'created_at']),
        ]
    
    def __str__(self):
        return self.title


class PostImage(models.Model):
    """帖子图片模型"""
    
    post = models.ForeignKey(
        Post, 
        on_delete=models.CASCADE, 
        related_name='images',
        verbose_name='帖子'
    )
    image = models.ImageField(upload_to='post_images/', verbose_name='图片')
    caption = models.CharField(max_length=100, blank=True, verbose_name='图片说明')
    sort_order = models.PositiveIntegerField(default=0, verbose_name='排序')
    
    class Meta:
        verbose_name = '帖子图片'
        verbose_name_plural = '帖子图片'
        ordering = ['sort_order', 'id']
    
    def __str__(self):
        return f'{self.post.title} - 图片 {self.id}'


class Comment(models.Model):
    """评论模型"""
    
    post = models.ForeignKey(
        Post, 
        on_delete=models.CASCADE, 
        related_name='comments',
        verbose_name='帖子'
    )
    author = models.ForeignKey(
        User, 
        on_delete=models.CASCADE, 
        related_name='comments',
        verbose_name='评论者'
    )
    content = models.TextField(verbose_name='评论内容')
    
    # 回复功能
    parent = models.ForeignKey(
        'self', 
        on_delete=models.CASCADE, 
        null=True, 
        blank=True,
        related_name='replies',
        verbose_name='父评论'
    )
    reply_to = models.ForeignKey(
        User, 
        on_delete=models.CASCADE, 
        null=True, 
        blank=True,
        related_name='replied_comments',
        verbose_name='回复给'
    )
    
    # 统计信息
    likes_count = models.PositiveIntegerField(default=0, verbose_name='点赞数')
    
    # 状态
    is_deleted = models.BooleanField(default=False, verbose_name='是否删除')
    
    # 时间戳
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='更新时间')
    
    class Meta:
        verbose_name = '评论'
        verbose_name_plural = '评论'
        ordering = ['created_at']
    
    def __str__(self):
        return f'{self.author} 评论: {self.content[:50]}'


class PostLike(models.Model):
    """帖子点赞模型"""
    
    post = models.ForeignKey(
        Post, 
        on_delete=models.CASCADE, 
        related_name='likes',
        verbose_name='帖子'
    )
    user = models.ForeignKey(
        User, 
        on_delete=models.CASCADE, 
        related_name='post_likes',
        verbose_name='用户'
    )
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='点赞时间')
    
    class Meta:
        verbose_name = '帖子点赞'
        verbose_name_plural = '帖子点赞'
        unique_together = ('post', 'user')
    
    def __str__(self):
        return f'{self.user} 点赞 {self.post}'


class CommentLike(models.Model):
    """评论点赞模型"""
    
    comment = models.ForeignKey(
        Comment, 
        on_delete=models.CASCADE, 
        related_name='likes',
        verbose_name='评论'
    )
    user = models.ForeignKey(
        User, 
        on_delete=models.CASCADE, 
        related_name='comment_likes',
        verbose_name='用户'
    )
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='点赞时间')
    
    class Meta:
        verbose_name = '评论点赞'
        verbose_name_plural = '评论点赞'
        unique_together = ('comment', 'user')
    
    def __str__(self):
        return f'{self.user} 点赞评论 {self.comment.id}'


class PostCollection(models.Model):
    """帖子收藏模型"""
    
    post = models.ForeignKey(
        Post, 
        on_delete=models.CASCADE, 
        related_name='collections',
        verbose_name='帖子'
    )
    user = models.ForeignKey(
        User, 
        on_delete=models.CASCADE, 
        related_name='post_collections',
        verbose_name='用户'
    )
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='收藏时间')
    
    class Meta:
        verbose_name = '帖子收藏'
        verbose_name_plural = '帖子收藏'
        unique_together = ('post', 'user')
    
    def __str__(self):
        return f'{self.user} 收藏 {self.post}'