"""
Prompt API
处理Prompt相关的所有接口
"""

from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity

from app.models.prompt import Prompt, PromptVersion
from app.models.tag import Tag, PromptTag
from app.models.base import db
from app.utils.logger import get_logger
from app.utils.response import success_response, error_response, paginate_response

# 创建蓝图
prompts_bp = Blueprint('prompts', __name__)

# 获取日志记录器
logger = get_logger('prompts')


@prompts_bp.route('', methods=['GET'])
@jwt_required()
def get_prompts():
    """
    获取Prompt列表
    支持分页、搜索、标签筛选
    """
    try:
        # 获取查询参数
        page = request.args.get('page', 1, type=int)
        limit = request.args.get('limit', 20, type=int)
        search = request.args.get('search', '')
        tags = request.args.get('tags', '')
        sort = request.args.get('sort', 'created_at')
        order = request.args.get('order', 'desc')
        
        # 获取当前用户ID
        user_id = int(get_jwt_identity())
        
        # 构建查询
        query = Prompt.query.filter_by(author_id=user_id, is_deleted=False)
        
        # 搜索
        if search:
            query = Prompt.search(search, author_id=user_id)
        
        # 标签筛选
        if tags:
            tag_ids = [int(t) for t in tags.split(',') if t.isdigit()]
            if tag_ids:
                from app.models.tag import PromptTag
                query = query.join(PromptTag).filter(PromptTag.tag_id.in_(tag_ids))
        
        # 排序
        if sort == 'updated_at':
            query = query.order_by(Prompt.updated_at.desc() if order == 'desc' else Prompt.updated_at.asc())
        elif sort == 'star_count':
            query = query.order_by(Prompt.star_count.desc() if order == 'desc' else Prompt.star_count.asc())
        else:
            query = query.order_by(Prompt.created_at.desc() if order == 'desc' else Prompt.created_at.asc())
        
        # 分页
        pagination = query.paginate(page=page, per_page=limit, error_out=False)
        
        # 构建响应数据
        items = []
        for prompt in pagination.items:
            item = prompt.to_dict(include_tags=True, include_author=True)
            item['stats'] = {
                'view_count': prompt.view_count,
                'test_count': prompt.test_count,
                'star_count': prompt.star_count,
                'version_count': prompt.version_count
            }
            items.append(item)
        
        return paginate_response(items, pagination)
        
    except Exception as e:
        logger.error(f"获取Prompt列表失败: {str(e)}", exc_info=True)
        return error_response(500, '获取Prompt列表失败')


@prompts_bp.route('/<int:prompt_id>', methods=['GET'])
@jwt_required()
def get_prompt(prompt_id):
    """
    获取单个Prompt详情
    """
    try:
        user_id = int(get_jwt_identity())
        
        # 获取Prompt
        prompt = Prompt.get_by_id(prompt_id)
        
        if not prompt or prompt.is_deleted:
            return error_response(404, 'Prompt不存在')
        
        # 检查权限
        from app.models.user import User
        user = User.get_by_id(user_id)
        if not user.has_permission(prompt_id, 'read'):
            return error_response(403, '无权限访问此Prompt')
        
        # 增加查看次数
        prompt.increment_view_count()
        
        # 构建响应数据
        data = prompt.to_dict(include_tags=True, include_author=True)
        
        # 添加当前版本信息
        current_version = prompt.get_current_version()
        if current_version:
            data['current_version'] = {
                'id': current_version.id,
                'version_number': current_version.version_number,
                'created_at': current_version.created_at.isoformat()
            }
        
        # 添加协作者信息
        collaborators = []
        for collab in prompt.collaborations:
            collaborators.append({
                'id': collab.user.id,
                'username': collab.user.username,
                'permission': collab.permission
            })
        data['collaborators'] = collaborators
        
        # 添加统计信息
        data['stats'] = {
            'view_count': prompt.view_count,
            'test_count': prompt.test_count,
            'star_count': prompt.star_count,
            'version_count': prompt.version_count
        }
        
        return success_response(data)
        
    except Exception as e:
        logger.error(f"获取Prompt详情失败: {str(e)}", exc_info=True)
        return error_response(500, '获取Prompt详情失败')


