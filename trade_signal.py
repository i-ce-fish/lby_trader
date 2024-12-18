from dataclasses import dataclass
from datetime import datetime
from typing import Optional, Tuple, List
import pandas as pd
import logging

logger = logging.getLogger(__name__)

@dataclass
class TradeSignal:
    stock_code: str # 股票代码
    current_value: float # 当前值
    extreme_value: float | None # 极值
    change_ratio: float | None # 变化比例
    time: datetime | None # 时间

@dataclass
class SignalParams:
    threshold: float # 阈值
    percent: float # 百分比
    column: str # 数据列名

@dataclass
class ThresholdParams(SignalParams):
    drawdown_percent: float = 0.01  # 回撤阈值，默认1%, 回撤超过阈值后重置通知状态

# 信号参数常量定义
BUY_POINT_PARAMS = SignalParams(threshold=90, percent=0.05, column='dz')     # 峰值回撤参数
SELL_POINT_PARAMS = SignalParams(threshold=-5, percent=0.05, column='dz')    # 波谷反弹参数
QUICK_PULLUP_PARAMS = SignalParams(threshold=3, percent=0.015, column='sp')    # 拉升信号参数
START_PULLUP_PARAMS = SignalParams(threshold=3, percent=0, column='sp')    # 开始拉升参数
ZT_PARAMS = ThresholdParams(threshold=0, percent=0, column=None, drawdown_percent=0.985)    # 涨停信号参数

class SignalMonitorBase:
    
    def __init__(self, params: SignalParams | None = None, log: logging.Logger = None):
        self.threshold = params.threshold
        self.percent = params.percent
        self.is_monitoring = False
        self.notified = False
        self.column = params.column
        self.log = log
        self.latest_time = None # 最新监听时间
    def _reset_state(self):
        self.is_monitoring = False
        self.notified = False


# 峰值回撤监控
class PeakDrawdownMonitor(SignalMonitorBase):
    def __init__(self, params: SignalParams, log: logging.Logger):
        super().__init__(params, log)
        self.max_value = 0
    def on_tick(self, df: pd.DataFrame, stock_code: str) -> Optional[TradeSignal]:
        try:

            value = df[self.column].iloc[-1]
            current_time = df.index[-1]

            # 如果当前时间与最新监听时间相同
            if self.latest_time and (current_time == self.latest_time):
                return None
                
            self.latest_time = current_time
            
            if value < self.threshold:
                self._reset_state()
                return None
                
            if value >= self.threshold:
                if not self.is_monitoring:
                    self.is_monitoring = True
                    self.max_value = value
                elif value > self.max_value:
                    self.max_value = value
                
            if self.is_monitoring and not self.notified:
                drawdown = (self.max_value - value) / self.max_value
                if drawdown >= self.percent:
                    self.notified = True
                    return TradeSignal(stock_code, value, self.max_value, drawdown, current_time)
            return None
        except Exception as e:
            self.log.error(f"峰值回撤监控异常: {e}", exc_info=True)
            return None
            
    def _reset_state(self):
        super()._reset_state()
        self.max_value = 0

# 波谷反弹监控
class ValleyBounceMonitor(SignalMonitorBase):
    def __init__(self, params: SignalParams, log: logging.Logger):
        super().__init__(params, log)
        self.min_value = float('inf')
    def on_tick(self, df: pd.DataFrame, stock_code: str) -> Optional[TradeSignal]:
        try:
            value = df[self.column].iloc[-1]
            current_time = df.index[-1]

            # 如果当前时间与最新监听时间相同,
            if self.latest_time and (current_time == self.latest_time):
                return None

            self.latest_time = current_time

            if value > self.threshold:
                self._reset_state()
                return None
                
            if value <= self.threshold:
                if not self.is_monitoring:
                    self.min_value = value
                    self.is_monitoring = True
                if value < self.min_value:
                    self.min_value = value
                

            if self.is_monitoring and not self.notified:
                if self.min_value == 0:
                    bounce = value - self.min_value
                else:
                    bounce = (value - self.min_value) / self.min_value
                if abs(bounce) >= self.percent:
                    self.notified = True
                    return TradeSignal(stock_code, value, self.min_value, bounce, current_time)
            return None
        except Exception as e:
            self.log.error(f"波谷反弹监控异常: {e}", exc_info=True)
            return None
            
    def _reset_state(self):
        super()._reset_state()
        self.min_value = float('inf')

# 新增阈值监控类
class ThresholdMonitor(SignalMonitorBase):
    def __init__(self, params: SignalParams, log: logging.Logger):
        super().__init__(params, log)
        self.max_value = None  # 记录触发后的最大值
        # self.drawdown_percent = params.drawdown_percent  # 回撤阈值，可以通过参数配置
        
    def on_tick(self, df: pd.DataFrame, stock_code: str) -> Optional[TradeSignal]:
        try:
            value = df[self.column].iloc[-1]
            current_time = df.index[-1]

            # 如果当前时间与最新监听时间相同
            if self.latest_time and (current_time == self.latest_time):
                return None
                
            self.latest_time = current_time
            
            # 当值超过阈值且未通知时触发信号
            if value > self.threshold and not self.notified:
                self.notified = True
                self.max_value = value
                return TradeSignal(
                    stock_code=stock_code,
                    current_value=value,
                    extreme_value=self.threshold,
                    change_ratio=0,  # 阈值监控不需要计算变化比例
                    time=current_time
                )
            
            # 更新最大值
            if self.notified and value > self.max_value:
                self.max_value = value
            
            # 检查回撤重置条件
            # if self.notified and self.max_value:
            #     drawdown = (self.max_value - value) / self.max_value
            #     if drawdown >= self.drawdown_percent:
            #         self._reset_state()
            #         self.max_value = None
            
            # 当值低于阈值时重置状态
            if value < self.threshold:
                self._reset_state()
                self.max_value = None
                
            return None
        except Exception as e:
            self.log.error(f"阈值监控异常: {e}", exc_info=True)
            return None

