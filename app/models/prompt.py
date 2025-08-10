"""
Prompt模型
定义Prompt表和版本表结构
"""

from .base import db, BaseModel


class Prompt(BaseModel):
    """Prompt主模型"""
    
    __tablename__ = 'prompts'
    
    # 标题
    title = db.Column(
        db.String(200),
        nullable=False,
        comment='Prompt标题'
    )
    
    # 内容
    content = db.Column(
        db.Text,
        nullable=False,
        comment='Prompt内容'
    )
    
    # 描述说明
    description = db.Column(
        db.String(500),
        default=None,
        comment='描述说明'
    )
    
    # 作者ID
    author_id = db.Column(
        db.Integer,
        db.ForeignKey('users.id'),
        nullable=False,
        comment='作者ID'
    )
    
    # 是否公开
    is_public = db.Column(
        db.Boolean,
        default=False,
        comment='是否公开'
    )
    
    # 软删除标记
    is_deleted = db.Column(
        db.Boolean,
        default=False,
        comment='软删除标记'
    )
    
    # 查看次数
    view_count = db.Column(
        db.Integer,
        default=0,
        comment='查看次数'
    )
    
    # 测试次数
    test_count = db.Column(
        db.Integer,
        default=0,
        comment='测试次数'
    )
    
    # 收藏次数
    star_count = db.Column(
        db.Integer,
        default=0,
        comment='收藏次数'
    )
    
    # 版本数量
    version_count = db.Column(
        db.Integer,
        default=1,
        comment='版本数量'
    )
    
    # 最后测试时间
    last_tested_at = db.Column(
        db.DateTime,
        default=None,
        comment='最后测试时间'
    )
    
    # 关系定义
    # 版本列表
    versions = db.relationship(
        'PromptVersion',
        backref='prompt',
        lazy='dynamic',
        cascade='all, delete-orphan',
        order_by='PromptVersion.version_number.desc()'
    )
    
    # 标签关联
    prompt_tags = db.relationship(
        'PromptTag',
        backref='prompt',
        lazy='dynamic',
        cascade='all, delete-orphan'
    )
    
    # 测试记录
    test_records = db.relationship(
        'TestRecord',
        backref='prompt',
        lazy='dynamic',
        cascade='all, delete-orphan'
    )
    
    # 协作权限
    collaborations = db.relationship(
        'Collaboration',
        backref='prompt',
        lazy='dynamic',
        cascade='all, delete-orphan'
    )
    
    def increment_view_count(self):
        """增加查看次数"""
        self.view_count += 1
        self.save()
    
    def increment_test_count(self):
        """增加测试次数"""
        from datetime import datetime
        self.test_count += 1
        self.last_tested_at = datetime.utcnow()
        self.save()
    
    def create_version(self, title=None, content=None, description=None, 
                      change_summary=None, author_id=None):
        """
        创建新版本
        
        参数:
            title: 版本标题
            content: 版本内容
            description: 版本描述
            change_summary: 修改摘要
            author_id: 修改者ID
        
        返回:
            PromptVersion实例
        """
        # 使用数据库查询获取最大版本号，避免缓存问题
        from sqlalchemy import func
        max_version = db.session.query(func.max(PromptVersion.version_number)).filter(
            PromptVersion.prompt_id == self.id
        ).scalar()
        
        # 计算下一个版本号
        next_version_number = (max_version + 1) if max_version else 1
        
        # 创建版本记录
        version = PromptVersion(
            prompt_id=self.id,
            version_number=next_version_number,
            title=title or self.title,
            content=content or self.content,
            description=description or self.description,
            change_summary=change_summary,
            author_id=author_id or self.author_id
        )
        version.save()
        
        # 更新版本计数
        self.version_count = next_version_number
        self.save()
        
        return version
    
    def get_current_version(self):
        """
        获取当前版本（最新版本）
        
        返回:
            PromptVersion实例或None
        """
        return self.versions.first()
    
    def get_version_by_number(self, version_number):
        """
        根据版本号获取版本
        
        参数:
            version_number: 版本号
        
        返回:
            PromptVersion实例或None
        """
        return self.versions.filter_by(version_number=version_number).first()
    
    def rollback_to_version(self, version_id):
        """
        回滚到指定版本
        
        参数:
            version_id: 版本ID
        
        返回:
            bool: 是否成功
        """
        version = PromptVersion.get_by_id(version_id)
        if not version or version.prompt_id != self.id:
            return False
        
        # 更新当前内容为指定版本的内容
        self.title = version.title
        self.content = version.content
        self.description = version.description
        
        # 创建新版本记录
        self.create_version(
            change_summary=f"回滚到版本 {version.version_number}"
        )
        
        return True
    
    def get_tags(self):
        """
        获取Prompt的所有标签
        
        返回:
            Tag列表
        """
        return [pt.tag for pt in self.prompt_tags]
    
    def add_tag(self, tag_id):
        """
        添加标签
        
        参数:
            tag_id: 标签ID
        
        返回:
            bool: 是否成功
        """
        from .tag import Tag, PromptTag
        
        # 检查标签是否存在
        tag = Tag.get_by_id(tag_id)
        if not tag:
            return False
        
        # 检查是否已有此标签
        existing = PromptTag.query.filter_by(
            prompt_id=self.id,
            tag_id=tag_id
        ).first()
        
        if existing:
            return True
        
        # 添加标签关联
        prompt_tag = PromptTag(
            prompt_id=self.id,
            tag_id=tag_id
        )
        prompt_tag.save()
        
        # 更新标签使用次数
        tag.increment_use_count()
        
        return True
    
    def remove_tag(self, tag_id):
        """
        移除标签
        
        参数:
            tag_id: 标签ID
        
        返回:
            bool: 是否成功
        """
        from .tag import PromptTag
        
        prompt_tag = PromptTag.query.filter_by(
            prompt_id=self.id,
            tag_id=tag_id
        ).first()
        
        if prompt_tag:
            prompt_tag.delete()
            return True
        
        return False
    
    def soft_delete(self):
        """软删除"""
        self.is_deleted = True
        self.save()
    
    def restore(self):
        """恢复软删除"""
        self.is_deleted = False
        self.save()
    
    def to_dict(self, include_tags=False, include_author=False):
        """
        转换为字典
        
        参数:
            include_tags: 是否包含标签信息
            include_author: 是否包含作者信息
        
        返回:
            dict: Prompt信息字典
        """
        data = super().to_dict()
        
        if include_tags:
            data['tags'] = [tag.to_dict() for tag in self.get_tags()]
        
        if include_author and self.author:
            data['author'] = {
                'id': self.author.id,
                'username': self.author.username
            }
        
        return data
    
    @classmethod
    def search(cls, keyword, tags=None, author_id=None):
        """
        搜索Prompt
        
        参数:
            keyword: 搜索关键词
            tags: 标签ID列表
            author_id: 作者ID
        
        返回:
            Query对象
        """
        query = cls.query.filter_by(is_deleted=False)
        
        # 关键词搜索
        if keyword:
            search_filter = db.or_(
                cls.title.contains(keyword),
                cls.content.contains(keyword),
                cls.description.contains(keyword)
            )
            query = query.filter(search_filter)
        
        # 标签筛选
        if tags:
            from .tag import PromptTag
            query = query.join(PromptTag).filter(PromptTag.tag_id.in_(tags))
        
        # 作者筛选
        if author_id:
            query = query.filter_by(author_id=author_id)
        
        return query
    
    def __repr__(self):
        """返回Prompt的字符串表示"""
        return f"<Prompt {self.title}>"


