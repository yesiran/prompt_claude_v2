"""
用户API
处理用户设置等用户相关接口
"""

from flask import Blueprint, request
from flask_jwt_extended import jwt_required, get_jwt_identity

from app.models.user import User
from app.models.user_setting import UserSetting
from app.models.base import db
from app.utils.logger import get_logger
from app.utils.response import success_response, error_response

# 创建蓝图
users_bp = Blueprint('users', __name__)

# 获取日志记录器
logger = get_logger('users')


@users_bp.route('/settings', methods=['GET'])
@jwt_required()
def get_user_settings():
    """
    获取用户设置
    """
    try:
        user_id = int(get_jwt_identity())
        
        # 获取用户设置
        settings = UserSetting.get_user_settings(user_id)
        
        if not settings:
            # 创建默认设置
            settings = UserSetting.create_default_settings(user_id)
        
        return success_response(settings.to_dict())
        
    except Exception as e:
        logger.error(f"获取用户设置失败: {str(e)}", exc_info=True)
        return error_response(500, '获取用户设置失败')


@users_bp.route('/settings', methods=['PUT'])
@jwt_required()
def update_user_settings():
    """
    更新用户设置
    """
    try:
        user_id = int(get_jwt_identity())
        data = request.get_json()
        
        # 获取用户设置
        settings = UserSetting.get_user_settings(user_id)
        
        if not settings:
            settings = UserSetting.create_default_settings(user_id)
        
        # 更新设置
        if 'background_music' in data:
            settings.update_background_music(data['background_music'])
        
        if 'background_image' in data:
            settings.background_image = data['background_image']
        
        if 'editor_theme' in data:
            settings.update_theme(data['editor_theme'])
        
        if 'auto_save_interval' in data:
            settings.auto_save_interval = data['auto_save_interval']
        
        if 'default_model' in data:
            settings.default_model = data['default_model']
        
        if 'notification_enabled' in data:
            settings.notification_enabled = data['notification_enabled']
        
        if 'keyboard_shortcuts' in data:
            settings.keyboard_shortcuts = data['keyboard_shortcuts']
        
        settings.save()
        
        # 记录日志
        logger.info(f"更新用户设置: user_id={user_id}")
        
        return success_response(settings.to_dict())
        
    except Exception as e:
        logger.error(f"更新用户设置失败: {str(e)}", exc_info=True)
        return error_response(500, '更新用户设置失败')


@users_bp.route('/profile', methods=['GET'])
@jwt_required()
def get_user_profile():
    """
    获取用户个人资料
    """
    try:
        user_id = int(get_jwt_identity())
        
        # 获取用户
        user = User.get_by_id(user_id)
        
        if not user:
            return error_response(404, '用户不存在')
        
        # 构建响应数据
        data = user.to_dict()
        data['prompts_count'] = user.get_prompts_count()
        
        return success_response(data)
        
    except Exception as e:
        logger.error(f"获取用户资料失败: {str(e)}", exc_info=True)
        return error_response(500, '获取用户资料失败')


@users_bp.route('/profile', methods=['PUT'])
@jwt_required()
def update_user_profile():
    """
    更新用户个人资料
    """
    try:
        user_id = int(get_jwt_identity())
        data = request.get_json()
        
        # 获取用户
        user = User.get_by_id(user_id)
        
        if not user:
            return error_response(404, '用户不存在')
        
        # 更新资料
        if 'username' in data:
            # 检查用户名是否已被使用
            username = data['username'].strip()
            existing = User.get_by_username(username)
            if existing and existing.id != user_id:
                return error_response(400, '用户名已被使用')
            user.username = username
        
        if 'avatar_url' in data:
            user.avatar_url = data['avatar_url']
        
        if 'theme_preference' in data:
            user.theme_preference = data['theme_preference']
        
        user.save()
        
        # 记录日志
        logger.info(f"更新用户资料: {user.username}")
        
        return success_response(user.to_dict())
        
    except Exception as e:
        logger.error(f"更新用户资料失败: {str(e)}", exc_info=True)
        return error_response(500, '更新用户资料失败')