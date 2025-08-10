# 后端API设计方案

## 设计原则
- **RESTful风格**：遵循REST架构约束
- **一致性**：统一的响应格式和错误处理
- **简洁性**：URL设计简洁明了
- **安全性**：适当的认证和授权机制

## API基础规范

### 1. 基础URL
```
http://localhost:5000/api/v1
```

### 2. 响应格式
```json
{
    "code": 200,           // 状态码
    "message": "success",  // 消息
    "data": {},           // 数据
    "timestamp": 1234567890 // 时间戳
}
```

### 3. 错误响应
```json
{
    "code": 400,
    "message": "错误描述",
    "errors": {           // 详细错误信息（可选）
        "field": "错误详情"
    },
    "timestamp": 1234567890
}
```

### 4. HTTP状态码
- 200: 成功
- 201: 创建成功
- 204: 删除成功
- 400: 请求错误
- 401: 未认证
- 403: 无权限
- 404: 资源不存在
- 500: 服务器错误

## API接口定义

### 1. 认证接口

#### 1.1 用户注册
```
POST /api/v1/auth/register
```
请求体：
```json
{
    "username": "string",
    "email": "string",
    "password": "string"
}
```

#### 1.2 用户登录
```
POST /api/v1/auth/login
```
请求体：
```json
{
    "email": "string",
    "password": "string"
}
```
响应：
```json
{
    "code": 200,
    "data": {
        "token": "jwt_token",
        "user": {
            "id": 1,
            "username": "string",
            "email": "string"
        }
    }
}
```

#### 1.3 登出
```
POST /api/v1/auth/logout
Headers: Authorization: Bearer {token}
```

### 2. Prompt管理接口

#### 2.1 获取Prompt列表
```
GET /api/v1/prompts
```
查询参数：
- page: 页码（默认1）
- limit: 每页数量（默认20）
- search: 搜索关键词
- tags: 标签ID列表（逗号分隔）
- sort: 排序字段（created_at, updated_at, star_count）
- order: 排序方向（asc, desc）

响应：
```json
{
    "code": 200,
    "data": {
        "items": [
            {
                "id": 1,
                "title": "Prompt标题",
                "description": "描述",
                "content": "内容预览（前200字）",
                "tags": [
                    {"id": 1, "name": "工作", "color": "#3B82F6"}
                ],
                "author": {
                    "id": 1,
                    "username": "user1"
                },
                "stats": {
                    "view_count": 10,
                    "test_count": 5,
                    "star_count": 3,
                    "version_count": 2
                },
                "created_at": "2025-01-01T00:00:00Z",
                "updated_at": "2025-01-02T00:00:00Z"
            }
        ],
        "pagination": {
            "page": 1,
            "limit": 20,
            "total": 100,
            "pages": 5
        }
    }
}
```

#### 2.2 获取单个Prompt详情
```
GET /api/v1/prompts/{id}
```
响应：
```json
{
    "code": 200,
    "data": {
        "id": 1,
        "title": "Prompt标题",
        "content": "完整内容",
        "description": "描述",
        "tags": [...],
        "author": {...},
        "collaborators": [
            {
                "id": 2,
                "username": "user2",
                "permission": "write"
            }
        ],
        "current_version": {
            "id": 10,
            "version_number": 3,
            "created_at": "2025-01-02T00:00:00Z"
        },
        "stats": {...},
        "created_at": "2025-01-01T00:00:00Z",
        "updated_at": "2025-01-02T00:00:00Z"
    }
}
```

#### 2.3 创建Prompt
```
POST /api/v1/prompts
```
请求体：
```json
{
    "title": "string",
    "content": "string",
    "description": "string",
    "tags": [1, 2, 3]  // 标签ID数组
}
```

#### 2.4 更新Prompt
```
PUT /api/v1/prompts/{id}
```
请求体：
```json
{
    "title": "string",
    "content": "string",
    "description": "string",
    "tags": [1, 2, 3],
    "change_summary": "修改摘要"  // 版本变更说明
}
```

#### 2.5 删除Prompt
```
DELETE /api/v1/prompts/{id}
```

#### 2.6 自动保存（草稿）
```
POST /api/v1/prompts/{id}/autosave
```
请求体：
```json
{
    "content": "string",
    "title": "string"
}
```
说明：此接口用于实时保存，不创建新版本

### 3. 版本管理接口

#### 3.1 获取版本历史
```
GET /api/v1/prompts/{id}/versions
```
查询参数：
- page: 页码
- limit: 每页数量

响应：
```json
{
    "code": 200,
    "data": {
        "items": [
            {
                "id": 10,
                "version_number": 3,
                "title": "版本标题",
                "change_summary": "修改摘要",
                "author": {
                    "id": 1,
                    "username": "user1"
                },
                "created_at": "2025-01-02T00:00:00Z"
            }
        ],
        "pagination": {...}
    }
}
```

#### 3.2 获取特定版本详情
```
GET /api/v1/prompts/{id}/versions/{version_id}
```

#### 3.3 版本对比
```
GET /api/v1/prompts/{id}/versions/compare
```
查询参数：
- from: 起始版本ID
- to: 目标版本ID