@prompts_bp.route('', methods=['POST'])
@jwt_required()
def create_prompt():
    """
    创建新的Prompt
    """
    try:
        user_id = int(get_jwt_identity())
        data = request.get_json()
        
        # 参数验证
        title = data.get('title', '').strip()
        content = data.get('content', '').strip()
        description = data.get('description', '').strip()
        tag_ids = data.get('tags', [])
        
        if not title:
            return error_response(400, '标题不能为空')
        
        if not content:
            return error_response(400, '内容不能为空')
        
        # 创建Prompt
        prompt = Prompt(
            title=title,
            content=content,
            description=description,
            author_id=user_id
        )
        prompt.save()
        
        # 创建初始版本
        prompt.create_version(
            title=title,
            content=content,
            description=description,
            change_summary='初始版本',
            author_id=user_id
        )
        
        # 添加标签
        for tag_id in tag_ids:
            prompt.add_tag(tag_id)
        
        # 记录日志
        logger.info(f"创建Prompt: {prompt.id} - {title}")
        
        return success_response(prompt.to_dict(include_tags=True), 201)
        
    except Exception as e:
        logger.error(f"创建Prompt失败: {str(e)}", exc_info=True)
        return error_response(500, '创建Prompt失败')


@prompts_bp.route('/<int:prompt_id>', methods=['PUT'])
@jwt_required()
def update_prompt(prompt_id):
    """
    更新Prompt
    """
    try:
        user_id = int(get_jwt_identity())
        data = request.get_json()
        
        # 获取Prompt
        prompt = Prompt.get_by_id(prompt_id)
        
        if not prompt or prompt.is_deleted:
            return error_response(404, 'Prompt不存在')
        
        # 检查权限
        from app.models.user import User
        user = User.get_by_id(user_id)
        if not user.has_permission(prompt_id, 'write'):
            return error_response(403, '无权限编辑此Prompt')
        
        # 获取更新数据
        title = data.get('title', prompt.title).strip()
        content = data.get('content', prompt.content).strip()
        description = data.get('description', prompt.description)
        tag_ids = data.get('tags')
        change_summary = data.get('change_summary', '')
        
        # 检查是否有实际变更
        has_change = (
            title != prompt.title or
            content != prompt.content or
            description != prompt.description
        )
        
        if has_change:
            # 创建新版本（带重试机制处理并发冲突）
            from sqlalchemy.exc import IntegrityError
            retry_count = 0
            max_retries = 3
            
            while retry_count < max_retries:
                try:
                    prompt.create_version(
                        title=title,
                        content=content,
                        description=description,
                        change_summary=change_summary or '更新内容',
                        author_id=user_id
                    )
                    
                    # 更新主记录
                    prompt.title = title
                    prompt.content = content
                    prompt.description = description
                    prompt.save()
                    break  # 成功则退出循环
                    
                except IntegrityError as e:
                    # 版本号冲突，重试
                    db.session.rollback()
                    retry_count += 1
                    if retry_count >= max_retries:
                        logger.error(f"版本创建失败（重试{max_retries}次后）: {str(e)}")
                        return error_response(500, '版本创建失败，请稍后重试')
                    logger.warning(f"版本号冲突，重试第{retry_count}次")
        
        # 更新标签
        if tag_ids is not None:
            # 获取当前标签ID列表
            current_tag_ids = [pt.tag_id for pt in prompt.prompt_tags]
            
            # 计算需要删除和添加的标签
            tags_to_remove = set(current_tag_ids) - set(tag_ids)
            tags_to_add = set(tag_ids) - set(current_tag_ids)
            
            # 移除不需要的标签（不提交事务）
            for tag_id in tags_to_remove:
                pt = PromptTag.query.filter_by(
                    prompt_id=prompt.id,
                    tag_id=tag_id
                ).first()
                if pt:
                    db.session.delete(pt)
                    # 更新标签使用次数
                    tag = Tag.get_by_id(tag_id)
                    if tag:
                        tag.decrement_use_count()
            
            # 添加新标签（不提交事务）
            for tag_id in tags_to_add:
                tag = Tag.get_by_id(tag_id)
                if tag:
                    prompt_tag = PromptTag(
                        prompt_id=prompt.id,
                        tag_id=tag_id
                    )
                    db.session.add(prompt_tag)
                    # 更新标签使用次数
                    tag.increment_use_count()
            
            # 统一提交所有更改
            db.session.commit()
            
            # 刷新对象状态，确保标签关联正确加载
            db.session.refresh(prompt)
        
        # 记录日志
        logger.info(f"更新Prompt: {prompt.id}")
        
        return success_response(prompt.to_dict(include_tags=True))
        
    except Exception as e:
        logger.error(f"更新Prompt失败: {str(e)}", exc_info=True)
        return error_response(500, '更新Prompt失败')


