"""
标签API
处理标签相关的接口
"""

from flask import Blueprint, request
from flask_jwt_extended import jwt_required, get_jwt_identity

from app.models.tag import Tag
from app.models.base import db
from app.utils.logger import get_logger
from app.utils.response import success_response, error_response

# 创建蓝图
tags_bp = Blueprint('tags', __name__)

# 获取日志记录器
logger = get_logger('tags')


@tags_bp.route('', methods=['GET'])
@jwt_required()
def get_tags():
    """
    获取所有标签
    """
    try:
        # 获取查询参数
        category = request.args.get('category')
        
        # 查询标签
        if category:
            tags = Tag.get_by_category(category)
        else:
            tags = Tag.get_all()
        
        # 构建响应数据
        data = [tag.to_dict() for tag in tags]
        
        return success_response(data)
        
    except Exception as e:
        logger.error(f"获取标签列表失败: {str(e)}", exc_info=True)
        return error_response(500, '获取标签列表失败')


@tags_bp.route('/popular', methods=['GET'])
@jwt_required()
def get_popular_tags():
    """
    获取热门标签
    """
    try:
        # 获取限制数量
        limit = request.args.get('limit', 10, type=int)
        
        # 获取热门标签
        tags = Tag.get_popular(limit)
        
        # 构建响应数据
        data = [tag.to_dict() for tag in tags]
        
        return success_response(data)
        
    except Exception as e:
        logger.error(f"获取热门标签失败: {str(e)}", exc_info=True)
        return error_response(500, '获取热门标签失败')


@tags_bp.route('', methods=['POST'])
@jwt_required()
def create_tag():
    """
    创建新标签
    """
    try:
        user_id = int(get_jwt_identity())
        data = request.get_json()
        
        # 参数验证
        name = data.get('name', '').strip()
        category = data.get('category', 'general')
        color = data.get('color', '#6B7280')
        
        if not name:
            return error_response(400, '标签名称不能为空')
        
        # 创建或获取标签
        tag = Tag.create_or_get(
            name=name,
            category=category,
            color=color,
            created_by=user_id
        )
        
        # 记录日志
        logger.info(f"创建标签: {tag.name}")
        
        return success_response(tag.to_dict(), 201)
        
    except Exception as e:
        logger.error(f"创建标签失败: {str(e)}", exc_info=True)
        return error_response(500, '创建标签失败')


@tags_bp.route('/<int:tag_id>', methods=['DELETE'])
@jwt_required()
def delete_tag(tag_id):
    """
    删除标签
    注意：根据产品设计，标签是轻量级的，任何用户都可以删除未被使用的标签
    如果标签正在被使用，则需要提示用户
    """
    try:
        user_id = int(get_jwt_identity())
        
        # 获取标签
        tag = Tag.get_by_id(tag_id)
        
        if not tag:
            return error_response(404, '标签不存在')
        
        # 检查标签是否被使用
        if tag.use_count > 0:
            return error_response(400, f'标签正在被 {tag.use_count} 个Prompt使用，无法删除')
        
        # 删除标签
        tag.delete()
        
        # 记录日志
        logger.info(f"用户 {user_id} 删除标签: {tag.name}")
        
        return success_response({'message': '删除成功'})
        
    except Exception as e:
        logger.error(f"删除标签失败: {str(e)}", exc_info=True)
        return error_response(500, '删除标签失败')