"""
测试记录模型
定义Prompt测试记录表结构
"""

from .base import db, BaseModel


class TestRecord(BaseModel):
    """测试记录模型"""
    
    __tablename__ = 'test_records'
    
    # Prompt ID
    prompt_id = db.Column(
        db.Integer,
        db.ForeignKey('prompts.id', ondelete='CASCADE'),
        nullable=False,
        comment='Prompt ID'
    )
    
    # 版本ID
    version_id = db.Column(
        db.Integer,
        db.ForeignKey('prompt_versions.id', ondelete='SET NULL'),
        default=None,
        comment='版本ID'
    )
    
    # 测试用户ID
    user_id = db.Column(
        db.Integer,
        db.ForeignKey('users.id'),
        nullable=False,
        comment='测试用户ID'
    )
    
    # 模型名称
    model_name = db.Column(
        db.String(50),
        nullable=False,
        comment='模型名称'
    )
    
    # 模型参数（JSON格式）
    model_params = db.Column(
        db.JSON,
        default=None,
        comment='模型参数'
    )
    
    # 输入token数
    input_tokens = db.Column(
        db.Integer,
        default=0,
        comment='输入token数'
    )
    
    # 输出token数
    output_tokens = db.Column(
        db.Integer,
        default=0,
        comment='输出token数'
    )
    
    # 响应时间（秒）
    response_time = db.Column(
        db.Numeric(10, 3),
        default=None,
        comment='响应时间(秒)'
    )
    
    # 测试输入
    test_input = db.Column(
        db.Text,
        default=None,
        comment='测试输入'
    )
    
    # 测试输出
    test_output = db.Column(
        db.Text,
        default=None,
        comment='测试输出'
    )
    
    # 测试状态
    status = db.Column(
        db.Enum('success', 'failed', 'timeout'),
        default='success',
        comment='测试状态'
    )
    
    # 错误信息
    error_message = db.Column(
        db.Text,
        default=None,
        comment='错误信息'
    )
    
    # 关系定义
    tester = db.relationship(
        'User',
        backref='test_records',
        foreign_keys=[user_id]
    )
    
    version = db.relationship(
        'PromptVersion',
        backref='test_records',
        foreign_keys=[version_id]
    )
    
    def get_total_tokens(self):
        """
        获取总token数
        
        返回:
            int: 总token数
        """
        return self.input_tokens + self.output_tokens
    
    def calculate_cost(self, input_price_per_1k=0.01, output_price_per_1k=0.03):
        """
        计算测试成本（示例计算）
        
        参数:
            input_price_per_1k: 每1000个输入token的价格
            output_price_per_1k: 每1000个输出token的价格
        
        返回:
            float: 测试成本
        """
        input_cost = (self.input_tokens / 1000) * input_price_per_1k
        output_cost = (self.output_tokens / 1000) * output_price_per_1k
        return round(input_cost + output_cost, 4)
    
    @classmethod
    def get_user_tests(cls, user_id, limit=None):
        """
        获取用户的测试记录
        
        参数:
            user_id: 用户ID
            limit: 返回数量限制
        
        返回:
            TestRecord列表
        """
        query = cls.query.filter_by(user_id=user_id).order_by(cls.created_at.desc())
        
        if limit:
            query = query.limit(limit)
        
        return query.all()
    
    @classmethod
    def get_prompt_tests(cls, prompt_id, limit=None):
        """
        获取Prompt的测试记录
        
        参数:
            prompt_id: Prompt ID
            limit: 返回数量限制
        
        返回:
            TestRecord列表
        """
        query = cls.query.filter_by(prompt_id=prompt_id).order_by(cls.created_at.desc())
        
        if limit:
            query = query.limit(limit)
        
        return query.all()
    
    @classmethod
    def get_model_statistics(cls, prompt_id):
        """
        获取不同模型的测试统计
        
        参数:
            prompt_id: Prompt ID
        
        返回:
            dict: 模型统计信息
        """
        tests = cls.query.filter_by(prompt_id=prompt_id).all()
        
        stats = {}
        for test in tests:
            model = test.model_name
            if model not in stats:
                stats[model] = {
                    'total_tests': 0,
                    'success_count': 0,
                    'failed_count': 0,
                    'avg_response_time': 0,
                    'total_response_time': 0
                }
            
            stats[model]['total_tests'] += 1
            
            if test.status == 'success':
                stats[model]['success_count'] += 1
            elif test.status == 'failed':
                stats[model]['failed_count'] += 1
            
            if test.response_time:
                stats[model]['total_response_time'] += float(test.response_time)
        
        # 计算平均响应时间
        for model in stats:
            if stats[model]['total_tests'] > 0:
                stats[model]['avg_response_time'] = round(
                    stats[model]['total_response_time'] / stats[model]['total_tests'],
                    3
                )
            del stats[model]['total_response_time']  # 删除临时字段
        
        return stats
    
    def __repr__(self):
        """返回测试记录的字符串表示"""
        return f"<TestRecord {self.id} {self.model_name}>"