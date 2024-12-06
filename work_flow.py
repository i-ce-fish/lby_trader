# -*- encoding: UTF-8 -*-

from itertools import islice
import data_fetcher
from db.db_class import StockDailyData
import settings
import select_stock_strategy as enter
import akshare as ak
import wx_pusher
import logging
from datetime import datetime
from db.sqlite_utils import StockInfo, add_watch_stock, get_stock_info_by_name, get_watching_or_stopped_stocks, get_watching_stocks, init_db, save_stock_daily_data, save_stock_info, get_stock_info, get_all_stocks, update_stock_info
from utils import DateHelper
from decorators import handle_api_error
import pandas as pd
#  每周更新一次数据库
def updateDb():
    update_stock()
    update_fund()

# 更新股票数据库
def update_stock():
    logging.info('更新股票数据库')
    all_data = ak.stock_zh_a_spot_em()
    # 总市值	 流通市值	
    subset = all_data[['代码', '名称','最新价','涨跌幅','总市值','流通市值']]
    for _, row in subset.iterrows():
        save_stock_info(
            StockInfo(
                code=row['代码'],
                name=row['名称'],
                price=float(row['最新价']),
                change_pct=float(row['涨跌幅']),
                float_market_value=float(row['流通市值']),
                total_market_value=float(row['总市值'])
            )
        )

# 更新基金数据库
def update_fund():
    logging.info('更新基金数据库')
    fund_data = ak.fund_exchange_rank_em()
    for _, row in fund_data.iterrows():
        save_stock_info(
            StockInfo(
                code=row['基金代码'],
                name=row['基金简称'],
                price=float(row['单位净值'])
            )
        )
# 更新监听股票数据库
def update_listen_stocks():
    
    logging.info('更新stock-watching')

    all_data = get_all_stocks()
    subset = all_data[['序号','代码', '名称', '最新价']]

    # 转换为元组列表 
    stocks = [(tuple(x)[1], tuple(x)[2]) for x in subset.values]
    # 测试数据
    # stocks = [( '000882', '华联股份'),( '300100', '双林股份'),]
    # 获取股票数据  
    stocks_data = data_fetcher.run(stocks)
    end = settings.config['end_date']
    
    # 筛选周期4 too  需要配合同花顺资金流接口使用
    # head_dict = dict(islice(stocks_data.items(), 100))
    # zq4_results =  dict(filter(check_enter(end_date=end, strategy_fun=enter.check_ea), stocks_data.items()))
    # 筛选活跃股
    hyg_results = dict(filter(check_enter(end_date=end, strategy_fun=enter.check_hyg), stocks_data.items()))
    save_watch_stock(hyg_results)
    if len(hyg_results) > 0:
        hyg_msg = ''
        for stock in hyg_results.keys():
            hyg_msg += f"{stock[1].ljust(10)}\t{stock[0]}\n"
        wx_pusher.wx_push(f'[选股] \n{hyg_msg}\n{datetime.now().strftime("%Y-%m-%d %H:%M:%S")}')
    
    # 更新个股行情数据
    update_stock_daily_data(stocks_data)

def update_stock_daily_data(stocks_data):
    logging.info('更新监听/停止监听个股行情数据')
    watching_or_stopped_stocks = get_watching_or_stopped_stocks()
    for stock in watching_or_stopped_stocks:
        stock_key = (stock.code, stock.name)
        if stock_key in stocks_data and stocks_data[stock_key] is not None:
            df = stocks_data[stock_key]
            # 遍历df插入数据库
            for _, row in df.iterrows():
                date = pd.to_datetime(row['日期']).strftime('%Y%m%d')
                open = row['开盘']
                close = row['收盘']
                high = row['最高']
                low = row['最低']
                volume = row['成交量']
                amount = row['成交额']
                turnover_rate = row['换手率']
                change_pct = row['涨跌幅']
                change_amount = row['涨跌额']
                amplitude = row['振幅']
                save_stock_daily_data(StockDailyData(code=stock.code, 
                                                     name=stock.name, 
                                                     trade_date=date, 
                                                     open=open, 
                                                     close=close, 
                                                     high=high, 
                                                     low=low, 
                                                     volume=volume, 
                                                     amount=amount, 
                                                     amplitude=amplitude,
                                                     turnover_rate=turnover_rate, 
                                                     change_pct=change_pct, 
                                                     change_amount=change_amount,
                                                     ))
            

def save_watch_stock(stockList):
   # 保存到数据库
    for stock,df in stockList.items():
        code = stock[0]
        name = stock[1]
        price = df.iloc[0]['收盘']
        strategy = df.iloc[0]['strategy']
        add_watch_stock(code, name, price, strategy)

#  todo  后期可能要加上科创板
@handle_api_error(default_return=[])
def get_all_stocks():
    """获取所有主板+创业板股票数据"""
    all_data = ak.stock_zh_a_spot_em()
    if all_data is None:
        logging.error("获取所���股票数据失败")
        return []
    logging.info(f"获取所有股票数据成功, 数量: {len(all_data)}")
    # 使用正则表达式过滤掉北交所(8/9开头)、科创板(688开头)和其他特殊板块(4开头)的股票
    exclude_pattern = '^(8|9|4|688)'
    all_data = all_data[~all_data['代码'].str.match(exclude_pattern)]
    return all_data

# @deprecated 同花顺接口数据股票代码缺失严重,  不再使用, 且股票名称中空格/英文的处理与东财不一致
@handle_api_error(default_return=[])
def get_fund_flow():
    """获取资金流向数据, 20日排行, 阶段涨幅降序"""
    fund_flow_data = ak.stock_fund_flow_individual(symbol="20日排行")
    if fund_flow_data is None:
        logging.error("获取资金流向数据失败")
        return []
    # 遍历subset,如果股票代码不完整,  则从数据库获取
    subset = fund_flow_data[['序号',
                             '股票代码', 
                             '股票简称', 
                             '最新价']]
    # 处理接口股票代码不正确的情况
    def fix_code(row):
        code = row['股票代码']
        if len(str(code)) != 6:
            info = get_stock_info_by_name(row['股票简称'])
            if info:
                row['股票代码'] = info[0]
                return row
            else:
                # 删除row
                logging.info("股票代码不正确, 且无法找到:{}".format(row['股票简称']))
                return None
        return row
    # 过滤掉None
    subset = subset.apply(fix_code, axis=1).dropna()
    return subset



# 策略公共函数
def check_enter(end_date=None, strategy_fun=enter.check_volume):
    # 定义一个内部函数，用于过滤股票数据
    def end_date_filter(stock_data):
        # 如果end_date为空, 则不进行过滤
        if end_date is not None:
            # 如果end_date小于股票上市日期, 则不进行过滤
            if end_date < DateHelper.date_to_str(stock_data[1].iloc[0].日期):  # 该股票在end_date时还未上市
                logging.debug("{}在{}时还未上市".format(stock_data[0], end_date))
                return False
        # 执行策略
        return strategy_fun(stock_data[0], stock_data[1], end_date=end_date)
    return end_date_filter