@prompts_bp.route('/<int:prompt_id>', methods=['DELETE'])
@jwt_required()
def delete_prompt(prompt_id):
    """
    删除Prompt（软删除）
    """
    try:
        user_id = int(get_jwt_identity())
        
        # 获取Prompt
        prompt = Prompt.get_by_id(prompt_id)
        
        if not prompt or prompt.is_deleted:
            return error_response(404, 'Prompt不存在')
        
        # 检查权限（只有作者可以删除）
        if prompt.author_id != user_id:
            return error_response(403, '无权限删除此Prompt')
        
        # 软删除
        prompt.soft_delete()
        
        # 记录日志
        logger.info(f"删除Prompt: {prompt.id}")
        
        return success_response({'message': '删除成功'}, 204)
        
    except Exception as e:
        logger.error(f"删除Prompt失败: {str(e)}", exc_info=True)
        return error_response(500, '删除Prompt失败')


@prompts_bp.route('/<int:prompt_id>/autosave', methods=['POST'])
@jwt_required()
def autosave_prompt(prompt_id):
    """
    自动保存Prompt（不创建新版本）
    """
    try:
        user_id = int(get_jwt_identity())
        data = request.get_json()
        
        # 获取Prompt
        prompt = Prompt.get_by_id(prompt_id)
        
        if not prompt or prompt.is_deleted:
            return error_response(404, 'Prompt不存在')
        
        # 检查权限
        from app.models.user import User
        user = User.get_by_id(user_id)
        if not user.has_permission(prompt_id, 'write'):
            return error_response(403, '无权限编辑此Prompt')
        
        # 更新内容（不创建版本）
        if 'title' in data:
            prompt.title = data['title'].strip()
        if 'content' in data:
            prompt.content = data['content'].strip()
        
        prompt.save()
        
        return success_response({'message': '自动保存成功'})
        
    except Exception as e:
        logger.error(f"自动保存失败: {str(e)}", exc_info=True)
        return error_response(500, '自动保存失败')


@prompts_bp.route('/<int:prompt_id>/versions', methods=['GET'])
@jwt_required()
def get_prompt_versions(prompt_id):
    """
    获取Prompt的版本历史
    """
    try:
        user_id = int(get_jwt_identity())
        
        # 获取Prompt
        prompt = Prompt.get_by_id(prompt_id)
        
        if not prompt or prompt.is_deleted:
            return error_response(404, 'Prompt不存在')
        
        # 检查权限
        from app.models.user import User
        user = User.get_by_id(user_id)
        if not user.has_permission(prompt_id, 'read'):
            return error_response(403, '无权限访问此Prompt')
        
        # 获取查询参数
        page = request.args.get('page', 1, type=int)
        limit = request.args.get('limit', 20, type=int)
        
        # 获取版本列表
        versions = prompt.versions.paginate(page=page, per_page=limit, error_out=False)
        
        # 构建响应数据
        items = []
        for version in versions.items:
            items.append({
                'id': version.id,
                'version_number': version.version_number,
                'title': version.title,
                'change_summary': version.change_summary,
                'author': {
                    'id': version.version_author.id,
                    'username': version.version_author.username
                },
                'created_at': version.created_at.isoformat()
            })
        
        return paginate_response(items, versions)
        
    except Exception as e:
        logger.error(f"获取版本历史失败: {str(e)}", exc_info=True)
        return error_response(500, '获取版本历史失败')


