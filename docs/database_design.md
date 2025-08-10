# 数据库设计方案

## 设计理念
- **最小化原则**：只存储必要的信息
- **扩展性考虑**：预留合理的扩展空间
- **关系清晰**：表之间的关系简单明了
- **性能优先**：合理的索引设计

## 数据库表设计

### 1. 用户表 (users)
```sql
CREATE TABLE users (
    id INT PRIMARY KEY AUTO_INCREMENT,
    username VARCHAR(50) UNIQUE NOT NULL COMMENT '用户名',
    email VARCHAR(100) UNIQUE NOT NULL COMMENT '邮箱',
    password_hash VARCHAR(255) NOT NULL COMMENT '密码哈希',
    avatar_url VARCHAR(500) DEFAULT NULL COMMENT '头像URL',
    theme_preference JSON DEFAULT NULL COMMENT '主题偏好设置',
    is_active BOOLEAN DEFAULT TRUE COMMENT '是否激活',
    last_login_at TIMESTAMP NULL COMMENT '最后登录时间',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
    INDEX idx_username (username),
    INDEX idx_email (email)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='用户表';
```

### 2. Prompt表 (prompts)
```sql
CREATE TABLE prompts (
    id INT PRIMARY KEY AUTO_INCREMENT,
    title VARCHAR(200) NOT NULL COMMENT 'Prompt标题',
    content TEXT NOT NULL COMMENT 'Prompt内容',
    description VARCHAR(500) DEFAULT NULL COMMENT '描述说明',
    author_id INT NOT NULL COMMENT '作者ID',
    is_public BOOLEAN DEFAULT FALSE COMMENT '是否公开',
    is_deleted BOOLEAN DEFAULT FALSE COMMENT '软删除标记',
    view_count INT DEFAULT 0 COMMENT '查看次数',
    test_count INT DEFAULT 0 COMMENT '测试次数',
    star_count INT DEFAULT 0 COMMENT '收藏次数',
    version_count INT DEFAULT 1 COMMENT '版本数量',
    last_tested_at TIMESTAMP NULL COMMENT '最后测试时间',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
    FOREIGN KEY (author_id) REFERENCES users(id),
    INDEX idx_author_id (author_id),
    INDEX idx_created_at (created_at),
    INDEX idx_is_deleted (is_deleted),
    FULLTEXT idx_fulltext (title, content, description)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='Prompt主表';
```

### 3. Prompt版本表 (prompt_versions)
```sql
CREATE TABLE prompt_versions (
    id INT PRIMARY KEY AUTO_INCREMENT,
    prompt_id INT NOT NULL COMMENT 'Prompt ID',
    version_number INT NOT NULL COMMENT '版本号',
    title VARCHAR(200) NOT NULL COMMENT '版本标题',
    content TEXT NOT NULL COMMENT '版本内容',
    description VARCHAR(500) DEFAULT NULL COMMENT '版本描述',
    change_summary VARCHAR(500) DEFAULT NULL COMMENT '修改摘要',
    author_id INT NOT NULL COMMENT '修改者ID',
    is_major_version BOOLEAN DEFAULT FALSE COMMENT '是否为主要版本',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    FOREIGN KEY (prompt_id) REFERENCES prompts(id) ON DELETE CASCADE,
    FOREIGN KEY (author_id) REFERENCES users(id),
    UNIQUE KEY uk_prompt_version (prompt_id, version_number),
    INDEX idx_prompt_id (prompt_id),
    INDEX idx_created_at (created_at)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='Prompt版本记录表';
```

### 4. 标签表 (tags)
```sql
CREATE TABLE tags (
    id INT PRIMARY KEY AUTO_INCREMENT,
    name VARCHAR(50) UNIQUE NOT NULL COMMENT '标签名称',
    category VARCHAR(50) DEFAULT 'general' COMMENT '标签分类',
    color VARCHAR(7) DEFAULT '#6B7280' COMMENT '标签颜色',
    description VARCHAR(200) DEFAULT NULL COMMENT '标签描述',
    use_count INT DEFAULT 0 COMMENT '使用次数',
    created_by INT DEFAULT NULL COMMENT '创建者ID',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
    FOREIGN KEY (created_by) REFERENCES users(id),
    INDEX idx_name (name),
    INDEX idx_category (category)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='标签表';
```

### 5. Prompt标签关联表 (prompt_tags)
```sql
CREATE TABLE prompt_tags (
    id INT PRIMARY KEY AUTO_INCREMENT,
    prompt_id INT NOT NULL COMMENT 'Prompt ID',
    tag_id INT NOT NULL COMMENT '标签ID',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    FOREIGN KEY (prompt_id) REFERENCES prompts(id) ON DELETE CASCADE,
    FOREIGN KEY (tag_id) REFERENCES tags(id) ON DELETE CASCADE,
    UNIQUE KEY uk_prompt_tag (prompt_id, tag_id),
    INDEX idx_prompt_id (prompt_id),
    INDEX idx_tag_id (tag_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='Prompt标签关联表';
```

