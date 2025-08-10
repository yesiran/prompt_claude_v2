"""
标签模型
定义标签表和Prompt-标签关联表
"""

from .base import db, BaseModel


class Tag(BaseModel):
    """标签模型"""
    
    __tablename__ = 'tags'
    
    # 标签名称
    name = db.Column(
        db.String(50),
        unique=True,
        nullable=False,
        comment='标签名称'
    )
    
    # 标签分类
    category = db.Column(
        db.String(50),
        default='general',
        comment='标签分类'
    )
    
    # 标签颜色
    color = db.Column(
        db.String(7),
        default='#6B7280',
        comment='标签颜色'
    )
    
    # 标签描述
    description = db.Column(
        db.String(200),
        default=None,
        comment='标签描述'
    )
    
    # 使用次数
    use_count = db.Column(
        db.Integer,
        default=0,
        comment='使用次数'
    )
    
    # 创建者ID
    created_by = db.Column(
        db.Integer,
        db.ForeignKey('users.id'),
        default=None,
        comment='创建者ID'
    )
    
    # 关系定义
    creator = db.relationship(
        'User',
        backref='created_tags',
        foreign_keys=[created_by]
    )
    
    # 关联的Prompt
    prompt_tags = db.relationship(
        'PromptTag',
        backref='tag',
        lazy='dynamic',
        cascade='all, delete-orphan'
    )
    
    def increment_use_count(self):
        """增加使用次数"""
        self.use_count += 1
        self.save()
    
    def decrement_use_count(self):
        """减少使用次数"""
        if self.use_count > 0:
            self.use_count -= 1
            self.save()
    
    def get_prompts(self):
        """
        获取使用此标签的所有Prompt
        
        返回:
            Prompt列表
        """
        return [pt.prompt for pt in self.prompt_tags]
    
    def get_prompts_count(self):
        """
        获取使用此标签的Prompt数量
        
        返回:
            int: Prompt数量
        """
        return self.prompt_tags.count()
    
    @classmethod
    def get_by_name(cls, name):
        """
        根据名称获取标签
        
        参数:
            name: 标签名称
        
        返回:
            Tag实例或None
        """
        return cls.query.filter_by(name=name).first()
    
    @classmethod
    def get_by_category(cls, category):
        """
        根据分类获取标签列表
        
        参数:
            category: 标签分类
        
        返回:
            Tag列表
        """
        return cls.query.filter_by(category=category).all()
    
    @classmethod
    def get_popular(cls, limit=10):
        """
        获取热门标签
        
        参数:
            limit: 返回数量限制
        
        返回:
            Tag列表
        """
        return cls.query.order_by(cls.use_count.desc()).limit(limit).all()
    
    @classmethod
    def create_or_get(cls, name, category='general', color='#6B7280', created_by=None):
        """
        创建或获取标签（如果已存在则返回现有标签）
        
        参数:
            name: 标签名称
            category: 标签分类
            color: 标签颜色
            created_by: 创建者ID
        
        返回:
            Tag实例
        """
        tag = cls.get_by_name(name)
        if tag:
            return tag
        
        tag = cls(
            name=name,
            category=category,
            color=color,
            created_by=created_by
        )
        tag.save()
        return tag
    
    def __repr__(self):
        """返回标签的字符串表示"""
        return f"<Tag {self.name}>"


class PromptTag(BaseModel):
    """Prompt-标签关联模型"""
    
    __tablename__ = 'prompt_tags'
    
    # Prompt ID
    prompt_id = db.Column(
        db.Integer,
        db.ForeignKey('prompts.id', ondelete='CASCADE'),
        nullable=False,
        comment='Prompt ID'
    )
    
    # 标签ID
    tag_id = db.Column(
        db.Integer,
        db.ForeignKey('tags.id', ondelete='CASCADE'),
        nullable=False,
        comment='标签ID'
    )
    
    # 唯一约束
    __table_args__ = (
        db.UniqueConstraint('prompt_id', 'tag_id', name='uk_prompt_tag'),
    )
    
    def __repr__(self):
        """返回关联的字符串表示"""
        return f"<PromptTag prompt:{self.prompt_id} tag:{self.tag_id}>"