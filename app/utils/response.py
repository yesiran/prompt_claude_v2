"""
响应工具模块
提供统一的API响应格式
"""

from flask import jsonify
from datetime import datetime


def success_response(data=None, code=200):
    """
    成功响应
    
    参数:
        data: 响应数据
        code: HTTP状态码
    
    返回:
        Flask响应对象
    """
    response = {
        'code': code,
        'message': 'success',
        'data': data,
        'timestamp': int(datetime.now().timestamp())
    }
    return jsonify(response), code


def error_response(code, message, errors=None):
    """
    错误响应
    
    参数:
        code: HTTP状态码
        message: 错误消息
        errors: 详细错误信息（可选）
    
    返回:
        Flask响应对象
    """
    response = {
        'code': code,
        'message': message,
        'timestamp': int(datetime.now().timestamp())
    }
    
    if errors:
        response['errors'] = errors
    
    return jsonify(response), code


def paginate_response(items, pagination):
    """
    分页响应
    
    参数:
        items: 数据项列表
        pagination: 分页信息对象
    
    返回:
        Flask响应对象
    """
    data = {
        'items': items,
        'pagination': {
            'page': pagination.page,
            'per_page': pagination.per_page,
            'total': pagination.total,
            'pages': pagination.pages
        }
    }
    
    return success_response(data)