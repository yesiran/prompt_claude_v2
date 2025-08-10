"""
基础模型类
所有数据模型的基类，提供通用字段和方法
"""

from datetime import datetime
from flask_sqlalchemy import SQLAlchemy

# 创建数据库实例
db = SQLAlchemy()


class BaseModel(db.Model):
    """
    基础模型类
    所有模型都继承此类，自动包含id、created_at、updated_at字段
    """
    
    __abstract__ = True  # 声明为抽象类，不会创建对应的数据表
    
    # 主键ID，自增
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    
    # 创建时间，默认为当前时间
    created_at = db.Column(
        db.DateTime,
        default=datetime.utcnow,
        nullable=False,
        comment='创建时间'
    )
    
    # 更新时间，每次更新时自动更新
    updated_at = db.Column(
        db.DateTime,
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
        nullable=False,
        comment='更新时间'
    )
    
    def save(self):
        """
        保存模型到数据库
        如果是新记录则插入，如果是已存在记录则更新
        """
        try:
            db.session.add(self)
            db.session.commit()
            return True
        except Exception as e:
            db.session.rollback()
            raise e
    
    def delete(self):
        """
        从数据库删除记录
        """
        try:
            db.session.delete(self)
            db.session.commit()
            return True
        except Exception as e:
            db.session.rollback()
            raise e
    
    def update(self, **kwargs):
        """
        更新模型属性
        
        参数:
            **kwargs: 要更新的属性键值对
        """
        for key, value in kwargs.items():
            if hasattr(self, key):
                setattr(self, key, value)
        
        return self.save()
    
    def to_dict(self, exclude=None):
        """
        将模型转换为字典
        
        参数:
            exclude: 要排除的字段列表
        
        返回:
            字典格式的模型数据
        """
        if exclude is None:
            exclude = []
        
        data = {}
        for column in self.__table__.columns:
            if column.name not in exclude:
                value = getattr(self, column.name)
                
                # 处理特殊类型
                if isinstance(value, datetime):
                    value = value.isoformat()
                
                data[column.name] = value
        
        return data
    
    @classmethod
    def get_by_id(cls, id):
        """
        根据ID获取记录
        
        参数:
            id: 记录ID
        
        返回:
            模型实例或None
        """
        return cls.query.get(id)
    
    @classmethod
    def get_all(cls):
        """
        获取所有记录
        
        返回:
            模型实例列表
        """
        return cls.query.all()
    
    @classmethod
    def create(cls, **kwargs):
        """
        创建新记录
        
        参数:
            **kwargs: 模型属性键值对
        
        返回:
            创建的模型实例
        """
        instance = cls(**kwargs)
        instance.save()
        return instance
    
    @classmethod
    def bulk_create(cls, items):
        """
        批量创建记录
        
        参数:
            items: 包含模型属性的字典列表
        
        返回:
            创建的模型实例列表
        """
        instances = [cls(**item) for item in items]
        
        try:
            db.session.bulk_save_objects(instances)
            db.session.commit()
            return instances
        except Exception as e:
            db.session.rollback()
            raise e
    
    @classmethod
    def paginate(cls, page=1, per_page=20, **kwargs):
        """
        分页查询
        
        参数:
            page: 页码，从1开始
            per_page: 每页记录数
            **kwargs: 查询条件
        
        返回:
            分页对象
        """
        query = cls.query
        
        # 添加查询条件
        for key, value in kwargs.items():
            if hasattr(cls, key):
                query = query.filter(getattr(cls, key) == value)
        
        return query.paginate(
            page=page,
            per_page=per_page,
            error_out=False
        )
    
    def __repr__(self):
        """
        返回模型的字符串表示
        """
        return f"<{self.__class__.__name__} id={self.id}>"