class PromptVersion(BaseModel):
    """Prompt版本模型"""
    
    __tablename__ = 'prompt_versions'
    
    # Prompt ID
    prompt_id = db.Column(
        db.Integer,
        db.ForeignKey('prompts.id', ondelete='CASCADE'),
        nullable=False,
        comment='Prompt ID'
    )
    
    # 版本号
    version_number = db.Column(
        db.Integer,
        nullable=False,
        comment='版本号'
    )
    
    # 版本标题
    title = db.Column(
        db.String(200),
        nullable=False,
        comment='版本标题'
    )
    
    # 版本内容
    content = db.Column(
        db.Text,
        nullable=False,
        comment='版本内容'
    )
    
    # 版本描述
    description = db.Column(
        db.String(500),
        default=None,
        comment='版本描述'
    )
    
    # 修改摘要
    change_summary = db.Column(
        db.String(500),
        default=None,
        comment='修改摘要'
    )
    
    # 修改者ID
    author_id = db.Column(
        db.Integer,
        db.ForeignKey('users.id'),
        nullable=False,
        comment='修改者ID'
    )
    
    # 是否为主要版本
    is_major_version = db.Column(
        db.Boolean,
        default=False,
        comment='是否为主要版本'
    )
    
    # 关系定义
    version_author = db.relationship(
        'User',
        backref='prompt_versions',
        foreign_keys=[author_id]
    )
    
    # 唯一约束
    __table_args__ = (
        db.UniqueConstraint('prompt_id', 'version_number', name='uk_prompt_version'),
    )
    
    def compare_with(self, other_version):
        """
        与另一个版本比较
        
        参数:
            other_version: 另一个PromptVersion实例
        
        返回:
            dict: 差异信息
        """
        import difflib
        
        # 比较内容差异
        content_diff = list(difflib.unified_diff(
            other_version.content.splitlines(),
            self.content.splitlines(),
            lineterm='',
            fromfile=f'版本 {other_version.version_number}',
            tofile=f'版本 {self.version_number}'
        ))
        
        return {
            'from_version': other_version.version_number,
            'to_version': self.version_number,
            'title_changed': self.title != other_version.title,
            'description_changed': self.description != other_version.description,
            'content_diff': content_diff
        }
    
    def __repr__(self):
        """返回版本的字符串表示"""
        return f"<PromptVersion {self.prompt_id}:{self.version_number}>"