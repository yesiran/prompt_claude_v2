#!/bin/bash

# 启动脚本
# 用于快速启动Prompt管理系统

echo "========================================="
echo "     静思 - Prompt管理系统启动脚本"
echo "========================================="

# 检查是否已安装Docker
if ! command -v docker &> /dev/null; then
    echo "❌ Docker未安装，请先安装Docker"
    echo "访问 https://docs.docker.com/get-docker/ 获取安装指南"
    exit 1
fi

# 检查是否已安装Docker Compose
if ! command -v docker-compose &> /dev/null; then
    echo "❌ Docker Compose未安装，请先安装Docker Compose"
    echo "访问 https://docs.docker.com/compose/install/ 获取安装指南"
    exit 1
fi

# 检查环境配置文件
if [ ! -f .env ]; then
    echo "📝 创建环境配置文件..."
    cp .env.template .env
    echo "⚠️  请编辑 .env 文件，配置必要的环境变量"
    echo "   特别是数据库密码和API密钥"
    read -p "按Enter键继续..." -r
fi

# 创建必要的目录
echo "📁 创建必要的目录..."
mkdir -p logs uploads

# 启动服务
echo "🚀 启动服务..."
docker-compose up -d

# 等待服务启动
echo "⏳ 等待服务启动..."
sleep 10

# 检查服务状态
echo "🔍 检查服务状态..."
docker-compose ps

# 显示访问信息
echo ""
echo "========================================="
echo "✅ 服务启动成功！"
echo ""
echo "📌 访问地址："
echo "   Web应用: http://localhost:5002"
echo "   数据库: localhost:3306"
echo ""
echo "📧 测试账号："
echo "   邮箱: test@example.com"
echo "   密码: password123"
echo ""
echo "🔧 常用命令："
echo "   查看日志: docker-compose logs -f"
echo "   停止服务: docker-compose down"
echo "   重启服务: docker-compose restart"
echo "========================================="