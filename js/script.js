// 贴吧首页交互功能
class TiebaHomepage {
    constructor() {
        this.currentPage = 'home';
        this.init();
    }

    init() {
        this.setupNavigation();
        this.loadHotTiebas();
        this.loadHotPosts();
        this.setupSearch();
        this.setupAnimations();
        this.setupPageNavigation();
    }

    // 设置导航栏交互
    setupNavigation() {
        const navToggle = document.getElementById('navToggle');
        const navLinks = document.getElementById('navLinks');

        if (navToggle && navLinks) {
            navToggle.addEventListener('click', () => {
                navLinks.classList.toggle('active');
                navToggle.classList.toggle('active');
            });

            // 点击导航链接时关闭移动端菜单
            navLinks.querySelectorAll('a').forEach(link => {
                link.addEventListener('click', () => {
                    navLinks.classList.remove('active');
                    navToggle.classList.remove('active');
                });
            });
        }

        // 点击页面其他区域关闭移动端菜单
        document.addEventListener('click', (e) => {
            if (!e.target.closest('.nav-container') && navLinks) {
                navLinks.classList.remove('active');
                navToggle.classList.remove('active');
            }
        });
    }

    // 加载热门贴吧数据
    loadHotTiebas() {
        const tiebaGrid = document.getElementById('tiebaGrid');
        if (!tiebaGrid) return;

        // 模拟热门贴吧数据
        const hotTiebas = [
            { name: '英雄联盟', members: '1280万', avatar: 'LOL' },
            { name: '王者荣耀', members: '980万', avatar: 'WZ' },
            { name: '原神', members: '750万', avatar: 'YS' },
            { name: '数码', members: '620万', avatar: 'SM' },
            { name: '美食', members: '580万', avatar: 'MS' },
            { name: '电影', members: '520万', avatar: 'DY' },
            { name: '音乐', members: '480万', avatar: 'YY' },
            { name: '体育', members: '450万', avatar: 'TY' }
        ];

        tiebaGrid.innerHTML = hotTiebas.map((tieba, index) => `
            <div class="tieba-item" data-index="${index}" onclick="tiebaHomepage.goToTieba('${tieba.name}')">
                <div class="tieba-avatar">${tieba.avatar}</div>
                <div class="tieba-name">${tieba.name}</div>
                <div class="tieba-members">${tieba.members} 成员</div>
            </div>
        `).join('');
    }

    // 加载热门帖子数据
    loadHotPosts() {
        const postList = document.getElementById('postList');
        if (!postList) return;

        // 模拟热门帖子数据
        const hotPosts = [
            {
                title: '【讨论】大家觉得新版本哪个英雄最强？',
                content: '新版本更新后，英雄强度发生了很大变化，大家来讨论一下当前版本最强的英雄是哪个？',
                author: '游戏达人',
                time: '2小时前',
                views: '1.2万',
                replies: '356',
                likes: '890',
                avatar: '游'
            },
            {
                title: '【分享】今天发现了一家超好吃的火锅店！',
                content: '位置在市中心，环境很好，食材新鲜，强烈推荐给大家！',
                author: '美食家小张',
                time: '4小时前',
                views: '8.6千',
                replies: '128',
                likes: '456',
                avatar: '美'
            },
            {
                title: '【求助】电脑突然蓝屏怎么办？',
                content: '今天开机突然蓝屏，错误代码0x0000007B，有大神知道怎么解决吗？',
                author: '电脑小白',
                time: '6小时前',
                views: '5.3千',
                replies: '89',
                likes: '234',
                avatar: '电'
            },
            {
                title: '【讨论】最近有什么好看的电影推荐？',
                content: '周末想去看电影，大家有什么好推荐的吗？科幻、动作、喜剧都可以。',
                author: '电影爱好者',
                time: '8小时前',
                views: '7.1千',
                replies: '156',
                likes: '378',
                avatar: '电'
            },
            {
                title: '【技术】JavaScript最新特性解析',
                content: '深入解析ES2023新特性，包括新的数组方法和语法糖。',
                author: '前端开发',
                time: '12小时前',
                views: '9.8千',
                replies: '234',
                likes: '567',
                avatar: '前'
            }
        ];

        postList.innerHTML = hotPosts.map((post, index) => `
            <div class="post-item" data-index="${index}" onclick="tiebaHomepage.viewPost(${index})">
                <div class="post-header">
                    <div class="post-avatar">${post.avatar}</div>
                    <div class="post-meta">
                        <div class="post-author">${post.author}</div>
                        <div class="post-time">${post.time}</div>
                    </div>
                </div>
                <div class="post-title">${post.title}</div>
                <div class="post-content">${post.content}</div>
                <div class="post-stats">
                    <span class="post-stat">
                        <i class="fas fa-eye"></i>
                        ${post.views}
                    </span>
                    <span class="post-stat">
                        <i class="fas fa-comment"></i>
                        ${post.replies}
                    </span>
                    <span class="post-stat">
                        <i class="fas fa-heart"></i>
                        ${post.likes}
                    </span>
                </div>
            </div>
        `).join('');
    }

