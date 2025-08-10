"""
操作日志模型
定义操作日志表结构
"""

from .base import db, BaseModel


class OperationLog(BaseModel):
    """操作日志模型"""
    
    __tablename__ = 'operation_logs'
    
    # 使用BIGINT作为主键，因为日志量可能很大
    id = db.Column(
        db.BigInteger,
        primary_key=True,
        autoincrement=True
    )
    
    # 操作用户ID
    user_id = db.Column(
        db.Integer,
        db.ForeignKey('users.id'),
        nullable=False,
        comment='操作用户ID'
    )
    
    # 操作类型
    action_type = db.Column(
        db.String(50),
        nullable=False,
        comment='操作类型'
    )
    
    # 目标类型
    target_type = db.Column(
        db.String(50),
        nullable=False,
        comment='目标类型'
    )
    
    # 目标ID
    target_id = db.Column(
        db.Integer,
        nullable=False,
        comment='目标ID'
    )
    
    # 操作详情（JSON格式）
    action_detail = db.Column(
        db.JSON,
        default=None,
        comment='操作详情'
    )
    
    # IP地址
    ip_address = db.Column(
        db.String(45),
        default=None,
        comment='IP地址'
    )
    
    # 用户代理
    user_agent = db.Column(
        db.String(500),
        default=None,
        comment='用户代理'
    )
    
    # 索引定义
    __table_args__ = (
        db.Index('idx_user_id', 'user_id'),
        db.Index('idx_target', 'target_type', 'target_id'),
        db.Index('idx_created_at', 'created_at'),
    )
    
    # 操作类型常量
    ACTION_CREATE = 'create'
    ACTION_UPDATE = 'update'
    ACTION_DELETE = 'delete'
    ACTION_READ = 'read'
    ACTION_TEST = 'test'
    ACTION_SHARE = 'share'
    ACTION_LOGIN = 'login'
    ACTION_LOGOUT = 'logout'
    
    # 目标类型常量
    TARGET_PROMPT = 'prompt'
    TARGET_VERSION = 'version'
    TARGET_TAG = 'tag'
    TARGET_USER = 'user'
    TARGET_SETTING = 'setting'
    
    @classmethod
    def log_action(cls, user_id, action_type, target_type, target_id, 
                  detail=None, ip_address=None, user_agent=None):
        """
        记录操作日志
        
        参数:
            user_id: 操作用户ID
            action_type: 操作类型
            target_type: 目标类型
            target_id: 目标ID
            detail: 操作详情
            ip_address: IP地址
            user_agent: 用户代理
        
        返回:
            OperationLog实例
        """
        log = cls(
            user_id=user_id,
            action_type=action_type,
            target_type=target_type,
            target_id=target_id,
            action_detail=detail,
            ip_address=ip_address,
            user_agent=user_agent
        )
        log.save()
        return log
    
    @classmethod
    def get_user_logs(cls, user_id, limit=None):
        """
        获取用户的操作日志
        
        参数:
            user_id: 用户ID
            limit: 返回数量限制
        
        返回:
            OperationLog列表
        """
        query = cls.query.filter_by(user_id=user_id).order_by(cls.created_at.desc())
        
        if limit:
            query = query.limit(limit)
        
        return query.all()
    
    @classmethod
    def get_target_logs(cls, target_type, target_id, limit=None):
        """
        获取特定目标的操作日志
        
        参数:
            target_type: 目标类型
            target_id: 目标ID
            limit: 返回数量限制
        
        返回:
            OperationLog列表
        """
        query = cls.query.filter_by(
            target_type=target_type,
            target_id=target_id
        ).order_by(cls.created_at.desc())
        
        if limit:
            query = query.limit(limit)
        
        return query.all()
    
    @classmethod
    def get_recent_activities(cls, limit=50):
        """
        获取最近的活动日志
        
        参数:
            limit: 返回数量限制
        
        返回:
            OperationLog列表
        """
        return cls.query.order_by(cls.created_at.desc()).limit(limit).all()
    
    @classmethod
    def cleanup_old_logs(cls, days=90):
        """
        清理旧日志
        
        参数:
            days: 保留天数
        
        返回:
            int: 删除的记录数
        """
        from datetime import datetime, timedelta
        
        cutoff_date = datetime.utcnow() - timedelta(days=days)
        
        old_logs = cls.query.filter(cls.created_at < cutoff_date)
        count = old_logs.count()
        old_logs.delete()
        
        db.session.commit()
        return count
    
    def get_action_description(self):
        """
        获取操作的描述文本
        
        返回:
            str: 操作描述
        """
        action_descriptions = {
            self.ACTION_CREATE: '创建',
            self.ACTION_UPDATE: '更新',
            self.ACTION_DELETE: '删除',
            self.ACTION_READ: '查看',
            self.ACTION_TEST: '测试',
            self.ACTION_SHARE: '分享',
            self.ACTION_LOGIN: '登录',
            self.ACTION_LOGOUT: '登出'
        }
        
        target_descriptions = {
            self.TARGET_PROMPT: 'Prompt',
            self.TARGET_VERSION: '版本',
            self.TARGET_TAG: '标签',
            self.TARGET_USER: '用户',
            self.TARGET_SETTING: '设置'
        }
        
        action = action_descriptions.get(self.action_type, self.action_type)
        target = target_descriptions.get(self.target_type, self.target_type)
        
        return f"{action}{target} #{self.target_id}"
    
    def __repr__(self):
        """返回操作日志的字符串表示"""
        return f"<OperationLog {self.id} {self.action_type} {self.target_type}:{self.target_id}>"