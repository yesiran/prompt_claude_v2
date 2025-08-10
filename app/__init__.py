"""
Flask应用初始化模块
负责创建和配置Flask应用实例
"""

from flask import Flask
from flask_cors import CORS
from flask_jwt_extended import JWTManager

from config.config import get_config
from app.models.base import db
from app.utils.logger import init_logger, get_logger


def create_app(env=None):
    """
    创建Flask应用实例
    
    参数:
        env: 环境名称 ('development', 'production')
    
    返回:
        Flask应用实例
    """
    # 创建Flask应用
    app = Flask(__name__)
    
    # 加载配置
    config = get_config(env)
    app.config.from_object(config)
    
    # 初始化日志
    init_logger(config)
    logger = get_logger('app')
    logger.info(f"应用启动，环境: {env or 'development'}")
    
    # 初始化数据库
    db.init_app(app)
    
    # 初始化JWT
    jwt = JWTManager(app)
    
    # 配置CORS
    CORS(app, origins=config.CORS_ORIGINS)
    
    # 注册蓝图
    register_blueprints(app)
    
    # 注册错误处理
    register_error_handlers(app)
    
    # 注册请求钩子
    register_request_hooks(app)
    
    # 创建数据库表（开发环境）
    if app.config['DEBUG']:
        with app.app_context():
            db.create_all()
            logger.info("数据库表创建完成")
    
    return app


def register_blueprints(app):
    """
    注册所有蓝图
    
    参数:
        app: Flask应用实例
    """
    from app.api.auth import auth_bp
    from app.api.prompts import prompts_bp
    from app.api.tags import tags_bp
    from app.api.users import users_bp
    
    # API前缀
    api_prefix = '/api/v1'
    
    # 注册蓝图
    app.register_blueprint(auth_bp, url_prefix=f'{api_prefix}/auth')
    app.register_blueprint(prompts_bp, url_prefix=f'{api_prefix}/prompts')
    app.register_blueprint(tags_bp, url_prefix=f'{api_prefix}/tags')
    app.register_blueprint(users_bp, url_prefix=f'{api_prefix}/users')
    
    get_logger('app').info("蓝图注册完成")


def register_error_handlers(app):
    """
    注册全局错误处理器
    
    参数:
        app: Flask应用实例
    """
    from flask import jsonify
    from werkzeug.exceptions import HTTPException
    
    @app.errorhandler(HTTPException)
    def handle_http_exception(e):
        """处理HTTP异常"""
        response = {
            'code': e.code,
            'message': e.description,
            'timestamp': int(datetime.now().timestamp())
        }
        return jsonify(response), e.code
    
    @app.errorhandler(Exception)
    def handle_exception(e):
        """处理所有其他异常"""
        logger = get_logger('app')
        logger.error(f"未处理的异常: {str(e)}", exc_info=True)
        
        response = {
            'code': 500,
            'message': '服务器内部错误',
            'timestamp': int(datetime.now().timestamp())
        }
        
        # 开发环境显示详细错误
        if app.config['DEBUG']:
            response['error'] = str(e)
        
        return jsonify(response), 500
    
    @app.errorhandler(404)
    def handle_404(e):
        """处理404错误"""
        response = {
            'code': 404,
            'message': '请求的资源不存在',
            'timestamp': int(datetime.now().timestamp())
        }
        return jsonify(response), 404
    
    @app.errorhandler(401)
    def handle_401(e):
        """处理401未授权错误"""
        response = {
            'code': 401,
            'message': '未授权访问',
            'timestamp': int(datetime.now().timestamp())
        }
        return jsonify(response), 401


def register_request_hooks(app):
    """
    注册请求钩子
    
    参数:
        app: Flask应用实例
    """
    from flask import request, g
    from datetime import datetime
    import time
    
    @app.before_request
    def before_request():
        """请求前钩子"""
        g.start_time = time.time()
        
        # 记录请求日志
        logger = get_logger('request')
        logger.info(f"{request.method} {request.path} - {request.remote_addr}")
    
    @app.after_request
    def after_request(response):
        """请求后钩子"""
        if hasattr(g, 'start_time'):
            elapsed = round(time.time() - g.start_time, 3)
            
            # 添加响应时间头
            response.headers['X-Response-Time'] = f"{elapsed}s"
            
            # 记录响应日志
            logger = get_logger('request')
            logger.info(f"响应 {response.status_code} - 耗时 {elapsed}s")
        
        # 添加安全头
        response.headers['X-Content-Type-Options'] = 'nosniff'
        response.headers['X-Frame-Options'] = 'DENY'
        response.headers['X-XSS-Protection'] = '1; mode=block'
        
        return response
    
    @app.teardown_appcontext
    def teardown_db(exception):
        """清理数据库会话"""
        if exception:
            db.session.rollback()
            logger = get_logger('app')
            logger.error(f"请求异常，回滚数据库事务: {str(exception)}")


# 导入必要的模块，避免循环导入
from datetime import datetime