    // 设置搜索功能
    setupSearch() {
        const searchInputs = document.querySelectorAll('.search-input, .search-input-large');
        const searchButtons = document.querySelectorAll('.search-btn, .search-btn-large');

        searchInputs.forEach(input => {
            input.addEventListener('keypress', (e) => {
                if (e.key === 'Enter') {
                    this.performSearch(input.value);
                }
            });
        });

        searchButtons.forEach(button => {
            button.addEventListener('click', () => {
                const input = button.previousElementSibling || 
                             button.parentElement.querySelector('.search-input') ||
                             button.parentElement.querySelector('.search-input-large');
                if (input) {
                    this.performSearch(input.value);
                }
            });
        });
    }

    // 执行搜索
    performSearch(query) {
        if (!query.trim()) {
            this.showMessage('请输入搜索关键词', 'warning');
            return;
        }

        this.showMessage(`正在搜索: ${query}`, 'info');
        
        // 模拟搜索延迟
        setTimeout(() => {
            this.showMessage(`找到 ${Math.floor(Math.random() * 1000)} 条相关结果`, 'success');
            // 在实际应用中，这里会跳转到搜索结果页面
        }, 1000);
    }

    // 设置动画效果
    setupAnimations() {
        // 观察器用于滚动动画
        const observerOptions = {
            threshold: 0.1,
            rootMargin: '0px 0px -50px 0px'
        };

        const observer = new IntersectionObserver((entries) => {
            entries.forEach(entry => {
                if (entry.isIntersecting) {
                    entry.target.style.animationPlayState = 'running';
                }
            });
        }, observerOptions);

        // 观察所有可动画的元素
        document.querySelectorAll('.tieba-item, .post-item').forEach(item => {
            observer.observe(item);
        });

        // 添加滚动到顶部的按钮
        this.addScrollToTopButton();
    }

    // 添加滚动到顶部按钮
    addScrollToTopButton() {
        const scrollButton = document.createElement('button');
        scrollButton.innerHTML = '<i class="fas fa-chevron-up"></i>';
        scrollButton.className = 'scroll-to-top';
        scrollButton.style.cssText = `
            position: fixed;
            bottom: 30px;
            right: 30px;
            width: 50px;
            height: 50px;
            border-radius: 50%;
            background: var(--primary-color);
            color: white;
            border: none;
            cursor: pointer;
            font-size: 1.2rem;
            box-shadow: var(--shadow-medium);
            opacity: 0;
            transform: translateY(20px);
            transition: all 0.3s ease;
            z-index: 999;
        `;

        scrollButton.addEventListener('click', () => {
            window.scrollTo({
                top: 0,
                behavior: 'smooth'
            });
        });

        document.body.appendChild(scrollButton);

        // 显示/隐藏滚动按钮
        window.addEventListener('scroll', () => {
            if (window.scrollY > 300) {
                scrollButton.style.opacity = '1';
                scrollButton.style.transform = 'translateY(0)';
            } else {
                scrollButton.style.opacity = '0';
                scrollButton.style.transform = 'translateY(20px)';
            }
        });
    }

