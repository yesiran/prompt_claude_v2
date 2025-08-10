# 修复标签更新事务管理问题

**日期**: 2025-08-09  
**类型**: Bug修复

## 问题描述

用户反馈：点击保存提示"保存失败"，但数据实际已写入数据库。

错误日志显示：
```
sqlalchemy.exc.IntegrityError: (pymysql.err.IntegrityError) (1062, "Duplicate entry '7-2' for key 'prompt_tags.uk_prompt_tag'")
```

## 问题分析

1. **根本原因**：标签更新逻辑存在事务管理问题
   - 原代码先删除所有旧标签（`pt.delete()`）
   - 然后添加新标签（`prompt.add_tag(tag_id)`）
   - `delete()` 方法内部会调用 `db.session.commit()`，过早提交事务
   - 导致在添加相同标签时产生重复键冲突

2. **为什么数据还能保存**：
   - Prompt内容和版本创建在标签处理之前已完成
   - 错误发生在标签更新阶段
   - 主要数据已经保存，只是标签部分失败

## 解决方案

修改 `app/api/prompts.py` 中的标签更新逻辑：

```python
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
            db.session.delete(pt)  # 只标记删除，不提交
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
            db.session.add(prompt_tag)  # 只添加到会话，不提交
            # 更新标签使用次数
            tag.increment_use_count()
    
    # 统一提交所有更改
    db.session.commit()
    
    # 刷新对象状态
    db.session.refresh(prompt)
```

## 关键改进

1. **差异化更新**：只处理真正需要改变的标签
   - 计算需要删除的标签：`tags_to_remove = set(current_tag_ids) - set(tag_ids)`
   - 计算需要添加的标签：`tags_to_add = set(tag_ids) - set(current_tag_ids)`
   - 保留的标签不做任何操作

2. **事务原子性**：所有操作在同一个事务中完成
   - 使用 `db.session.delete()` 和 `db.session.add()` 而不是调用模型的 `delete()` 和 `save()` 方法
   - 最后统一调用 `db.session.commit()`
   - 确保要么全部成功，要么全部失败

3. **避免重复键冲突**：
   - 不删除后重新添加相同的标签
   - 只处理真正变化的部分

## 测试验证

创建了专门的测试脚本 `test_tag_update.py`：

```bash
source prompt_claude_v2/bin/activate && python test_tag_update.py
```

测试结果：
- ✅ 标签添加正常
- ✅ 标签更新正常（保留、删除、添加）
- ✅ 重复更新不会报错
- ✅ 事务管理正确

## 影响范围

- 修复了Prompt更新时的标签处理逻辑
- 提高了事务的原子性和一致性
- 用户不会再看到"保存失败"的错误提示

## 后续建议

1. 考虑在所有涉及多表操作的地方统一事务管理策略
2. 避免在模型方法中直接提交事务，让调用者控制事务边界
3. 添加更多的集成测试，覆盖各种边界情况