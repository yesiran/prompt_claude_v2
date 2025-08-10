#!/usr/bin/env python3
"""
测试保存流程脚本
验证数据库连接和Prompt保存功能是否正常
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app import create_app
from app.models.base import db
from app.models.user import User
from app.models.prompt import Prompt, PromptVersion
from app.models.tag import Tag
from sqlalchemy import text
import json

def test_database_connection():
    """测试数据库连接"""
    print("=" * 50)
    print("1. 测试数据库连接...")
    
    try:
        # 执行简单查询
        result = db.session.execute(text('SELECT 1'))
        print("✅ 数据库连接成功")
        return True
    except Exception as e:
        print(f"❌ 数据库连接失败: {str(e)}")
        return False

def test_user_creation():
    """测试用户创建"""
    print("=" * 50)
    print("2. 测试用户创建...")
    
    try:
        # 检查是否已存在测试用户
        test_user = User.query.filter_by(email='test@example.com').first()
        
        if not test_user:
            # 创建测试用户
            test_user = User(
                username='testuser',
                email='test@example.com'
            )
            test_user.set_password('Test123456')  # 使用set_password方法设置密码
            db.session.add(test_user)
            db.session.commit()
            print("✅ 创建新测试用户成功")
        else:
            print("✅ 测试用户已存在")
        
        return test_user
    except Exception as e:
        print(f"❌ 用户操作失败: {str(e)}")
        db.session.rollback()
        return None

def test_prompt_save():
    """测试Prompt保存功能"""
    print("=" * 50)
    print("3. 测试Prompt保存功能...")
    
    try:
        # 获取测试用户
        test_user = User.query.filter_by(email='test@example.com').first()
        if not test_user:
            print("❌ 找不到测试用户")
            return False
        
        # 创建新的Prompt
        new_prompt = Prompt(
            title='测试Prompt标题',
            content='这是一个测试Prompt的内容，用于验证保存功能是否正常工作。',
            description='测试描述',
            author_id=test_user.id
        )
        
        db.session.add(new_prompt)
        db.session.commit()
        
        print(f"✅ Prompt保存成功，ID: {new_prompt.id}")
        
        # 创建版本记录
        version = PromptVersion(
            prompt_id=new_prompt.id,
            version_number=1,
            title=new_prompt.title,
            content=new_prompt.content,
            description=new_prompt.description,
            change_summary='初始版本',
            author_id=test_user.id
        )
        
        db.session.add(version)
        db.session.commit()
        
        print(f"✅ 版本记录创建成功，版本号: {version.version_number}")
        
        return new_prompt
    except Exception as e:
        print(f"❌ Prompt保存失败: {str(e)}")
        db.session.rollback()
        return None

def test_prompt_update():
    """测试Prompt更新功能"""
    print("=" * 50)
    print("4. 测试Prompt更新功能...")
    
    try:
        # 获取最新创建的Prompt
        test_user = User.query.filter_by(email='test@example.com').first()
        latest_prompt = Prompt.query.filter_by(author_id=test_user.id).order_by(Prompt.created_at.desc()).first()
        
        if not latest_prompt:
            print("❌ 找不到测试Prompt")
            return False
        
        # 更新Prompt
        latest_prompt.title = '更新后的标题'
        latest_prompt.content = '更新后的内容，验证更新功能是否正常。'
        
        # 创建新版本
        new_version = PromptVersion(
            prompt_id=latest_prompt.id,
            version_number=2,
            title=latest_prompt.title,
            content=latest_prompt.content,
            description=latest_prompt.description,
            change_summary='更新内容和标题',
            author_id=test_user.id
        )
        
        db.session.add(new_version)
        db.session.commit()
        
        print(f"✅ Prompt更新成功，新版本号: {new_version.version_number}")
        
        # 验证版本数量
        version_count = PromptVersion.query.filter_by(prompt_id=latest_prompt.id).count()
        print(f"✅ 当前Prompt共有 {version_count} 个版本")
        
        return True
    except Exception as e:
        print(f"❌ Prompt更新失败: {str(e)}")
        db.session.rollback()
        return False

def test_prompt_query():
    """测试Prompt查询功能"""
    print("=" * 50)
    print("5. 测试Prompt查询功能...")
    
    try:
        # 获取测试用户的所有Prompt
        test_user = User.query.filter_by(email='test@example.com').first()
        prompts = Prompt.query.filter_by(author_id=test_user.id, is_deleted=False).all()
        
        print(f"✅ 查询到 {len(prompts)} 个Prompt")
        
        for prompt in prompts:
            print(f"  - ID: {prompt.id}, 标题: {prompt.title}, 创建时间: {prompt.created_at}")
            
            # 获取版本信息
            versions = PromptVersion.query.filter_by(prompt_id=prompt.id).all()
            print(f"    版本数: {len(versions)}")
        
        return True
    except Exception as e:
        print(f"❌ Prompt查询失败: {str(e)}")
        return False

def main():
    """主测试函数"""
    print("\n" + "=" * 50)
    print("开始测试保存流程")
    print("=" * 50)
    
    # 创建应用上下文
    app = create_app('development')
    
    with app.app_context():
        # 运行测试
        results = []
        
        # 1. 测试数据库连接
        results.append(test_database_connection())
        
        if results[0]:
            # 2. 测试用户创建
            user = test_user_creation()
            results.append(user is not None)
            
            if results[1]:
                # 3. 测试Prompt保存
                prompt = test_prompt_save()
                results.append(prompt is not None)
                
                if results[2]:
                    # 4. 测试Prompt更新
                    results.append(test_prompt_update())
                    
                    # 5. 测试Prompt查询
                    results.append(test_prompt_query())
    
    # 输出测试结果总结
    print("\n" + "=" * 50)
    print("测试结果总结")
    print("=" * 50)
    
    test_names = [
        "数据库连接",
        "用户创建",
        "Prompt保存",
        "Prompt更新", 
        "Prompt查询"
    ]
    
    for i, (name, result) in enumerate(zip(test_names, results)):
        status = "✅ 通过" if result else "❌ 失败"
        print(f"{i+1}. {name}: {status}")
    
    # 总体结果
    if all(results):
        print("\n🎉 所有测试通过！保存流程工作正常。")
    else:
        print("\n⚠️ 部分测试失败，请检查相关功能。")
    
    return all(results)

if __name__ == '__main__':
    success = main()
    sys.exit(0 if success else 1)