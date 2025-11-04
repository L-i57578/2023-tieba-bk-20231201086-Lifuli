"""
主视图文件，处理前端页面的渲染
"""
from django.shortcuts import render, redirect
from django.views.generic import TemplateView, View
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.contrib import messages
from django.db import models

class HomeView(TemplateView):
    """首页视图"""
    template_name = 'home.html'

class TiebaSquareView(View):
    """贴吧广场视图"""
    template_name = 'tieba_square.html'
    
    def get(self, request):
        from tiebas.models import Tieba
        from posts.models import Post
        
        # 获取搜索参数
        search_query = request.GET.get('search', '').strip()
        category_filter = request.GET.get('category', '')
        sort_by = request.GET.get('sort', 'all')
        
        # 获取贴吧列表（支持搜索和筛选）
        tiebas = Tieba.objects.all()
        
        # 搜索功能
        if search_query:
            tiebas = tiebas.filter(name__icontains=search_query)
        
        # 分类筛选
        if category_filter:
            tiebas = tiebas.filter(category=category_filter)
        
        # 排序功能
        if sort_by == 'hot':
            tiebas = tiebas.order_by('-members_count')
        elif sort_by == 'new':
            tiebas = tiebas.order_by('-created_at')
        elif sort_by == 'recommend':
            # 推荐排序（可以基于算法，这里简化为按关注数排序）
            tiebas = tiebas.order_by('-members_count')
        else:
            tiebas = tiebas.order_by('-members_count')  # 默认按关注数排序
        
        # 获取最新的帖子（跨贴吧，按创建时间倒序排列），预加载图片数据
        latest_posts = Post.objects.all().order_by('-created_at').prefetch_related('images')[:10]  # 显示最新的10个帖子
        
        return render(request, self.template_name, {
            'tiebas': tiebas,
            'latest_posts': latest_posts,
            'search_query': search_query,
            'category_filter': category_filter,
            'sort_by': sort_by
        })

class TiebaDetailView(View):
    """贴吧详情视图"""
    template_name = 'tieba_detail.html'
    
    def get(self, request, pk):
        from tiebas.models import Tieba
        from posts.models import Post
        
        try:
            # 获取贴吧信息
            tieba = Tieba.objects.get(id=pk)
            
            # 获取该贴吧的帖子列表（按创建时间倒序排列）
            posts = Post.objects.filter(tieba=tieba).order_by('-created_at')
            
            # 获取贴吧成员数量
            member_count = tieba.members_count or 0
            
            # 获取今日帖子数量（简化处理，实际应该按日期过滤）
            today_posts_count = posts.count()  # 简化处理
            
            return render(request, self.template_name, {
                'tieba': tieba,
                'posts': posts,
                'member_count': member_count,
                'today_posts_count': today_posts_count
            })
            
        except Tieba.DoesNotExist:
            from django.http import Http404
            raise Http404("贴吧不存在")

class PostDetailView(View):
    """帖子详情视图"""
    template_name = 'post_detail.html'
    
    def get(self, request, pk):
        from posts.models import Post
        from posts.models import Comment
        
        try:
            # 获取帖子信息，预加载图片数据
            post = Post.objects.prefetch_related('images').get(id=pk)
            
            # 增加帖子浏览量
            post.views_count = (post.views_count or 0) + 1
            post.save()
            
            # 获取帖子的回复（评论）
            comments = Comment.objects.filter(post=post).order_by('-created_at')
            
            # 获取相关帖子（同贴吧的其他帖子）
            related_posts = Post.objects.filter(
                tieba=post.tieba
            ).exclude(id=post.id).order_by('-created_at')[:5]
            
            return render(request, self.template_name, {
                'post': post,
                'comments': comments,
                'related_posts': related_posts,
                'comment_count': comments.count()
            })
            
        except Post.DoesNotExist:
            from django.http import Http404
            raise Http404("帖子不存在")
    
    def post(self, request, pk):
        from posts.models import Post
        from posts.models import Comment
        
        try:
            post = Post.objects.get(id=pk)
            content = request.POST.get('content')
            
            if content and request.user.is_authenticated:
                # 创建评论
                Comment.objects.create(
                    post=post,
                    author=request.user,
                    content=content
                )
            
            return redirect('post_detail', pk=pk)
        except Post.DoesNotExist:
            from django.http import Http404
            raise Http404("帖子不存在")

class UserProfileView(View):
    """用户个人资料视图"""
    template_name = 'user_profile.html'
    
    def get(self, request):
        from posts.models import Post
        
        # 获取当前用户的帖子（按创建时间倒序排列）
        user_posts = Post.objects.filter(author=request.user).order_by('-created_at')[:20]
        
        # 获取用户帖子统计
        total_posts = Post.objects.filter(author=request.user).count()
        
        return render(request, self.template_name, {
            'user_posts': user_posts,
            'total_posts': total_posts
        })

class EditProfileView(TemplateView):
    """编辑个人资料视图"""
    template_name = 'edit_profile.html'

