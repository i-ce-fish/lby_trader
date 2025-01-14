import math
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
    watch_stocks = [stock for stock in get_watching_stocks()]

    def init(self):
        print(f"策略初始化时的事件处理器：{self.main_engine.event_engine.queue_size}")
        for stock in self.watch_stocks:
            self.quotation_engine.watch(stock.code)
        # 创建信号监控管理器
        self.signal_manager = SignalMonitorManager(self.log)

    # 更新监听股票
    def update_watch_stocks(self):
        # 取消当前股票监听
        for stock in self.watch_stocks:
            self.quotation_engine.un_watch(stock.code)
        # 重新查询数据库更新监听
        self.watch_stocks = [stock for stock in get_watching_stocks()]
        for stock in self.watch_stocks:
            self.quotation_engine.watch(stock.code)

    def on_bar(self, context: Context, data: Dict[str, DataFrame]):
        self.update_watch_stocks()
        for stock in self.watch_stocks:
            stock_code = stock.code
            ddt_df = ddt(data[stock_code])
            # 过滤出最近一个工作日00:00:00到23:59:59之间的数据
            latest_day = data[stock_code].index[-1]
            start_time = latest_day.replace(hour=9, minute=30, second=0, microsecond=0)
            start_time_str = start_time.strftime('%Y-%m-%d %H:%M:%S')
            end_time = latest_day.replace(hour=15, minute=0, second=0, microsecond=0)
            # 过滤索引为今天的数据
            latest_data = ddt_df.loc[start_time_str:end_time.strftime('%Y-%m-%d %H:%M:%S')]
            stock_info = get_stock_info(stock_code)
            if stock_info:
                stock_id = stock_info.name
            else:
                stock_id = stock_code
            # 根据ddt_line绘制曲线，调试时需要
            # plot_basic(latest_data,latest_day.strftime('%Y-%m-%d')+'_'+stock_id+'.png')

            # 涨停判断数据预处理
            # 昨天收盘价
            yesterday_info = ddt_df.loc[:start_time_str].iloc[-2]
            yesterday_close = yesterday_info.close
            # 最新价格
            latest_info = latest_data.iloc[-1]
            # 涨停判断
            max_price = 0
            if stock_code.startswith('688') or stock_code.startswith('300') or stock_code.startswith('301'):
                # 保留2位小数, 但不四舍五入
                max_price = math.floor( 1.2 * yesterday_close * 10 ** 2) / 10 ** 2
            else:
                max_price = math.floor( 1.1 * yesterday_close * 10 ** 2) / 10 ** 2
            latest_data['max_price'] = max_price
           

            signals = self.signal_manager.check_signals(latest_data, stock_code, stock.is_buy_monitor)
            if len(signals)>0 :
                latest_info = latest_data.iloc[-1]
                signal_types = [signal[0] for signal in signals]  # 提取所有信号类型
                push_msg = f"[{' '.join(signal_types)}] {stock_id}: 由价格{latest_info.close}在{latest_data.index[-1].strftime('%H:%M:%S')}触发"
                push_res = wx_push(push_msg)
                self.log.info(f"推送消息: {push_msg}==>>>{push_res}")

            


    def on_close(self, context: Context):
        self.log.info("on_close")

    def on_open(self, context: Context):
        pass

    def shutdown(self):
        self.log.info("shutdown")
