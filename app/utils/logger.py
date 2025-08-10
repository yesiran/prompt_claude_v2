"""
日志管理模块
提供统一的日志记录功能，支持文件持久化和按日期切分
"""

import os
import sys
import logging
from logging.handlers import RotatingFileHandler, TimedRotatingFileHandler
from datetime import datetime
from pathlib import Path


class LoggerManager:
    """日志管理器"""
    
    def __init__(self, config):
        """
        初始化日志管理器
        
        参数:
            config: 配置对象
        """
        self.config = config
        self.loggers = {}
        self._setup_log_directory()
    
    def _setup_log_directory(self):
        """创建日志目录"""
        log_dir = Path(self.config.LOG_DIR)
        if not log_dir.exists():
            log_dir.mkdir(parents=True, exist_ok=True)
    
    def get_logger(self, name='app', log_file=None):
        """
        获取日志记录器
        
        参数:
            name: 日志记录器名称
            log_file: 日志文件名（不含路径）
        
        返回:
            Logger对象
        """
        if name in self.loggers:
            return self.loggers[name]
        
        logger = logging.getLogger(name)
        logger.setLevel(getattr(logging, self.config.LOG_LEVEL.upper()))
        
        # 防止重复添加handler
        if logger.handlers:
            return logger
        
        # 日志格式
        formatter = logging.Formatter(
            '[%(asctime)s] [%(levelname)s] [%(name)s] [%(filename)s:%(lineno)d] - %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        
        # 控制台输出
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setFormatter(formatter)
        logger.addHandler(console_handler)
        
        # 文件输出 - 按日期切分
        if log_file:
            file_path = os.path.join(self.config.LOG_DIR, log_file)
        else:
            # 默认日志文件名格式: prompt_project_log.2025-01-01.log
            file_path = os.path.join(
                self.config.LOG_DIR,
                f'prompt_project_log'
            )
        
        # 使用TimedRotatingFileHandler实现按日期切分
        file_handler = TimedRotatingFileHandler(
            filename=file_path,
            when='midnight',  # 每天午夜切分
            interval=1,  # 间隔1天
            backupCount=30,  # 保留30天的日志
            encoding='utf-8'
        )
        file_handler.suffix = "%Y-%m-%d.log"  # 文件后缀格式
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)
        
        # 错误日志单独记录
        error_file_path = os.path.join(
            self.config.LOG_DIR,
            'error_log'
        )
        error_handler = TimedRotatingFileHandler(
            filename=error_file_path,
            when='midnight',
            interval=1,
            backupCount=30,
            encoding='utf-8'
        )
        error_handler.suffix = "%Y-%m-%d.log"
        error_handler.setLevel(logging.ERROR)
        error_handler.setFormatter(formatter)
        logger.addHandler(error_handler)
        
        # 缓存logger
        self.loggers[name] = logger
        
        return logger
    
    def get_request_logger(self):
        """获取请求日志记录器"""
        return self.get_logger('request', 'request.log')
    
    def get_db_logger(self):
        """获取数据库日志记录器"""
        return self.get_logger('database', 'database.log')
    
    def get_api_logger(self):
        """获取API日志记录器"""
        return self.get_logger('api', 'api.log')


# 全局日志管理器实例
_logger_manager = None


def init_logger(config):
    """
    初始化日志管理器
    
    参数:
        config: 配置对象
    """
    global _logger_manager
    _logger_manager = LoggerManager(config)
    return _logger_manager


def get_logger(name='app', log_file=None):
    """
    获取日志记录器
    
    参数:
        name: 日志记录器名称
        log_file: 日志文件名
    
    返回:
        Logger对象
    """
    if _logger_manager is None:
        # 如果还没初始化，使用默认配置
        from config.config import get_config
        init_logger(get_config())
    
    return _logger_manager.get_logger(name, log_file)


def log_function_call(logger=None):
    """
    函数调用日志装饰器
    
    参数:
        logger: 日志记录器，如果不提供则使用默认logger
    
    使用示例:
        @log_function_call()
        def my_function(arg1, arg2):
            return result
    """
    def decorator(func):
        def wrapper(*args, **kwargs):
            nonlocal logger
            if logger is None:
                logger = get_logger()
            
            # 记录函数调用
            func_name = func.__name__
            logger.debug(f"调用函数 {func_name}, 参数: args={args}, kwargs={kwargs}")
            
            try:
                # 执行函数
                result = func(*args, **kwargs)
                logger.debug(f"函数 {func_name} 执行成功, 返回: {result}")
                return result
            except Exception as e:
                logger.error(f"函数 {func_name} 执行失败: {str(e)}", exc_info=True)
                raise
        
        return wrapper
    return decorator


def log_performance(logger=None):
    """
    性能日志装饰器，记录函数执行时间
    
    参数:
        logger: 日志记录器
    """
    import time
    
    def decorator(func):
        def wrapper(*args, **kwargs):
            nonlocal logger
            if logger is None:
                logger = get_logger()
            
            start_time = time.time()
            result = func(*args, **kwargs)
            elapsed_time = time.time() - start_time
            
            logger.info(f"函数 {func.__name__} 执行耗时: {elapsed_time:.3f}秒")
            
            return result
        
        return wrapper
    return decorator


class LogContext:
    """
    日志上下文管理器，用于批量记录相关日志
    
    使用示例:
        with LogContext('user_operation', user_id=123):
            # 这里的所有日志都会自动带上user_id=123的上下文
            logger.info("开始操作")
            # ... 执行操作
            logger.info("操作完成")
    """
    
    def __init__(self, context_name, **context_data):
        """
        初始化日志上下文
        
        参数:
            context_name: 上下文名称
            **context_data: 上下文数据
        """
        self.context_name = context_name
        self.context_data = context_data
        self.logger = get_logger()
    
    def __enter__(self):
        """进入上下文"""
        context_str = ', '.join([f"{k}={v}" for k, v in self.context_data.items()])
        self.logger.info(f"进入上下文 [{self.context_name}] - {context_str}")
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """退出上下文"""
        if exc_type:
            self.logger.error(f"上下文 [{self.context_name}] 异常退出: {exc_val}")
        else:
            self.logger.info(f"退出上下文 [{self.context_name}]")
        
        return False  # 不抑制异常