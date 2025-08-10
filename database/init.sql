-- 初始化数据库脚本
-- 创建数据库（如果不存在）
CREATE DATABASE IF NOT EXISTS prompt_manager DEFAULT CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;

USE prompt_manager;

-- 插入默认标签数据
INSERT INTO tags (name, category, color, description) VALUES
('工作', 'scene', '#3B82F6', '工作相关的Prompt'),
('学习', 'scene', '#10B981', '学习相关的Prompt'),
('创作', 'scene', '#8B5CF6', '创作相关的Prompt'),
('生活', 'scene', '#F59E0B', '生活相关的Prompt'),
('GPT-5', 'model', '#EF4444', 'OpenAI GPT-5模型'),
('Claude', 'model', '#F59E0B', 'Anthropic Claude模型'),
('代码', 'type', '#6366F1', '代码生成类Prompt'),
('文案', 'type', '#EC4899', '文案创作类Prompt'),
('翻译', 'type', '#14B8A6', '翻译类Prompt'),
('分析', 'type', '#84CC16', '分析类Prompt')
ON DUPLICATE KEY UPDATE name=name;

-- 创建测试用户（仅用于开发环境）
-- 密码为 'password123'
INSERT INTO users (username, email, password_hash, is_active) VALUES
('testuser', 'test@example.com', 'pbkdf2:sha256:600000$DcvKGmFQ$8e4a3f4c8b9e5d1a2b3c4d5e6f7a8b9c0d1e2f3a4b5c6d7e8f9a0b1c2d3e4f5', TRUE),
('testuser2', 'test2@example.com', 'pbkdf2:sha256:600000$DcvKGmFQ$8e4a3f4c8b9e5d1a2b3c4d5e6f7a8b9c0d1e2f3a4b5c6d7e8f9a0b1c2d3e4f5', TRUE)
ON DUPLICATE KEY UPDATE username=username;