"""
用户设置模型
定义用户设置表结构
"""

from .base import db, BaseModel


class UserSetting(BaseModel):
    """用户设置模型"""
    
    __tablename__ = 'user_settings'
    
    # 用户ID（唯一）
    user_id = db.Column(
        db.Integer,
        db.ForeignKey('users.id', ondelete='CASCADE'),
        unique=True,
        nullable=False,
        comment='用户ID'
    )
    
    # 背景音乐选择
    background_music = db.Column(
        db.String(100),
        default=None,
        comment='背景音乐选择'
    )
    
    # 背景图片URL
    background_image = db.Column(
        db.String(500),
        default=None,
        comment='背景图片URL'
    )
    
    # 编辑器主题
    editor_theme = db.Column(
        db.String(50),
        default='light',
        comment='编辑器主题'
    )
    
    # 自动保存间隔（秒）
    auto_save_interval = db.Column(
        db.Integer,
        default=3,
        comment='自动保存间隔(秒)'
    )
    
    # 默认测试模型
    default_model = db.Column(
        db.String(50),
        default='gpt-5',
        comment='默认测试模型'
    )
    
    # 是否开启通知
    notification_enabled = db.Column(
        db.Boolean,
        default=True,
        comment='是否开启通知'
    )
    
    # 快捷键配置（JSON格式）
    keyboard_shortcuts = db.Column(
        db.JSON,
        default=None,
        comment='快捷键配置'
    )
    
    @classmethod
    def get_user_settings(cls, user_id):
        """
        获取用户设置
        
        参数:
            user_id: 用户ID
        
        返回:
            UserSetting实例或None
        """
        return cls.query.filter_by(user_id=user_id).first()
    
    @classmethod
    def create_default_settings(cls, user_id):
        """
        创建默认用户设置
        
        参数:
            user_id: 用户ID
        
        返回:
            UserSetting实例
        """
        settings = cls(
            user_id=user_id,
            editor_theme='light',
            auto_save_interval=3,
            default_model='gpt-5',
            notification_enabled=True,
            keyboard_shortcuts={
                'save': 'Cmd+S',
                'test': 'Cmd+Enter',
                'search': 'Cmd+K',
                'focus': 'Cmd+/',
                'history': 'Cmd+H'
            }
        )
        settings.save()
        return settings
    
    def update_theme(self, theme):
        """
        更新编辑器主题
        
        参数:
            theme: 主题名称 ('light', 'dark', 'sepia')
        
        返回:
            bool: 是否成功
        """
        valid_themes = ['light', 'dark', 'sepia']
        if theme not in valid_themes:
            return False
        
        self.editor_theme = theme
        self.save()
        return True
    
    def update_background_music(self, music):
        """
        更新背景音乐
        
        参数:
            music: 音乐名称
        
        返回:
            bool: 是否成功
        """
        valid_music = ['rain', 'forest', 'piano', None]
        if music not in valid_music:
            return False
        
        self.background_music = music
        self.save()
        return True
    
    def get_shortcut(self, action):
        """
        获取指定操作的快捷键
        
        参数:
            action: 操作名称
        
        返回:
            str: 快捷键或None
        """
        if self.keyboard_shortcuts:
            return self.keyboard_shortcuts.get(action)
        return None
    
    def update_shortcut(self, action, shortcut):
        """
        更新快捷键
        
        参数:
            action: 操作名称
            shortcut: 新的快捷键
        
        返回:
            bool: 是否成功
        """
        if not self.keyboard_shortcuts:
            self.keyboard_shortcuts = {}
        
        self.keyboard_shortcuts[action] = shortcut
        self.save()
        return True
    
    def __repr__(self):
        """返回用户设置的字符串表示"""
        return f"<UserSetting user:{self.user_id}>"