响应：
```json
{
    "code": 200,
    "data": {
        "from": {
            "id": 9,
            "version_number": 2,
            "content": "旧内容"
        },
        "to": {
            "id": 10,
            "version_number": 3,
            "content": "新内容"
        },
        "diff": {
            "added": ["新增的行"],
            "removed": ["删除的行"],
            "modified": ["修改的行"]
        }
    }
}
```

#### 3.4 回滚版本
```
POST /api/v1/prompts/{id}/versions/{version_id}/rollback
```

### 4. 标签管理接口

#### 4.1 获取所有标签
```
GET /api/v1/tags
```
查询参数：
- category: 标签分类（scene, model, type）

#### 4.2 创建标签
```
POST /api/v1/tags
```
请求体：
```json
{
    "name": "string",
    "category": "string",
    "color": "#RRGGBB"
}
```

#### 4.3 获取热门标签
```
GET /api/v1/tags/popular
```
查询参数：
- limit: 数量限制（默认10）

### 5. 测试接口

#### 5.1 测试Prompt
```
POST /api/v1/prompts/{id}/test
```
请求体：
```json
{
    "model": "gpt-5",  // 或 "claude-opus-4.1"
    "input": "测试输入（可选）",
    "parameters": {
        "temperature": 0.7,
        "max_tokens": 1000
    }
}
```
响应：
```json
{
    "code": 200,
    "data": {
        "test_id": 100,
        "model": "gpt-5",
        "input": "测试输入",
        "output": "模型输出结果",
        "tokens": {
            "input": 50,
            "output": 200
        },
        "response_time": 1.234,
        "created_at": "2025-01-01T00:00:00Z"
    }
}
```

#### 5.2 获取测试历史
```
GET /api/v1/prompts/{id}/tests
```
查询参数：
- page: 页码
- limit: 每页数量

#### 5.3 批量测试（对比测试）
```
POST /api/v1/prompts/{id}/test/batch
```
请求体：
```json
{
    "models": ["gpt-5", "claude-opus-4.1"],
    "input": "测试输入",
    "parameters": {...}
}
```

### 6. 协作接口

#### 6.1 添加协作者
```
POST /api/v1/prompts/{id}/collaborators
```
请求体：
```json
{
    "user_id": 2,
    "permission": "write"  // read, write, admin
}
```

#### 6.2 更新协作权限
```
PUT /api/v1/prompts/{id}/collaborators/{user_id}
```
请求体：
```json
{
    "permission": "read"
}
```

#### 6.3 移除协作者
```
DELETE /api/v1/prompts/{id}/collaborators/{user_id}
```

### 7. 用户设置接口

#### 7.1 获取用户设置
```
GET /api/v1/users/settings
```

#### 7.2 更新用户设置
```
PUT /api/v1/users/settings
```
请求体：
```json
{
    "background_music": "rain",
    "background_image": "url",
    "editor_theme": "light",
    "auto_save_interval": 3,
    "default_model": "gpt-5"
}
```

### 8. 搜索接口

#### 8.1 全文搜索
```
GET /api/v1/search
```
查询参数：
- q: 搜索关键词
- type: 搜索类型（all, title, content, tag）
- page: 页码
- limit: 每页数量

### 9. WebSocket接口（实时协作）

#### 9.1 连接WebSocket
```
ws://localhost:5000/ws
```

#### 9.2 消息格式
发送：
```json
{
    "type": "edit",
    "prompt_id": 1,
    "content": "编辑内容",
    "cursor_position": 100
}
```

接收：
```json
{
    "type": "update",
    "prompt_id": 1,
    "user": {
        "id": 2,
        "username": "user2"
    },
    "content": "更新内容",
    "timestamp": 1234567890
}
```

## 中间件设计

### 1. 认证中间件
- JWT token验证
- 用户身份识别
- 权限检查

### 2. 日志中间件
- 请求日志记录
- 响应时间统计
- 错误日志收集

### 3. 限流中间件
- API调用频率限制
- 防止恶意请求

### 4. 缓存中间件
- 热点数据缓存
- 查询结果缓存

## 错误处理

### 错误码定义
```python
ERROR_CODES = {
    # 通用错误 1000-1999
    1000: "未知错误",
    1001: "参数错误",
    1002: "数据不存在",
    
    # 认证错误 2000-2999
    2001: "用户名或密码错误",
    2002: "Token无效",
    2003: "Token已过期",
    
    # 权限错误 3000-3999
    3001: "无权限访问",
    3002: "操作被拒绝",
    
    # 业务错误 4000-4999
    4001: "Prompt不存在",
    4002: "版本不存在",
    4003: "标签已存在",
    4004: "测试失败",
    
    # 外部服务错误 5000-5999
    5001: "OpenAI服务异常",
    5002: "Claude服务异常"
}
```

## 安全考虑

1. **认证机制**：JWT Token
2. **数据验证**：所有输入数据验证
3. **SQL注入防护**：使用ORM参数化查询
4. **XSS防护**：输出转义
5. **CSRF防护**：Token验证
6. **限流保护**：防止暴力攻击

## 性能优化

1. **分页查询**：避免一次加载过多数据
2. **懒加载**：按需加载关联数据
3. **缓存策略**：热点数据缓存
4. **异步处理**：测试等耗时操作异步化
5. **连接池**：数据库连接池管理