class ZtMonitor(SignalMonitorBase):
    def __init__(self, params: ThresholdParams, log: logging.Logger):
        super().__init__(params, log)
        self.drawdown_percent = params.drawdown_percent

    def on_tick(self, df: pd.DataFrame, stock_code: str) -> Optional[TradeSignal]:
        max_price = df['max_price'].iloc[-1]
        close = df['close'].iloc[-1]
        is_zt = close >= max_price
        current_time = df.index[-1]
        if not self.notified and is_zt:
            self.notified = True
            return TradeSignal(stock_code, close, 0, 0, current_time)

        if self.notified and not is_zt and close < max_price * self.drawdown_percent:
            self._reset_state()
            return None
        return None
    
    def _reset_state(self):
        super()._reset_state()


class ZtFallMonitor(SignalMonitorBase):
    def __init__(self, params: ThresholdParams, log: logging.Logger):
        super().__init__(params, log)
        self.drawdown_percent = params.drawdown_percent
    
    def on_tick(self, df: pd.DataFrame, stock_code: str) -> Optional[TradeSignal]:
        max_price = df['max_price'].iloc[-1]
        close = df['close'].iloc[-1]
        is_zt = close >= max_price
        is_zt_before = (df['close'] >= df['max_price']).any()
        is_zt_fall = close < max_price * self.drawdown_percent
        current_time = df.index[-1]
        if not self.notified and is_zt_before and is_zt_fall:
            self.notified = True
            return TradeSignal(stock_code, close, 0, 0, current_time)

        if self.notified and is_zt:
            self._reset_state()
            return None
        return None
        
    
    def _reset_state(self):
        super()._reset_state()



class SignalMonitorManager:
    def __init__(self, log: logging.Logger):
        self.log = log
        #  买点监控
        self.buy_point_monitors: dict[str, PeakDrawdownMonitor] = {}
        #  卖点监控
        self.sell_point_monitors: dict[str, ValleyBounceMonitor] = {}
        #  快速拉升后回落监控
        self.quick_pullup_monitors: dict[str, PeakDrawdownMonitor] = {}  
        #  开始拉升监控
        self.start_pullup_monitors: dict[str, ThresholdMonitor] = {}
        #  涨停监控
        self.zt_monitors: dict[str, ZtMonitor] = {}
        #  涨停后回落监控
        self.zt_fall_monitors: dict[str, ZtFallMonitor] = {}
        
    def check_signals(self, df: pd.DataFrame, stock_code: str) -> List[Tuple[str, TradeSignal]]:
        # 初始化监控器
        if stock_code not in self.buy_point_monitors:
            self.buy_point_monitors[stock_code] = PeakDrawdownMonitor(BUY_POINT_PARAMS, self.log)
            self.sell_point_monitors[stock_code] = ValleyBounceMonitor(SELL_POINT_PARAMS, self.log)
            self.quick_pullup_monitors[stock_code] = PeakDrawdownMonitor(QUICK_PULLUP_PARAMS, self.log)
            self.start_pullup_monitors[stock_code] = ThresholdMonitor(START_PULLUP_PARAMS, self.log)
            self.zt_monitors[stock_code] = ZtMonitor(ZT_PARAMS, self.log)
            self.zt_fall_monitors[stock_code] = ZtFallMonitor(ZT_PARAMS, self.log)
        signals = []
        
        # 检查峰值回撤信号
        if buy_point_signal := self.buy_point_monitors[stock_code].on_tick(df, stock_code):
            signals.append(('买点', buy_point_signal))
            
        # 检查波谷反弹信号
        if sell_point_signal := self.sell_point_monitors[stock_code].on_tick(df, stock_code):
            signals.append(('卖点', sell_point_signal))
            
        # 检查拉升信号
        if quick_pullup_signal := self.quick_pullup_monitors[stock_code].on_tick(df, stock_code):
            signals.append(('结束拉升', quick_pullup_signal))
            
        # 检查拉升信号
        if start_pullup_signal := self.start_pullup_monitors[stock_code].on_tick(df, stock_code):
            signals.append(('开始拉升', start_pullup_signal))
        
        # 检查涨停信号
        if zt_signal := self.zt_monitors[stock_code].on_tick(df, stock_code):
            signals.append(('涨停', zt_signal))

        # 检查涨停后回落信号
        if zt_fall_signal := self.zt_fall_monitors[stock_code].on_tick(df, stock_code):
            signals.append(('涨停后回落', zt_fall_signal))



        return signals