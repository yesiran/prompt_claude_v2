# 修复版本号重复导致的500错误

**日期**: 2025-08-09  
**类型**: Bug修复

## 问题描述

用户在保存包含标签的Prompt时，遇到500内部服务器错误。错误日志显示：
```
sqlalchemy.exc.IntegrityError: (MySQLdb.IntegrityError) (1062, "Duplicate entry '8-3' for key 'prompt_versions.uk_prompt_version'")
```

## 问题分析

1. **根本原因**: 版本号生成时使用了ORM关系查询（`self.versions`），这会使用SQLAlchemy的缓存机制，导致在同一个会话中多次调用时可能获取到过时的版本号。

2. **触发条件**: 
   - 更新Prompt时创建新版本
   - 在同一个数据库会话中，ORM缓存导致版本号计算错误
   - 尝试插入重复的版本号触发唯一约束冲突

## 解决方案

### 1. 修改版本号生成逻辑 (app/models/prompt.py)

使用直接的SQL查询（`func.max()`）替代ORM关系查询，避免缓存问题：

```python
def create_version(self, title=None, content=None, description=None, 
                  change_summary=None, author_id=None):
    # 使用数据库查询获取最大版本号，避免缓存问题
    from sqlalchemy import func
    max_version = db.session.query(func.max(PromptVersion.version_number)).filter(
        PromptVersion.prompt_id == self.id
    ).scalar()
    
    # 计算下一个版本号
    next_version_number = (max_version + 1) if max_version else 1
    
    # 创建版本记录
    version = PromptVersion(
        prompt_id=self.id,
        version_number=next_version_number,
        # ... 其他字段
    )
    version.save()
    
    # 更新版本计数
    self.version_count = next_version_number
    self.save()
    
    return version
```

### 2. 添加重试机制 (app/api/prompts.py)

在更新Prompt时添加重试机制，处理并发冲突：

```python
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
```

## 测试验证

运行测试脚本 `test_save_flow.py` 验证修复效果：

```bash
source prompt_claude_v2/bin/activate && python test_save_flow.py
```

测试结果：
- ✅ 数据库连接成功
- ✅ Prompt保存成功
- ✅ 版本记录创建成功
- ✅ Prompt更新成功，版本号正确递增
- ✅ 所有测试通过

## 影响范围

- 修复了所有涉及Prompt版本创建的操作
- 提高了并发处理的健壮性
- 不影响现有功能的使用

## 后续建议

1. 考虑使用数据库级别的序列或自增字段来生成版本号
2. 监控版本创建的性能，确保在高并发场景下的稳定性
3. 可以考虑添加分布式锁机制来处理更复杂的并发场景