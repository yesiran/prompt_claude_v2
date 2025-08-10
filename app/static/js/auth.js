/**
 * 认证相关的通用函数
 * 处理JWT token验证和认证失败的重定向
 */

/**
 * 检查用户是否已登录
 * @returns {boolean} 是否已登录
 */
function checkAuth() {
    const token = localStorage.getItem('token');
    return token !== null && token !== undefined && token !== '';
}

/**
 * 获取当前用户信息
 * @returns {Object|null} 用户信息对象或null
 */
function getCurrentUser() {
    const userStr = localStorage.getItem('user');
    if (userStr) {
        try {
            return JSON.parse(userStr);
        } catch (e) {
            console.error('解析用户信息失败:', e);
            return null;
        }
    }
    return null;
}

/**
 * 清除认证信息并跳转到登录页
 * @param {string} message - 可选的提示消息
 */
function redirectToLogin(message) {
    // 清除本地存储的认证信息
    localStorage.removeItem('token');
    localStorage.removeItem('user');
    
    // 如果有消息，存储起来在登录页显示
    if (message) {
        sessionStorage.setItem('loginMessage', message);
    }
    
    // 跳转到登录页
    window.location.href = '/login';
}

/**
 * 处理API响应，检查认证错误
 * @param {Response} response - fetch的响应对象
 * @returns {Promise<Response>} 处理后的响应
 */
async function handleAuthResponse(response) {
    // 如果是401或422错误（JWT验证失败），重定向到登录页
    if (response.status === 401) {
        redirectToLogin('登录已过期，请重新登录');
        throw new Error('Authentication failed');
    }
    
    if (response.status === 422) {
        // 检查是否是JWT相关的422错误
        try {
            const data = await response.clone().json();
            if (data.msg && (data.msg.includes('token') || data.msg.includes('JWT'))) {
                redirectToLogin('认证失败，请重新登录');
                throw new Error('JWT validation failed');
            }
        } catch (e) {
            // 如果不能解析JSON，继续处理
        }
    }
    
    return response;
}

/**
 * 发送认证请求的封装函数
 * @param {string} url - 请求URL
 * @param {Object} options - fetch选项
 * @returns {Promise<Response>} 响应对象
 */
async function authFetch(url, options = {}) {
    const token = localStorage.getItem('token');
    
    // 如果没有token，直接重定向到登录页
    if (!token && !url.includes('/auth/')) {
        redirectToLogin('请先登录');
        throw new Error('No authentication token');
    }
    
    // 添加认证头
    if (token) {
        options.headers = {
            ...options.headers,
            'Authorization': `Bearer ${token}`
        };
    }
    
    // 发送请求并处理认证错误
    try {
        const response = await fetch(url, options);
        return await handleAuthResponse(response);
    } catch (error) {
        // 网络错误或其他错误
        if (error.message === 'Authentication failed' || 
            error.message === 'JWT validation failed' ||
            error.message === 'No authentication token') {
            // 认证错误已经处理，直接抛出
            throw error;
        }
        
        // 其他错误
        console.error('请求失败:', error);
        throw error;
    }
}

/**
 * 初始化页面认证检查
 * 在需要认证的页面加载时调用
 */
function initAuthCheck() {
    // 检查是否已登录
    if (!checkAuth()) {
        redirectToLogin('请先登录');
        return false;
    }
    
    // 设置定期检查token有效性（可选）
    setInterval(() => {
        // 可以添加token过期时间检查
        const token = localStorage.getItem('token');
        if (!token) {
            redirectToLogin('登录已过期，请重新登录');
        }
    }, 60000); // 每分钟检查一次
    
    return true;
}

// 导出函数供其他模块使用
window.AuthUtils = {
    checkAuth,
    getCurrentUser,
    redirectToLogin,
    handleAuthResponse,
    authFetch,
    initAuthCheck
};