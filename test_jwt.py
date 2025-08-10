#!/usr/bin/env python3
"""
测试JWT认证问题
"""

import requests
import json

# 基础URL
BASE_URL = "http://localhost:5002"

def test_login():
    """测试登录并获取token"""
    print("=" * 50)
    print("1. 测试登录...")
    
    response = requests.post(
        f"{BASE_URL}/api/v1/auth/login",
        json={
            "email": "test@example.com",
            "password": "Test123456"
        }
    )
    
    print(f"状态码: {response.status_code}")
    print(f"响应内容: {response.text}")
    
    if response.status_code == 200:
        data = response.json()
        token = data.get('data', {}).get('token')
        print(f"获取到的Token: {token[:50] if token else 'None'}...")
        return token
    return None

def test_create_prompt(token):
    """测试创建Prompt"""
    print("=" * 50)
    print("2. 测试创建Prompt...")
    
    headers = {}
    if token:
        headers['Authorization'] = f'Bearer {token}'
        print(f"Authorization header: Bearer {token[:20]}...")
    else:
        print("警告：没有token")
    
    headers['Content-Type'] = 'application/json'
    
    response = requests.post(
        f"{BASE_URL}/api/v1/prompts",
        headers=headers,
        json={
            "title": "测试标题",
            "content": "测试内容",
            "description": "测试描述",
            "tags": []
        }
    )
    
    print(f"状态码: {response.status_code}")
    print(f"响应内容: {response.text[:200] if response.text else 'None'}...")
    
    # 打印请求头（调试用）
    print(f"发送的请求头: {headers}")

def test_get_tags(token):
    """测试获取标签列表"""
    print("=" * 50)
    print("3. 测试获取标签...")
    
    headers = {}
    if token:
        headers['Authorization'] = f'Bearer {token}'
    
    response = requests.get(
        f"{BASE_URL}/api/v1/tags",
        headers=headers
    )
    
    print(f"状态码: {response.status_code}")
    print(f"响应内容: {response.text[:200] if response.text else 'None'}...")

def main():
    print("\n开始测试JWT认证流程")
    print("=" * 50)
    
    # 测试登录
    token = test_login()
    
    if token:
        # 测试创建Prompt
        test_create_prompt(token)
        
        # 测试获取标签
        test_get_tags(token)
    else:
        print("登录失败，无法继续测试")

if __name__ == '__main__':
    main()