class PublishCenterView(View):
    """发布中心视图"""
    
    @method_decorator(login_required)
    def get(self, request):
        from tiebas.models import Tieba
        
        # 获取所有贴吧列表
        tiebas = Tieba.objects.all()
        
        return render(request, 'publish_center.html', {
            'tiebas': tiebas
        })
    
    @method_decorator(login_required)
    def post(self, request):
        from tiebas.models import Tieba
        from posts.models import Post, PostImage
        
        try:
            # 获取表单数据
            tieba_id = request.POST.get('tieba')
            title = request.POST.get('title')
            content = request.POST.get('content')
            post_type = request.POST.get('post_type', 'normal')
            
            # 验证必填字段
            if not all([tieba_id, title, content]):
                messages.error(request, '请填写完整的帖子信息')
                tiebas = Tieba.objects.all()
                return render(request, 'publish_center.html', {
                    'tiebas': tiebas
                })
            
            # 获取贴吧对象
            tieba = Tieba.objects.get(id=tieba_id)
            
            # 创建帖子
            post = Post.objects.create(
                title=title,
                content=content,
                post_type=post_type,
                tieba=tieba,
                author=request.user
            )
            
            # 处理图片上传
            images = request.FILES.getlist('images')
            for i, image in enumerate(images):
                if image:  # 确保文件存在
                    PostImage.objects.create(
                        post=post,
                        image=image,
                        sort_order=i
                    )
            
            messages.success(request, '帖子发布成功！')
            return redirect('post_detail', pk=post.id)
            
        except Tieba.DoesNotExist:
            messages.error(request, '选择的贴吧不存在')
            tiebas = Tieba.objects.all()
            return render(request, 'publish_center.html', {
                'tiebas': tiebas
            })
        except Exception as e:
            messages.error(request, f'发布失败：{str(e)}')
            tiebas = Tieba.objects.all()
            return render(request, 'publish_center.html', {
                'tiebas': tiebas
            })



class MessagesView(TemplateView):
    """消息视图"""
    template_name = 'messages.html'

class LoginView(View):
    """登录视图"""
    
    def get(self, request):
        if request.user.is_authenticated:
            return redirect('home')
        return render(request, 'login.html')
    
    def post(self, request):
        username = request.POST.get('username')
        password = request.POST.get('password')
        
        user = authenticate(request, username=username, password=password)
        
        if user is not None:
            login(request, user)
            return redirect('home')
        else:
            messages.error(request, '用户名或密码错误')
            return render(request, 'login.html')

class LogoutView(View):
    """退出登录视图"""
    
    def get(self, request):
        logout(request)
        return redirect('home')

class GlobalSearchView(View):
    """全局搜索视图"""
    template_name = 'search_results.html'
    
    def get(self, request):
        from tiebas.models import Tieba
        from posts.models import Post
        from users.models import User
        
        # 获取搜索关键词
        query = request.GET.get('q', '').strip()
        search_type = request.GET.get('type', 'all')  # all, tieba, post, user
        
        if not query:
            # 如果没有搜索关键词，重定向到首页
            return redirect('home')
        
        # 初始化搜索结果
        tieba_results = []
        post_results = []
        user_results = []
        
        # 根据搜索类型进行搜索
        if search_type == 'all' or search_type == 'tieba':
            # 搜索贴吧
            tieba_results = Tieba.objects.filter(
                models.Q(name__icontains=query) | 
                models.Q(description__icontains=query)
            ).order_by('-members_count')[:20]
        
        if search_type == 'all' or search_type == 'post':
            # 搜索帖子
            post_results = Post.objects.filter(
                models.Q(title__icontains=query) | 
                models.Q(content__icontains=query)
            ).order_by('-created_at')[:20]
        
        if search_type == 'all' or search_type == 'user':
            # 搜索用户
            user_results = User.objects.filter(
                models.Q(username__icontains=query) | 
                models.Q(nickname__icontains=query)
            )[:20]
        
        return render(request, self.template_name, {
            'query': query,
            'search_type': search_type,
            'tieba_results': tieba_results,
            'post_results': post_results,
            'user_results': user_results,
            'tieba_count': len(tieba_results),
            'post_count': len(post_results),
            'user_count': len(user_results)
        })

class RegisterView(View):
    """注册视图"""
    
    def get(self, request):
        if request.user.is_authenticated:
            return redirect('home')
        return render(request, 'register.html')
    
    def post(self, request):
        from django.contrib.auth import get_user_model
        
        User = get_user_model()
        username = request.POST.get('username')
        password = request.POST.get('password')
        email = request.POST.get('email')
        
        if User.objects.filter(username=username).exists():
            messages.error(request, '用户名已存在')
            return render(request, 'register.html')
        
        if User.objects.filter(email=email).exists():
            messages.error(request, '邮箱已被注册')
            return render(request, 'register.html')
        
        user = User.objects.create_user(username=username, password=password, email=email)
        login(request, user)
        return redirect('home')

def custom_404_view(request, exception=None):
    """自定义404页面"""
    return render(request, '404.html', status=404)

def custom_500_view(request):
    """自定义500页面"""
    return render(request, '500.html', status=500)