### 6. 测试记录表 (test_records)
```sql
CREATE TABLE test_records (
    id INT PRIMARY KEY AUTO_INCREMENT,
    prompt_id INT NOT NULL COMMENT 'Prompt ID',
    version_id INT DEFAULT NULL COMMENT '版本ID',
    user_id INT NOT NULL COMMENT '测试用户ID',
    model_name VARCHAR(50) NOT NULL COMMENT '模型名称',
    model_params JSON DEFAULT NULL COMMENT '模型参数',
    input_tokens INT DEFAULT 0 COMMENT '输入token数',
    output_tokens INT DEFAULT 0 COMMENT '输出token数',
    response_time DECIMAL(10,3) DEFAULT NULL COMMENT '响应时间(秒)',
    test_input TEXT DEFAULT NULL COMMENT '测试输入',
    test_output TEXT DEFAULT NULL COMMENT '测试输出',
    status ENUM('success', 'failed', 'timeout') DEFAULT 'success' COMMENT '测试状态',
    error_message TEXT DEFAULT NULL COMMENT '错误信息',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    FOREIGN KEY (prompt_id) REFERENCES prompts(id) ON DELETE CASCADE,
    FOREIGN KEY (version_id) REFERENCES prompt_versions(id) ON DELETE SET NULL,
    FOREIGN KEY (user_id) REFERENCES users(id),
    INDEX idx_prompt_id (prompt_id),
    INDEX idx_user_id (user_id),
    INDEX idx_created_at (created_at)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='测试记录表';
```

### 7. 协作权限表 (collaborations)
```sql
CREATE TABLE collaborations (
    id INT PRIMARY KEY AUTO_INCREMENT,
    prompt_id INT NOT NULL COMMENT 'Prompt ID',
    user_id INT NOT NULL COMMENT '协作用户ID',
    permission ENUM('read', 'write', 'admin') DEFAULT 'read' COMMENT '权限级别',
    invited_by INT NOT NULL COMMENT '邀请者ID',
    accepted_at TIMESTAMP NULL COMMENT '接受邀请时间',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
    FOREIGN KEY (prompt_id) REFERENCES prompts(id) ON DELETE CASCADE,
    FOREIGN KEY (user_id) REFERENCES users(id),
    FOREIGN KEY (invited_by) REFERENCES users(id),
    UNIQUE KEY uk_prompt_user (prompt_id, user_id),
    INDEX idx_prompt_id (prompt_id),
    INDEX idx_user_id (user_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='协作权限表';
```

### 8. 用户设置表 (user_settings)
```sql
CREATE TABLE user_settings (
    id INT PRIMARY KEY AUTO_INCREMENT,
    user_id INT UNIQUE NOT NULL COMMENT '用户ID',
    background_music VARCHAR(100) DEFAULT NULL COMMENT '背景音乐选择',
    background_image VARCHAR(500) DEFAULT NULL COMMENT '背景图片URL',
    editor_theme VARCHAR(50) DEFAULT 'light' COMMENT '编辑器主题',
    auto_save_interval INT DEFAULT 3 COMMENT '自动保存间隔(秒)',
    default_model VARCHAR(50) DEFAULT 'gpt-5' COMMENT '默认测试模型',
    notification_enabled BOOLEAN DEFAULT TRUE COMMENT '是否开启通知',
    keyboard_shortcuts JSON DEFAULT NULL COMMENT '快捷键配置',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    INDEX idx_user_id (user_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='用户设置表';
```

### 9. 操作日志表 (operation_logs)
```sql
CREATE TABLE operation_logs (
    id BIGINT PRIMARY KEY AUTO_INCREMENT,
    user_id INT NOT NULL COMMENT '操作用户ID',
    action_type VARCHAR(50) NOT NULL COMMENT '操作类型',
    target_type VARCHAR(50) NOT NULL COMMENT '目标类型',
    target_id INT NOT NULL COMMENT '目标ID',
    action_detail JSON DEFAULT NULL COMMENT '操作详情',
    ip_address VARCHAR(45) DEFAULT NULL COMMENT 'IP地址',
    user_agent VARCHAR(500) DEFAULT NULL COMMENT '用户代理',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    FOREIGN KEY (user_id) REFERENCES users(id),
    INDEX idx_user_id (user_id),
    INDEX idx_target (target_type, target_id),
    INDEX idx_created_at (created_at)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='操作日志表';
```

## 索引设计说明

1. **主键索引**：所有表都使用自增ID作为主键
2. **外键索引**：所有外键自动创建索引
3. **查询索引**：根据常用查询场景创建
4. **全文索引**：prompts表的标题和内容支持全文搜索

## 数据关系说明

```
users (1) ─────< (n) prompts
  │                    │
  │                    ├──< (n) prompt_versions
  │                    ├──< (n) prompt_tags ──> (n) tags
  │                    ├──< (n) test_records
  │                    └──< (n) collaborations
  │
  ├──< (1) user_settings
  └──< (n) operation_logs
```

## 设计考虑

### 扩展性考虑
1. **JSON字段**：用于存储灵活的配置数据
2. **软删除**：prompts表支持软删除
3. **版本管理**：独立的版本表，支持无限版本
4. **权限系统**：预留了协作权限表

### 性能优化
1. **分表设计**：将版本、标签等分离到独立表
2. **合理索引**：基于查询场景设计索引
3. **字段类型**：选择合适的字段类型和长度

### 数据完整性
1. **外键约束**：确保引用完整性
2. **唯一约束**：防止重复数据
3. **非空约束**：确保必要字段有值

## 初始数据

```sql
-- 插入默认标签
INSERT INTO tags (name, category, color) VALUES
('工作', 'scene', '#3B82F6'),
('学习', 'scene', '#10B981'),
('创作', 'scene', '#8B5CF6'),
('GPT-5', 'model', '#EF4444'),
('Claude', 'model', '#F59E0B'),
('代码', 'type', '#6366F1'),
('文案', 'type', '#EC4899'),
('翻译', 'type', '#14B8A6');

-- 插入测试用户（生产环境需要修改）
INSERT INTO users (username, email, password_hash) VALUES
('user1', 'user1@example.com', 'hashed_password_here'),
('user2', 'user2@example.com', 'hashed_password_here');
```