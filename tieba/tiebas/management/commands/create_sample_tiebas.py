"""
创建示例贴吧数据的管理命令
"""
from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from tiebas.models import Tieba, TiebaCategory

User = get_user_model()

class Command(BaseCommand):
    help = '创建示例贴吧数据'

    def handle(self, *args, **options):
        # 获取或创建管理员用户
        admin_user, created = User.objects.get_or_create(
            username='admin',
            defaults={
                'email': 'admin@example.com',
                'is_staff': True,
                'is_superuser': True
            }
        )
        
        if created:
            admin_user.set_password('admin123')
            admin_user.save()
            self.stdout.write(self.style.SUCCESS('创建管理员用户'))
        
        # 创建贴吧分类
        categories = [
            ('游戏', '各种游戏相关的贴吧'),
            ('生活', '生活娱乐相关的贴吧'),
            ('学习', '学习交流相关的贴吧'),
            ('科技', '科技数码相关的贴吧'),
        ]
        
        category_objs = {}
        for name, description in categories:
            category, created = TiebaCategory.objects.get_or_create(
                name=name,
                defaults={'description': description}
            )
            category_objs[name] = category
            if created:
                self.stdout.write(self.style.SUCCESS(f'创建分类: {name}'))
        
        # 创建示例贴吧
        tiebas = [
            ('英雄联盟', '英雄联盟游戏讨论', '游戏'),
            ('王者荣耀', '王者荣耀手游交流', '游戏'),
            ('美食', '美食分享与交流', '生活'),
            ('旅游', '旅游攻略分享', '生活'),
            ('编程', '编程学习交流', '学习'),
            ('考研', '考研经验分享', '学习'),
            ('手机', '手机数码讨论', '科技'),
            ('电脑', '电脑硬件交流', '科技'),
        ]
        
        for name, description, category_name in tiebas:
            tieba, created = Tieba.objects.get_or_create(
                name=name,
                defaults={
                    'description': description,
                    'category': category_objs[category_name],
                    'creator': admin_user
                }
            )
            if created:
                self.stdout.write(self.style.SUCCESS(f'创建贴吧: {name}'))
        
        self.stdout.write(self.style.SUCCESS('示例贴吧数据创建完成！'))