    // 显示消息提示
    showMessage(message, type = 'info') {
        // 移除现有的消息
        const existingMessage = document.querySelector('.message-toast');
        if (existingMessage) {
            existingMessage.remove();
        }

        const messageDiv = document.createElement('div');
        messageDiv.className = `message-toast message-${type}`;
        messageDiv.textContent = message;
        messageDiv.style.cssText = `
            position: fixed;
            top: 100px;
            right: 30px;
            padding: 15px 20px;
            border-radius: var(--border-radius-md);
            color: white;
            font-weight: 500;
            z-index: 1001;
            transform: translateX(100%);
            transition: transform 0.3s ease;
            max-width: 300px;
        `;

        // 根据类型设置背景色
        const colors = {
            info: '#3385ff',
            success: '#4ecdc4',
            warning: '#ff9500',
            error: '#ff6b6b'
        };
        messageDiv.style.background = colors[type] || colors.info;

        document.body.appendChild(messageDiv);

        // 显示动画
        setTimeout(() => {
            messageDiv.style.transform = 'translateX(0)';
        }, 100);

        // 3秒后自动消失
        setTimeout(() => {
            messageDiv.style.transform = 'translateX(100%)';
            setTimeout(() => {
                if (messageDiv.parentNode) {
                    messageDiv.remove();
                }
            }, 300);
        }, 3000);
    }

    // 跳转到贴吧页面
    goToTieba(tiebaName) {
        this.showMessage(`正在跳转到 ${tiebaName} 贴吧`, 'info');
        // 在实际应用中，这里会跳转到对应的贴吧页面
        setTimeout(() => {
            // window.location.href = `/tieba/${encodeURIComponent(tiebaName)}`;
        }, 1000);
    }

    // 查看帖子详情
    viewPost(postIndex) {
        this.showMessage(`正在加载帖子详情...`, 'info');
        // 在实际应用中，这里会跳转到帖子详情页面
        setTimeout(() => {
            // window.location.href = `/post/${postIndex}`;
        }, 1000);
    }

    // 页面加载完成后的初始化
    onPageLoad() {
        this.showMessage('欢迎来到百度贴吧！', 'success');
        
        // 添加加载动画
        document.body.style.opacity = '0';
        document.body.style.transition = 'opacity 0.5s ease';
        
        setTimeout(() => {
            document.body.style.opacity = '1';
        }, 100);
    }

    setupKeyboardShortcuts() {
        document.addEventListener('keydown', (e) => {
            // 搜索快捷键 Ctrl+K 或 Cmd+K
            if ((e.ctrlKey || e.metaKey) && e.key === 'k') {
                e.preventDefault();
                const searchInput = document.querySelector('.search-input');
                if (searchInput) {
                    searchInput.focus();
                }
            }
            
            // 回到顶部快捷键 Home
            if (e.key === 'Home') {
                e.preventDefault();
                this.scrollToTop();
            }
        });
    }

    setupPageNavigation() {
        // 监听导航链接点击
        const navLinks = document.querySelectorAll('.nav-links a, .nav-user a');
        navLinks.forEach(link => {
            link.addEventListener('click', (e) => {
                e.preventDefault();
                const target = link.getAttribute('href').substring(1); // 去掉#
                this.navigateToPage(target);
            });
        });

        // 监听表单内的链接点击
        document.addEventListener('click', (e) => {
            if (e.target.tagName === 'A' && e.target.getAttribute('href')?.startsWith('#')) {
                e.preventDefault();
                const target = e.target.getAttribute('href').substring(1);
                this.navigateToPage(target);
            }
        });

        // 监听浏览器前进后退按钮
        window.addEventListener('popstate', (e) => {
            const target = window.location.hash.substring(1) || 'home';
            this.navigateToPage(target, false);
        });

        // 初始化页面状态
        const initialPage = window.location.hash.substring(1) || 'home';
        this.navigateToPage(initialPage, false);
    }

    navigateToPage(pageId, updateHistory = true) {
        // 隐藏所有页面
        const allPages = document.querySelectorAll('.page-section, .hero-section, #home-content');
        allPages.forEach(page => {
            page.style.display = 'none';
        });

        // 显示目标页面
        if (pageId === 'home') {
            // 显示首页内容
            const heroSection = document.getElementById('home');
            const homeContent = document.getElementById('home-content');
            if (heroSection) heroSection.style.display = 'block';
            if (homeContent) homeContent.style.display = 'block';
        } else {
            const targetPage = document.getElementById(pageId);
            if (targetPage) {
                targetPage.style.display = 'block';
            }
        }

        this.currentPage = pageId;

        // 更新导航栏激活状态
        this.updateNavActiveState(pageId);

        // 更新浏览器历史记录
        if (updateHistory) {
            window.history.pushState({ page: pageId }, '', `#${pageId}`);
        }

        // 滚动到页面顶部
        window.scrollTo({ top: 0, behavior: 'smooth' });

        // 根据页面类型执行特定操作
        this.handlePageSpecificActions(pageId);
    }