@prompts_bp.route('/<int:prompt_id>/versions/<int:version_id>', methods=['GET'])
@jwt_required()
def get_prompt_version(prompt_id, version_id):
    """
    获取特定版本的详情
    """
    try:
        user_id = int(get_jwt_identity())
        
        # 获取Prompt
        prompt = Prompt.get_by_id(prompt_id)
        
        if not prompt or prompt.is_deleted:
            return error_response(404, 'Prompt不存在')
        
        # 检查权限
        from app.models.user import User
        user = User.get_by_id(user_id)
        if not user.has_permission(prompt_id, 'read'):
            return error_response(403, '无权限访问此Prompt')
        
        # 获取版本
        from app.models.prompt import PromptVersion
        version = PromptVersion.get_by_id(version_id)
        
        if not version or version.prompt_id != prompt_id:
            return error_response(404, '版本不存在')
        
        # 构建响应数据
        data = {
            'id': version.id,
            'version_number': version.version_number,
            'title': version.title,
            'content': version.content,
            'description': version.description,
            'change_summary': version.change_summary,
            'author': {
                'id': version.version_author.id,
                'username': version.version_author.username
            },
            'created_at': version.created_at.isoformat()
        }
        
        return success_response(data)
        
    except Exception as e:
        logger.error(f"获取版本详情失败: {str(e)}", exc_info=True)
        return error_response(500, '获取版本详情失败')


@prompts_bp.route('/<int:prompt_id>/test', methods=['POST'])
@jwt_required()
def test_prompt(prompt_id):
    """
    测试Prompt
    """
    try:
        user_id = int(get_jwt_identity())
        data = request.get_json()
        
        # 获取Prompt
        prompt = Prompt.get_by_id(prompt_id)
        
        if not prompt or prompt.is_deleted:
            return error_response(404, 'Prompt不存在')
        
        # 检查权限
        from app.models.user import User
        user = User.get_by_id(user_id)
        if not user.has_permission(prompt_id, 'read'):
            return error_response(403, '无权限访问此Prompt')
        
        # 获取测试参数
        model = data.get('model', 'gpt-5')
        test_input = data.get('input', '')
        parameters = data.get('parameters', {})
        
        # TODO: 这里应该调用实际的AI API
        # 目前返回模拟数据
        import time
        import random
        
        # 模拟响应时间
        response_time = round(random.uniform(0.5, 2.0), 3)
        time.sleep(0.5)  # 模拟网络延迟
        
        # 模拟响应
        test_output = f"这是{model}模型的测试响应。\n\nPrompt内容：\n{prompt.content}\n\n"
        if test_input:
            test_output += f"测试输入：\n{test_input}\n\n"
        test_output += "模拟输出：这是一个模拟的AI响应，实际使用时会调用真实的AI API。"
        
        # 记录测试
        from app.models.test_record import TestRecord
        test_record = TestRecord(
            prompt_id=prompt_id,
            user_id=user_id,
            model_name=model,
            model_params=parameters,
            input_tokens=len(prompt.content.split()) + len(test_input.split()),
            output_tokens=len(test_output.split()),
            response_time=response_time,
            test_input=test_input,
            test_output=test_output,
            status='success'
        )
        test_record.save()
        
        # 更新Prompt测试次数
        prompt.increment_test_count()
        
        # 返回结果
        return success_response({
            'test_id': test_record.id,
            'model': model,
            'input': test_input,
            'output': test_output,
            'tokens': {
                'input': test_record.input_tokens,
                'output': test_record.output_tokens
            },
            'response_time': response_time,
            'created_at': test_record.created_at.isoformat()
        })
        
    except Exception as e:
        logger.error(f"测试Prompt失败: {str(e)}", exc_info=True)
        return error_response(500, '测试失败')