"""
用户模型
定义用户表结构和相关方法
"""

from werkzeug.security import generate_password_hash, check_password_hash
from .base import db, BaseModel


class User(BaseModel):
    """用户模型"""
    
    __tablename__ = 'users'
    
    # 用户名，唯一，不可为空
    username = db.Column(
        db.String(50),
        unique=True,
        nullable=False,
        comment='用户名'
    )
    
    # 邮箱，唯一，不可为空
    email = db.Column(
        db.String(100),
        unique=True,
        nullable=False,
        comment='邮箱'
    )
    
    # 密码哈希值
    password_hash = db.Column(
        db.String(255),
        nullable=False,
        comment='密码哈希'
    )
    
    # 头像URL
    avatar_url = db.Column(
        db.String(500),
        default=None,
        comment='头像URL'
    )
    
    # 主题偏好设置，JSON格式存储
    theme_preference = db.Column(
        db.JSON,
        default=None,
        comment='主题偏好设置'
    )
    
    # 是否激活
    is_active = db.Column(
        db.Boolean,
        default=True,
        comment='是否激活'
    )
    
    # 最后登录时间
    last_login_at = db.Column(
        db.DateTime,
        default=None,
        comment='最后登录时间'
    )
    
    # 关系定义
    # 用户创建的Prompt列表
    prompts = db.relationship(
        'Prompt',
        backref='author',
        lazy='dynamic',
        foreign_keys='Prompt.author_id'
    )
    
    # 用户的设置
    settings = db.relationship(
        'UserSetting',
        backref='user',
        uselist=False,  # 一对一关系
        cascade='all, delete-orphan'
    )
    
    # 用户的协作权限
    collaborations = db.relationship(
        'Collaboration',
        backref='user',
        lazy='dynamic',
        foreign_keys='Collaboration.user_id'
    )
    
    # 用户的操作日志
    operation_logs = db.relationship(
        'OperationLog',
        backref='user',
        lazy='dynamic'
    )
    
    def set_password(self, password):
        """
        设置密码（自动加密）
        
        参数:
            password: 明文密码
        """
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        """
        验证密码
        
        参数:
            password: 明文密码
        
        返回:
            bool: 密码是否正确
        """
        return check_password_hash(self.password_hash, password)
    
    def update_login_time(self):
        """更新最后登录时间"""
        from datetime import datetime
        self.last_login_at = datetime.utcnow()
        self.save()
    
    def get_prompts_count(self):
        """
        获取用户创建的Prompt数量
        
        返回:
            int: Prompt数量
        """
        return self.prompts.count()
    
    def get_collaboration_prompts(self):
        """
        获取用户协作的Prompt列表
        
        返回:
            Prompt列表
        """
        return [collab.prompt for collab in self.collaborations]
    
    def has_permission(self, prompt_id, permission='read'):
        """
        检查用户对某个Prompt的权限
        
        参数:
            prompt_id: Prompt ID
            permission: 权限类型 ('read', 'write', 'admin')
        
        返回:
            bool: 是否有权限
        """
        from .prompt import Prompt
        from .collaboration import Collaboration
        
        # 检查是否是作者
        prompt = Prompt.get_by_id(prompt_id)
        if prompt and prompt.author_id == self.id:
            return True
        
        # 检查协作权限
        collab = Collaboration.query.filter_by(
            prompt_id=prompt_id,
            user_id=self.id
        ).first()
        
        if not collab:
            return False
        
        # 权限等级检查
        permission_levels = {
            'read': ['read', 'write', 'admin'],
            'write': ['write', 'admin'],
            'admin': ['admin']
        }
        
        return collab.permission in permission_levels.get(permission, [])
    
    def to_dict(self, exclude=None):
        """
        转换为字典（排除敏感信息）
        
        参数:
            exclude: 要排除的字段列表
        
        返回:
            dict: 用户信息字典
        """
        if exclude is None:
            exclude = []
        
        # 默认排除密码哈希
        exclude.append('password_hash')
        
        return super().to_dict(exclude=exclude)
    
    @classmethod
    def get_by_email(cls, email):
        """
        根据邮箱获取用户
        
        参数:
            email: 用户邮箱
        
        返回:
            User实例或None
        """
        return cls.query.filter_by(email=email).first()
    
    @classmethod
    def get_by_username(cls, username):
        """
        根据用户名获取用户
        
        参数:
            username: 用户名
        
        返回:
            User实例或None
        """
        return cls.query.filter_by(username=username).first()
    
    @classmethod
    def create_user(cls, username, email, password, **kwargs):
        """
        创建新用户
        
        参数:
            username: 用户名
            email: 邮箱
            password: 明文密码
            **kwargs: 其他用户属性
        
        返回:
            User实例
        """
        user = cls(
            username=username,
            email=email,
            **kwargs
        )
        user.set_password(password)
        user.save()
        
        # 创建默认用户设置
        from .user_setting import UserSetting
        UserSetting.create(user_id=user.id)
        
        return user
    
    def __repr__(self):
        """返回用户的字符串表示"""
        return f"<User {self.username}>"