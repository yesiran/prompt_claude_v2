"""
认证API
处理用户注册、登录、登出等认证相关接口
"""

from flask import Blueprint, request, jsonify
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity
from werkzeug.exceptions import BadRequest, Unauthorized

from app.models.user import User
from app.models.base import db
from app.utils.logger import get_logger
from app.utils.response import success_response, error_response

# 创建蓝图
auth_bp = Blueprint('auth', __name__)

# 获取日志记录器
logger = get_logger('auth')


@auth_bp.route('/register', methods=['POST'])
def register():
    """
    用户注册接口
    
    请求体:
        {
            "username": "用户名",
            "email": "邮箱",
            "password": "密码"
        }
    """
    try:
        data = request.get_json()
        
        # 参数验证
        username = data.get('username')
        email = data.get('email')
        password = data.get('password')
        
        if not all([username, email, password]):
            return error_response(400, '用户名、邮箱和密码不能为空')
        
        # 检查用户名是否已存在
        if User.get_by_username(username):
            return error_response(400, '用户名已被使用')
        
        # 检查邮箱是否已存在
        if User.get_by_email(email):
            return error_response(400, '邮箱已被注册')
        
        # 创建用户
        user = User.create_user(
            username=username,
            email=email,
            password=password
        )
        
        # 记录日志
        logger.info(f"新用户注册: {username} ({email})")
        
        # 返回成功响应
        return success_response({
            'user': user.to_dict(),
            'message': '注册成功'
        }, 201)
        
    except Exception as e:
        logger.error(f"注册失败: {str(e)}", exc_info=True)
        return error_response(500, '注册失败，请稍后重试')


@auth_bp.route('/login', methods=['POST'])
def login():
    """
    用户登录接口
    
    请求体:
        {
            "email": "邮箱",
            "password": "密码"
        }
    """
    try:
        data = request.get_json()
        
        # 参数验证
        email = data.get('email')
        password = data.get('password')
        
        if not all([email, password]):
            return error_response(400, '邮箱和密码不能为空')
        
        # 查找用户
        user = User.get_by_email(email)
        
        if not user:
            return error_response(401, '邮箱或密码错误')
        
        # 验证密码
        if not user.check_password(password):
            return error_response(401, '邮箱或密码错误')
        
        # 检查用户是否激活
        if not user.is_active:
            return error_response(401, '账号已被禁用')
        
        # 创建访问令牌（identity必须是字符串）
        access_token = create_access_token(identity=str(user.id))
        
        # 更新登录时间
        user.update_login_time()
        
        # 记录日志
        logger.info(f"用户登录成功: {user.username} ({email})")
        
        # 返回成功响应
        return success_response({
            'token': access_token,
            'user': user.to_dict()
        })
        
    except Exception as e:
        logger.error(f"登录失败: {str(e)}", exc_info=True)
        return error_response(500, '登录失败，请稍后重试')


@auth_bp.route('/logout', methods=['POST'])
@jwt_required()
def logout():
    """
    用户登出接口
    需要JWT认证
    """
    try:
        # 获取当前用户ID
        user_id = int(get_jwt_identity())
        
        # 这里可以将token加入黑名单（如果实现了token黑名单机制）
        # 目前简单返回成功
        
        # 记录日志
        logger.info(f"用户登出: user_id={user_id}")
        
        return success_response({'message': '登出成功'})
        
    except Exception as e:
        logger.error(f"登出失败: {str(e)}", exc_info=True)
        return error_response(500, '登出失败')


@auth_bp.route('/me', methods=['GET'])
@jwt_required()
def get_current_user():
    """
    获取当前用户信息
    需要JWT认证
    """
    try:
        # 获取当前用户ID
        user_id = int(get_jwt_identity())
        
        # 查找用户
        user = User.get_by_id(user_id)
        
        if not user:
            return error_response(404, '用户不存在')
        
        # 返回用户信息
        return success_response({
            'user': user.to_dict()
        })
        
    except Exception as e:
        logger.error(f"获取用户信息失败: {str(e)}", exc_info=True)
        return error_response(500, '获取用户信息失败')


@auth_bp.route('/change-password', methods=['POST'])
@jwt_required()
def change_password():
    """
    修改密码接口
    需要JWT认证
    
    请求体:
        {
            "old_password": "旧密码",
            "new_password": "新密码"
        }
    """
    try:
        # 获取当前用户
        user_id = int(get_jwt_identity())
        user = User.get_by_id(user_id)
        
        if not user:
            return error_response(404, '用户不存在')
        
        data = request.get_json()
        old_password = data.get('old_password')
        new_password = data.get('new_password')
        
        if not all([old_password, new_password]):
            return error_response(400, '旧密码和新密码不能为空')
        
        # 验证旧密码
        if not user.check_password(old_password):
            return error_response(401, '旧密码错误')
        
        # 设置新密码
        user.set_password(new_password)
        user.save()
        
        # 记录日志
        logger.info(f"用户修改密码: {user.username}")
        
        return success_response({'message': '密码修改成功'})
        
    except Exception as e:
        logger.error(f"修改密码失败: {str(e)}", exc_info=True)
        return error_response(500, '修改密码失败')


@auth_bp.route('/verify-token', methods=['GET'])
@jwt_required()
def verify_token():
    """
    验证Token有效性
    需要JWT认证
    """
    try:
        # 如果能到这里说明token有效
        user_id = int(get_jwt_identity())
        
        return success_response({
            'valid': True,
            'user_id': user_id
        })
        
    except Exception as e:
        logger.error(f"Token验证失败: {str(e)}", exc_info=True)
        return error_response(401, 'Token无效')