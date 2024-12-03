import time
import datetime
from typing import List, Dict

from dateutil import tz
from pandas import DataFrame


from db.sqlite_utils import get_stock_info, get_watching_stocks
from default_handler import DefaultLogHandler
from easyquant import StrategyTemplate
from context import Context
from easyquant.event_engine import Event
from easytrader.model import Position
from trade_signal import SignalMonitorManager
from utils import DateHelper
from tdx.formula import ddt, plot_basic
from wx_pusher import wx_push

class Strategy(StrategyTemplate):
    name = 'example strategy'
    # 从数据库获取监听股票
    watch_stocks = [stock.code for stock in get_watching_stocks()]

    def init(self):
        print(f"策略初始化时的事件处理器：{self.main_engine.event_engine.queue_size}")
        for stock_code in self.watch_stocks:
            self.quotation_engine.watch(stock_code)
        # 创建信号监控管理器
        self.signal_manager = SignalMonitorManager(self.log)

    # 更新监听股票
    def update_watch_stocks(self):
        # 取消当前股票监听
        for stock_code in self.watch_stocks:
            self.quotation_engine.un_watch(stock_code)
        # 重新查询数据库更新监听
        self.watch_stocks = [stock.code for stock in get_watching_stocks()]
        for stock_code in self.watch_stocks:
            self.quotation_engine.watch(stock_code)

    def on_bar(self, context: Context, data: Dict[str, DataFrame]):
        self.log.info(f"on_bar: {self.watch_stocks}")
        self.update_watch_stocks()
        for stock_code in self.watch_stocks:
            # 过滤出最近一个工作日00:00:00到23:59:59之间的数据
            latest_day = data[stock_code].index[-1]
            start_time = latest_day.replace(hour=0, minute=0, second=0, microsecond=0)
            end_time = latest_day.replace(hour=23, minute=59, second=59, microsecond=999999)
            # todo 是否需要过滤前一天的数据 
            ddt_df = ddt(data[stock_code])
            # 过滤索引为今天的数据
            latest_data = ddt_df.loc[start_time.strftime('%Y-%m-%d %H:%M:%S'):end_time.strftime('%Y-%m-%d %H:%M:%S')]
            # 根据ddt_line绘制曲线，
            stock_info = get_stock_info(stock_code)
            if stock_info:
                stock_id = stock_info.name
            else:
                stock_id = stock_code
            plot_basic(latest_data,latest_day.strftime('%Y-%m-%d')+'_'+stock_id+'.png')
            signals = self.signal_manager.check_signals(latest_data, stock_code)
            if len(signals)>0 :
                latest_info = latest_data.iloc[-1]
                signal_types = [signal[0] for signal in signals]  # 提取所有信号类型
                push_msg = f"{stock_id}: {', '.join(signal_types)}, 由价格{latest_info.close}在{latest_data.index[-1]}触发."
                push_res = wx_push(push_msg)
                self.log.info(f"推送消息: {push_msg}==>>>{push_res}")

            


    def on_close(self, context: Context):
        self.log.info("on_close")

    def on_open(self, context: Context):
        pass

    def shutdown(self):
        self.log.info("shutdown")