    updateNavActiveState(pageId) {
        // 移除所有激活状态
        const allNavLinks = document.querySelectorAll('.nav-links a');
        allNavLinks.forEach(link => {
            link.classList.remove('active');
        });

        // 设置当前页面激活状态
        const currentNavLink = document.querySelector(`.nav-links a[href="#${pageId}"]`);
        if (currentNavLink) {
            currentNavLink.classList.add('active');
        }
    }

    handlePageSpecificActions(pageId) {
        switch (pageId) {
            case 'hot':
                this.setupHotTabs();
                break;
            case 'rankings':
                this.setupRankingTabs();
                break;
            case 'login':
                this.setupLoginForm();
                break;
            case 'register':
                this.setupRegisterForm();
                break;
        }
    }

    setupHotTabs() {
        const tabButtons = document.querySelectorAll('#hot .tab-btn');
        const tabPanes = document.querySelectorAll('#hot .tab-pane');

        tabButtons.forEach(button => {
            button.addEventListener('click', () => {
                // 移除所有激活状态
                tabButtons.forEach(btn => btn.classList.remove('active'));
                tabPanes.forEach(pane => pane.classList.remove('active'));

                // 设置当前激活状态
                button.classList.add('active');
                const tabId = button.getAttribute('data-tab');
                const targetPane = document.getElementById(tabId);
                if (targetPane) {
                    targetPane.classList.add('active');
                }
            });
        });
    }

    setupRankingTabs() {
        const tabButtons = document.querySelectorAll('#rankings .tab-btn');
        const rankingLists = document.querySelectorAll('#rankings .ranking-list');

        tabButtons.forEach(button => {
            button.addEventListener('click', () => {
                // 移除所有激活状态
                tabButtons.forEach(btn => btn.classList.remove('active'));
                rankingLists.forEach(list => list.classList.remove('active'));

                // 设置当前激活状态
                button.classList.add('active');
                const tabId = button.getAttribute('data-tab');
                const targetList = document.getElementById(tabId);
                if (targetList) {
                    targetList.classList.add('active');
                }
            });
        });
    }

    setupLoginForm() {
        const loginForm = document.querySelector('#login form');
        if (loginForm) {
            loginForm.addEventListener('submit', (e) => {
                e.preventDefault();
                this.showMessage('登录功能开发中...', 'info');
            });
        }
    }

    setupRegisterForm() {
        const registerForm = document.querySelector('#register form');
        if (registerForm) {
            registerForm.addEventListener('submit', (e) => {
                e.preventDefault();
                this.showMessage('注册功能开发中...', 'info');
            });
        }
    }

    scrollToTop() {
        window.scrollTo({
            top: 0,
            behavior: 'smooth'
        });
    }
}

// 页面加载完成后初始化
window.addEventListener('DOMContentLoaded', () => {
    window.tiebaHomepage = new TiebaHomepage();
    tiebaHomepage.onPageLoad();
});

// 添加键盘快捷键支持
document.addEventListener('keydown', (e) => {
    // Ctrl + K 聚焦搜索框
    if ((e.ctrlKey || e.metaKey) && e.key === 'k') {
        e.preventDefault();
        const searchInput = document.querySelector('.search-input') || 
                           document.querySelector('.search-input-large');
        if (searchInput) {
            searchInput.focus();
        }
    }
    
    // ESC 键关闭移动端菜单
    if (e.key === 'Escape') {
        const navLinks = document.getElementById('navLinks');
        const navToggle = document.getElementById('navToggle');
        if (navLinks && navLinks.classList.contains('active')) {
            navLinks.classList.remove('active');
            navToggle.classList.remove('active');
        }
    }
});

// 添加触摸设备优化
if ('ontouchstart' in window) {
    document.documentElement.classList.add('touch-device');
}

// 添加页面可见性检测
document.addEventListener('visibilitychange', () => {
    if (!document.hidden) {
        // 页面重新可见时，可以刷新数据
        console.log('页面重新可见');
    }
});