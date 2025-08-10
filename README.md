# 静思 - Prompt管理系统

一个优雅、极简的Prompt管理工具，让思维沉淀成精华。

## 产品特性

- 🎯 **极简设计**：遵循"少即是多"的设计理念
- 📝 **版本管理**：自动保存每次修改，支持版本对比和回滚
- 🏷️ **智能标签**：灵活的标签系统，快速分类和检索
- 👥 **协作创作**：支持多人协作编辑和权限管理
- 🧪 **一键测试**：支持GPT-5和Claude Opus 4.1模型测试
- 🎵 **沉浸体验**：背景音乐和主题切换，营造专注氛围

## 技术栈

- **后端**: Flask + SQLAlchemy + MySQL
- **前端**: 原生JavaScript + CSS3
- **部署**: Docker + Docker Compose

## 快速开始

### 使用Docker部署（推荐）

1. 克隆项目
```bash
git clone <repository-url>
cd prompt_claude_v2
```

2. 配置环境变量
```bash
cp .env.template .env
# 编辑.env文件，填入你的配置
```

3. 启动服务
```bash
docker-compose up -d
```

4. 访问应用
```
http://localhost:5002
```

### 本地开发

1. 安装依赖
```bash
pip install -r requirements.txt
```

2. 配置数据库
```bash
# 创建MySQL数据库
mysql -u root -p
CREATE DATABASE prompt_manager CHARACTER SET utf8mb4;
```

3. 配置环境变量
```bash
cp .env.template .env
# 编辑.env文件
```

4. 启动应用
```bash
python app.py
```

## 项目结构

```
prompt_claude_v2/
├── app/                    # 应用主目录
│   ├── api/               # API接口
│   ├── models/            # 数据模型
│   ├── static/            # 静态文件
│   ├── templates/         # HTML模板
│   └── utils/             # 工具模块
├── config/                # 配置文件
├── database/              # 数据库脚本
├── docs/                  # 设计文档
├── logs/                  # 日志文件
├── docker-compose.yml     # Docker编排
└── requirements.txt       # Python依赖
```

## API文档

### 认证接口
- `POST /api/v1/auth/register` - 用户注册
- `POST /api/v1/auth/login` - 用户登录
- `POST /api/v1/auth/logout` - 用户登出

### Prompt接口
- `GET /api/v1/prompts` - 获取Prompt列表
- `POST /api/v1/prompts` - 创建Prompt
- `GET /api/v1/prompts/{id}` - 获取Prompt详情
- `PUT /api/v1/prompts/{id}` - 更新Prompt
- `DELETE /api/v1/prompts/{id}` - 删除Prompt

### 其他接口
详见 `docs/backend_design.md`

## 默认账号

开发环境提供了测试账号：
- 邮箱: test@example.com
- 密码: password123

**注意**: 生产环境请删除测试账号并修改所有默认密码！

## 环境变量说明

| 变量名 | 说明 | 默认值 |
|--------|------|--------|
| FLASK_ENV | 运行环境 | development |
| SECRET_KEY | Flask密钥 | 需修改 |
| DB_HOST | 数据库地址 | localhost |
| DB_PASSWORD | 数据库密码 | 需设置 |
| OPENAI_API_KEY | OpenAI密钥 | 需配置 |
| ANTHROPIC_API_KEY | Claude密钥 | 需配置 |

## 部署到生产环境

1. 修改所有密钥和密码
2. 配置HTTPS证书
3. 设置防火墙规则
4. 配置备份策略
5. 启用日志监控

## 开发指南

详见以下文档：
- `docs/product_design.md` - 产品设计
- `docs/database_design.md` - 数据库设计
- `docs/backend_design.md` - 后端设计
- `docs/frontend_design.md` - 前端设计

## License

MIT

## 作者

基于乔布斯和张小龙的产品理念设计
