/**
 * 单页应用(SPA)路由管理器
 * 管理页面切换，保持导航栏不动，只更新内容区域
 */

class SPARouter {
    constructor() {
        this.routes = {};
        this.currentRoute = null;
        this.contentContainer = null;
        this.init();
    }
    
    /**
     * 初始化路由器
     */
    init() {
        // 获取内容容器
        this.contentContainer = document.getElementById('mainContent');
        if (!this.contentContainer) {
            console.error('找不到内容容器 #mainContent');
            return;
        }
        
        // 监听浏览器前进后退
        window.addEventListener('popstate', (e) => {
            if (e.state && e.state.route) {
                this.loadRoute(e.state.route, false);
            }
        });
        
        // 拦截所有内部链接点击
        document.addEventListener('click', (e) => {
            // 检查是否是链接或链接内的元素
            let target = e.target;
            while (target && target !== document) {
                if (target.tagName === 'A' && target.href) {
                    const url = new URL(target.href);
                    // 如果是内部链接且有data-spa属性，使用SPA导航
                    if (url.origin === window.location.origin && target.dataset.spa !== 'false') {
                        e.preventDefault();
                        this.navigate(url.pathname);
                        return;
                    }
                }
                target = target.parentElement;
            }
        });
    }
    
    /**
     * 注册路由
     * @param {string} path - 路径
     * @param {Function} handler - 处理函数
     */
    register(path, handler) {
        this.routes[path] = handler;
    }
    
    /**
     * 导航到指定路径
     * @param {string} path - 目标路径
     * @param {boolean} pushState - 是否更新历史记录
     */
    navigate(path, pushState = true) {
        // 检查认证（除了登录和注册页面）
        if (!path.includes('/login') && !path.includes('/register')) {
            if (window.AuthUtils && !window.AuthUtils.checkAuth()) {
                window.AuthUtils.redirectToLogin('请先登录');
                return;
            }
        }
        
        // 更新URL但不刷新页面
        if (pushState) {
            window.history.pushState({ route: path }, '', path);
        }
        
        // 加载对应的内容
        this.loadRoute(path);
    }
    
    /**
     * 加载路由内容
     * @param {string} path - 路径
     */
    async loadRoute(path) {
        // 显示加载中
        this.showLoading();
        
        try {
            // 特殊处理编辑器路由
            if (path.startsWith('/editor/')) {
                await this.loadEditor(path);
            } else if (path === '/home' || path === '/') {
                await this.loadHome();
            } else {
                // 其他路由暂时使用传统方式
                window.location.href = path;
            }
            
            // 更新导航栏激活状态
            this.updateNavActive(path);
            
        } catch (error) {
            console.error('加载路由失败:', error);
            this.showError('页面加载失败，请刷新重试');
        }
    }
    
    /**
     * 加载主页内容
     */
    async loadHome() {
        try {
            // 加载主页的HTML内容
            const response = await fetch('/api/v1/spa/home', {
                headers: {
                    'Authorization': `Bearer ${localStorage.getItem('token')}`
                }
            });
            
            if (!response.ok) {
                // 如果API不存在，暂时使用传统方式
                window.location.href = '/home';
                return;
            }
            
            const html = await response.text();
            this.contentContainer.innerHTML = html;
            
            // 重新初始化主页的JavaScript
            if (window.initHomePage) {
                window.initHomePage();
            }
        } catch (error) {
            // 降级到传统导航
            window.location.href = '/home';
        }
    }
    
    /**
     * 加载编辑器内容
     * @param {string} path - 编辑器路径
     */
    async loadEditor(path) {
        const promptId = path.split('/').pop();
        
        try {
            // 加载编辑器HTML内容
            const response = await fetch(`/api/v1/spa/editor/${promptId}`, {
                headers: {
                    'Authorization': `Bearer ${localStorage.getItem('token')}`
                }
            });
            
            if (!response.ok) {
                // 如果API不存在，暂时使用传统方式
                window.location.href = path;
                return;
            }
            
            const html = await response.text();
            this.contentContainer.innerHTML = html;
            
            // 重新初始化编辑器
            if (window.initEditor) {
                window.initEditor(promptId);
            }
        } catch (error) {
            // 降级到传统导航
            window.location.href = path;
        }
    }
    
    /**
     * 显示加载中状态
     */
    showLoading() {
        if (this.contentContainer) {
            this.contentContainer.innerHTML = `
                <div class="loading-container">
                    <div class="loading-spinner"></div>
                    <p>加载中...</p>
                </div>
            `;
        }
    }
    
    /**
     * 显示错误信息
     * @param {string} message - 错误信息
     */
    showError(message) {
        if (this.contentContainer) {
            this.contentContainer.innerHTML = `
                <div class="error-container">
                    <h2>加载失败</h2>
                    <p>${message}</p>
                    <button onclick="location.reload()">刷新页面</button>
                </div>
            `;
        }
    }
    
    /**
     * 更新导航栏激活状态
     * @param {string} path - 当前路径
     */
    updateNavActive(path) {
        // 移除所有激活状态
        document.querySelectorAll('.nav-item').forEach(item => {
            item.classList.remove('active');
        });
        
        // 添加当前激活状态
        let activeSelector = '';
        if (path.includes('/editor')) {
            activeSelector = '[data-page="prompts"]';
        } else if (path === '/home' || path === '/') {
            activeSelector = '[data-page="prompts"]';
        } else if (path.includes('/tags')) {
            activeSelector = '[data-page="tags"]';
        } else if (path.includes('/collaboration')) {
            activeSelector = '[data-page="collaboration"]';
        } else if (path.includes('/history')) {
            activeSelector = '[data-page="history"]';
        }
        
        if (activeSelector) {
            const activeItem = document.querySelector(`.nav-item${activeSelector}`);
            if (activeItem) {
                activeItem.classList.add('active');
            }
        }
    }
}

// 创建全局路由器实例
window.spaRouter = new SPARouter();

/**
 * 使用SPA导航的辅助函数
 * @param {string} path - 目标路径
 */
window.navigateTo = function(path) {
    if (window.spaRouter) {
        window.spaRouter.navigate(path);
    } else {
        window.location.href = path;
    }
};