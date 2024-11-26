from datetime import datetime
from dataclasses import dataclass
from dataclasses import fields as dataclass_fields
from typing import Optional, List



@dataclass
class StockInfo:
    """股票基本信息数据类"""
    code: str                          # 股票代码
    name: str = None                   # 股票名称
    price: Optional[float] = None      # 当前价格
    change_pct: Optional[float] = None # 涨跌幅
    float_shares: Optional[float] = None    # 流通股本(万股)
    total_shares: Optional[float] = None    # 总股本(万股)
    float_market_value: Optional[float] = None  # 流通市值(万元)
    total_market_value: Optional[float] = None  # 总市值(万元)
    pe_ratio: Optional[float] = None      # 市盈率
    listing_date: Optional[str] = None    # 上市时间
    update_time: Optional[str] = None  # 更新时间


@dataclass
class WatchingStock:
    """股票监听数据类"""
    code: str                          # 股票代码
    name: str                          # 股票名称
    strategy: str                      # 策略名称
    watch_status: str                  # 监听状态：监听中/已停止/已触发
    id: Optional[int] = None           # 主键ID
    current_price: Optional[float] = None  # 最新价格
    create_time: Optional[datetime] = None  # 创建时间
    update_time: Optional[datetime] = None  # 更新时间
