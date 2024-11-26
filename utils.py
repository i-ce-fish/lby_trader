# -*- coding: UTF-8 -*-
from datetime import datetime, timedelta
from typing import Union, Optional

# import sys
# from pathlib import Path
# # 添加项目根目录到Python路径
# sys.path.append(str(Path(__file__).parent.parent))
import settings


# 是否是工作日
def is_weekday():
    return datetime.today().weekday() < 5

# 是否是工作时间
def is_work_time():
    # 工作时间 9:30 - 15:00
    now = datetime.now()
    return (now.hour >= 9 and now.minute >= 25) and (now.hour < 15 and now.minute < 0)



class DateHelper:
    """日期操作辅助类"""
    
    DEFAULT_FMT = "%Y-%m-%d"  # 修改默认格式为 YYYY-MM-DD
    
    @staticmethod
    def str_to_date(date_str: str) -> datetime:
        """将字符串转换为datetime对象"""
        if not date_str:
            return datetime.now()
            
        formats = [
            "%Y-%m-%d",  # 把 YYYY-MM-DD 放在第一位
            "%Y%m%d",
            "%Y/%m/%d",
            "%Y.%m.%d"
        ]
        
        for fmt in formats:
            try:
                return datetime.strptime(date_str, fmt)
            except ValueError:
                continue
        raise ValueError(f"无法解析日期格式: {date_str}")
    
    @staticmethod
    def date_to_str(date: datetime, fmt: str = DEFAULT_FMT) -> str:
        """将datetime对象转换为字符串"""
        return date.strftime(fmt)
    
    @classmethod
    def add_days(cls, date: Union[str, datetime], days: int, 
                 out_fmt: str = DEFAULT_FMT) -> str:
        """日期加上指定天数"""
        if isinstance(date, str):
            date = cls.str_to_date(date)
        result = date + timedelta(days=days)
        return cls.date_to_str(result, out_fmt)
    
    @classmethod
    def sub_days(cls, date: Union[str, datetime], days: int, 
                 out_fmt: str = DEFAULT_FMT) -> str:
        """日期减去指定天数"""
        return cls.add_days(date, -days, out_fmt)
    
    @classmethod
    def get_date_range(cls, start: Union[str, datetime], 
                      end: Union[str, datetime], 
                      fmt: str = DEFAULT_FMT) -> list:
        """获取日期范围内的所有日期"""
        if isinstance(start, str):
            start = cls.str_to_date(start)
        if isinstance(end, str):
            end = cls.str_to_date(end)
            
        date_list = []
        curr_date = start
        while curr_date <= end:
            date_list.append(cls.date_to_str(curr_date, fmt))
            curr_date += timedelta(days=1)
        return date_list
    
    @classmethod
    def get_today(cls, fmt: str = DEFAULT_FMT) -> str:
        """获取今天的日期"""
        return cls.date_to_str(datetime.now(), fmt)

    
    @classmethod
    def get_end_date(cls, fmt: str = DEFAULT_FMT) -> str:
        """
        获取回测日期，如果无法从配置读取则返回今天
        """
        try:
            end_date = settings.config['end_date']
            return end_date
        except (AttributeError, KeyError, ImportError):
            # 返回今天日期的字符串，格式：YYYY-MM-DD
            return datetime.now().strftime('%Y-%m-%d')
        
        
    @classmethod
    def get_days_before(cls, days: int, 
                       end_date: Optional[Union[str, datetime]] = None,
                       out_fmt: str = DEFAULT_FMT) -> str:
        """获取指定日期前N天的日期"""
        if end_date is None:
            end_date = datetime.now()
        return cls.sub_days(end_date, days, out_fmt)
    
    # 数据库时间格式化
    @classmethod
    def db_time_to_date(cls, time: str) -> str:
        return datetime.strptime(time, '%Y-%m-%d %H:%M:%S.%f')

    # 获取最近一个工作日
    @classmethod
    def get_last_work_day(cls, fmt: str = DEFAULT_FMT) -> str:
        today = datetime.now()
        #  todo 死循环
        while not is_weekday():
            today = cls.sub_days(today, 1)
        return today

        
# 使用示例
if __name__ == "__main__":
    # 基本日期操作
    print(f"今天: {DateHelper.get_today()}")  # 2024-01-23
    print(f"120天前: {DateHelper.get_days_before(120)}")  # 2023-09-25
    
    # 日期加减
    test_date = "2024-07-19"
    print(f"测试日期加7天: {DateHelper.add_days(test_date, 7)}")  # 2024-07-26
    print(f"测试日期减7天: {DateHelper.sub_days(test_date, 7)}")  # 2024-07-12
    
    # 支持不同格式输入
    print(DateHelper.add_days("20240719", 1))  # 2024-07-20
    print(DateHelper.add_days("2024/07/19", 1))  # 2024-07-20
    
    # 获取日期范围
    date_range = DateHelper.get_date_range("20240101", "20240105")
    print(f"日期范围: {date_range}")

    # 获取回测日期
    # print(f"回测日期: {DateHelper.get_end_date()}")
    print(f"最近一个工作日: {DateHelper.get_last_work_day()}")
