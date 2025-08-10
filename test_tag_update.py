#!/usr/bin/env python3
"""
测试标签更新功能
验证修复后的标签更新逻辑是否正常工作
"""

from app import create_app
from app.models.prompt import Prompt
from app.models.tag import Tag, PromptTag
from app.models.user import User
from app.models.base import db

def test_tag_update():
    """测试标签更新功能"""
    app = create_app()
    
    with app.app_context():
        print("="*50)
        print("测试标签更新功能")
        print("="*50)
        
        # 1. 获取测试用户
        test_user = User.query.filter_by(email='test@example.com').first()
        if not test_user:
            print("❌ 测试用户不存在")
            return
        print(f"✅ 测试用户: {test_user.username}")
        
        # 2. 创建测试Prompt
        test_prompt = Prompt(
            title="标签测试Prompt",
            content="用于测试标签更新功能",
            description="测试描述",
            author_id=test_user.id
        )
        test_prompt.save()
        prompt_id = test_prompt.id
        print(f"✅ 创建测试Prompt，ID: {prompt_id}")
        
        # 3. 获取可用标签
        tags = Tag.query.limit(3).all()
        if len(tags) < 2:
            print("❌ 标签数量不足，需要至少2个标签")
            return
        
        tag1, tag2, tag3 = tags[0], tags[1], tags[2] if len(tags) > 2 else tags[1]
        print(f"✅ 获取标签: {tag1.name}, {tag2.name}, {tag3.name if tag3 else 'N/A'}")
        
        # 4. 添加初始标签
        print("\n步骤1: 添加初始标签")
        test_prompt.add_tag(tag1.id)
        test_prompt.add_tag(tag2.id)
        
        # 验证标签添加
        current_tags = PromptTag.query.filter_by(prompt_id=prompt_id).all()
        print(f"  当前标签数: {len(current_tags)}")
        print(f"  标签ID: {[pt.tag_id for pt in current_tags]}")
        
        # 5. 模拟更新操作（保留一个，删除一个，添加一个）
        print("\n步骤2: 更新标签（保留tag1，删除tag2，添加tag3）")
        
        # 获取当前标签ID列表
        current_tag_ids = [pt.tag_id for pt in test_prompt.prompt_tags]
        new_tag_ids = [tag1.id, tag3.id]  # 保留tag1，添加tag3
        
        # 计算需要删除和添加的标签
        tags_to_remove = set(current_tag_ids) - set(new_tag_ids)
        tags_to_add = set(new_tag_ids) - set(current_tag_ids)
        
        print(f"  需要删除的标签ID: {list(tags_to_remove)}")
        print(f"  需要添加的标签ID: {list(tags_to_add)}")
        
        # 删除不需要的标签
        for tag_id in tags_to_remove:
            pt = PromptTag.query.filter_by(
                prompt_id=prompt_id,
                tag_id=tag_id
            ).first()
            if pt:
                db.session.delete(pt)
                print(f"  删除标签关联: prompt_id={prompt_id}, tag_id={tag_id}")
        
        # 添加新标签
        for tag_id in tags_to_add:
            tag = Tag.get_by_id(tag_id)
            if tag:
                prompt_tag = PromptTag(
                    prompt_id=prompt_id,
                    tag_id=tag_id
                )
                db.session.add(prompt_tag)
                print(f"  添加标签关联: prompt_id={prompt_id}, tag_id={tag_id}")
        
        # 提交事务
        db.session.commit()
        print("  ✅ 标签更新成功")
        
        # 6. 验证更新结果
        print("\n步骤3: 验证更新结果")
        db.session.refresh(test_prompt)
        final_tags = PromptTag.query.filter_by(prompt_id=prompt_id).all()
        print(f"  最终标签数: {len(final_tags)}")
        print(f"  标签ID: {[pt.tag_id for pt in final_tags]}")
        
        # 7. 测试重复更新（使用相同的标签）
        print("\n步骤4: 测试重复更新（使用相同的标签）")
        try:
            # 再次使用相同的标签进行更新
            current_tag_ids = [pt.tag_id for pt in final_tags]
            new_tag_ids = current_tag_ids  # 使用相同的标签
            
            tags_to_remove = set(current_tag_ids) - set(new_tag_ids)
            tags_to_add = set(new_tag_ids) - set(current_tag_ids)
            
            print(f"  需要删除的标签ID: {list(tags_to_remove)} (应该为空)")
            print(f"  需要添加的标签ID: {list(tags_to_add)} (应该为空)")
            
            # 由于没有变化，不需要执行任何操作
            if not tags_to_remove and not tags_to_add:
                print("  ✅ 标签未变化，无需更新")
            
            db.session.commit()
            print("  ✅ 重复更新测试通过")
            
        except Exception as e:
            print(f"  ❌ 重复更新失败: {str(e)}")
            db.session.rollback()
        
        # 8. 清理测试数据
        print("\n步骤5: 清理测试数据")
        # 删除测试标签关联
        PromptTag.query.filter_by(prompt_id=prompt_id).delete()
        # 删除测试Prompt
        Prompt.query.filter_by(id=prompt_id).delete()
        db.session.commit()
        print("  ✅ 测试数据已清理")
        
        print("\n" + "="*50)
        print("🎉 标签更新功能测试完成！")
        print("="*50)

if __name__ == "__main__":
    test_tag_update()