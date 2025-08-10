"""
Flask应用主入口文件
"""

import os
from flask import render_template, redirect
from app import create_app
from app.utils.logger import get_logger

# 获取环境变量，默认为开发环境
env = os.getenv('FLASK_ENV', 'development')

# 创建应用实例
app = create_app(env)

# 获取日志记录器
logger = get_logger('app')


# ========== 页面路由 ==========

@app.route('/')
def index():
    """根路径 - 重定向到登录页"""
    return redirect('/login')


@app.route('/login')
def login_page():
    """登录页面"""
    return render_template('login.html')


@app.route('/register')
def register_page():
    """注册页面"""
    return render_template('register.html')


@app.route('/home')
def home_page():
    """主页面"""
    return render_template('index.html')


@app.route('/editor/<prompt_id>')
def editor_page(prompt_id):
    """编辑器页面"""
    return render_template('editor.html')


@app.route('/tags')
def tags_page():
    """标签管理页面"""
    return render_template('tags.html')


# ========== API信息接口 ==========

@app.route('/api')
def api_info():
    """API信息"""
    return {
        'name': 'Prompt Manager API',
        'version': '1.0.0',
        'status': 'running',
        'environment': env,
        'endpoints': {
            'auth': '/api/v1/auth',
            'prompts': '/api/v1/prompts',
            'tags': '/api/v1/tags',
            'users': '/api/v1/users'
        }
    }


@app.route('/health')
def health():
    """健康检查接口"""
    return {
        'status': 'healthy',
        'database': check_database_connection()
    }


def check_database_connection():
    """
    检查数据库连接状态
    
    返回:
        str: 'connected' 或 'disconnected'
    """
    try:
        from app.models.base import db
        db.session.execute('SELECT 1')
        return 'connected'
    except Exception as e:
        logger.error(f"数据库连接失败: {str(e)}")
        return 'disconnected'


if __name__ == '__main__':
    """主程序入口"""
    
    # 获取配置
    port = app.config.get('APP_PORT', 5002)
    host = app.config.get('APP_HOST', '0.0.0.0')
    debug = app.config.get('DEBUG', True)
    
    logger.info(f"应用启动: http://{host}:{port}")
    logger.info(f"环境: {env}")
    logger.info(f"调试模式: {debug}")
    
    # 启动应用
    app.run(
        host=host,
        port=port,
        debug=debug
    )