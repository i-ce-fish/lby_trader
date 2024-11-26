import logging
from functools import wraps
import time

def handle_api_error(default_return=None):
    """处理API调用异常的装饰器"""
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            try:
                result = func(*args, **kwargs)
                if result is None:
                    logging.error(f"{func.__name__} 返回空数据")
                    return default_return
                return result
            except Exception as e:
                logging.error(f"{func.__name__} 调用失败: {str(e)}")
                print(f"{func.__name__} 调用失败: {str(e)}")
                return default_return
        return wrapper
    return decorator 


 

def timer(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        start = time.time()
        result = func(*args, **kwargs)
        end = time.time()
        print(f"{func.__name__} 执行时间: {end - start:.4f} 秒")
        return result
    return wrapper