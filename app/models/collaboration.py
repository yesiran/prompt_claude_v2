"""
协作权限模型
定义协作权限表结构
"""

from .base import db, BaseModel


class Collaboration(BaseModel):
    """协作权限模型"""
    
    __tablename__ = 'collaborations'
    
    # Prompt ID
    prompt_id = db.Column(
        db.Integer,
        db.ForeignKey('prompts.id', ondelete='CASCADE'),
        nullable=False,
        comment='Prompt ID'
    )
    
    # 协作用户ID
    user_id = db.Column(
        db.Integer,
        db.ForeignKey('users.id'),
        nullable=False,
        comment='协作用户ID'
    )
    
    # 权限级别
    permission = db.Column(
        db.Enum('read', 'write', 'admin'),
        default='read',
        comment='权限级别'
    )
    
    # 邀请者ID
    invited_by = db.Column(
        db.Integer,
        db.ForeignKey('users.id'),
        nullable=False,
        comment='邀请者ID'
    )
    
    # 接受邀请时间
    accepted_at = db.Column(
        db.DateTime,
        default=None,
        comment='接受邀请时间'
    )
    
    # 关系定义
    inviter = db.relationship(
        'User',
        backref='sent_invitations',
        foreign_keys=[invited_by]
    )
    
    # 唯一约束
    __table_args__ = (
        db.UniqueConstraint('prompt_id', 'user_id', name='uk_prompt_user'),
    )
    
    def accept_invitation(self):
        """接受邀请"""
        from datetime import datetime
        self.accepted_at = datetime.utcnow()
        self.save()
    
    def update_permission(self, new_permission):
        """
        更新权限级别
        
        参数:
            new_permission: 新的权限级别 ('read', 'write', 'admin')
        
        返回:
            bool: 是否成功
        """
        valid_permissions = ['read', 'write', 'admin']
        if new_permission not in valid_permissions:
            return False
        
        self.permission = new_permission
        self.save()
        return True
    
    def has_permission(self, required_permission):
        """
        检查是否有指定权限
        
        参数:
            required_permission: 需要的权限级别
        
        返回:
            bool: 是否有权限
        """
        permission_hierarchy = {
            'read': 1,
            'write': 2,
            'admin': 3
        }
        
        current_level = permission_hierarchy.get(self.permission, 0)
        required_level = permission_hierarchy.get(required_permission, 999)
        
        return current_level >= required_level
    
    @classmethod
    def get_user_collaborations(cls, user_id):
        """
        获取用户的所有协作
        
        参数:
            user_id: 用户ID
        
        返回:
            Collaboration列表
        """
        return cls.query.filter_by(user_id=user_id, accepted_at__ne=None).all()
    
    @classmethod
    def get_prompt_collaborators(cls, prompt_id):
        """
        获取Prompt的所有协作者
        
        参数:
            prompt_id: Prompt ID
        
        返回:
            Collaboration列表
        """
        return cls.query.filter_by(prompt_id=prompt_id).all()
    
    @classmethod
    def check_permission(cls, prompt_id, user_id, required_permission='read'):
        """
        检查用户对Prompt的权限
        
        参数:
            prompt_id: Prompt ID
            user_id: 用户ID
            required_permission: 需要的权限级别
        
        返回:
            bool: 是否有权限
        """
        collaboration = cls.query.filter_by(
            prompt_id=prompt_id,
            user_id=user_id
        ).first()
        
        if not collaboration:
            # 检查是否是作者
            from .prompt import Prompt
            prompt = Prompt.get_by_id(prompt_id)
            return prompt and prompt.author_id == user_id
        
        return collaboration.has_permission(required_permission)
    
    def __repr__(self):
        """返回协作的字符串表示"""
        return f"<Collaboration prompt:{self.prompt_id} user:{self.user_id} permission:{self.permission}>"