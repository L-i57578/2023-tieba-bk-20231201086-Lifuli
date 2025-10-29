"""
主视图文件，处理前端页面的渲染
"""
from django.shortcuts import render
from django.views.generic import TemplateView

class HomeView(TemplateView):
    """首页视图"""
    template_name = 'home.html'

class TiebaSquareView(TemplateView):
    """贴吧广场视图"""
    template_name = 'tieba_square.html'

class TiebaDetailView(TemplateView):
    """贴吧详情视图"""
    template_name = 'tieba_detail.html'

class PostDetailView(TemplateView):
    """帖子详情视图"""
    template_name = 'post_detail.html'

class UserProfileView(TemplateView):
    """用户个人资料视图"""
    template_name = 'user_profile.html'

class EditProfileView(TemplateView):
    """编辑个人资料视图"""
    template_name = 'edit_profile.html'

class PublishCenterView(TemplateView):
    """发布中心视图"""
    template_name = 'publish_center.html'

class MessagesView(TemplateView):
    """消息视图"""
    template_name = 'messages.html'

class LoginView(TemplateView):
    """登录视图"""
    template_name = 'login.html'

class RegisterView(TemplateView):
    """注册视图"""
    template_name = 'register.html'

def custom_404_view(request, exception=None):
    """自定义404页面"""
    return render(request, '404.html', status=404)

def custom_500_view(request):
    """自定义500页面"""
    return render(request, '500.html', status=500)