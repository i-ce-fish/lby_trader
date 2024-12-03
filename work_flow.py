# -*- encoding: UTF-8 -*-

from itertools import islice
import data_fetcher
import settings
import select_stock_strategy as enter
import akshare as ak
import wx_pusher
import logging
from datetime import datetime
from db.sqlite_utils import StockInfo, add_watch_stock, get_stock_info_by_name, get_watching_stocks, init_db, save_stock_info, get_stock_info, get_all_stocks, update_stock_info
from utils import DateHelper
from decorators import handle_api_error

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
    # 获取股票数据  
    stocks_data = data_fetcher.run(stocks)
    end = settings.config['end_date']
    # 筛选周期4
    head_dict = dict(islice(stocks_data.items(), 100))
    zq4_results =  dict(filter(check_enter(end_date=end, strategy_fun=enter.check_ea), head_dict.items()))
    # 筛选活跃股
    hyg_results = dict(filter(check_enter(end_date=end, strategy_fun=enter.check_hyg), stocks_data.items()))
    results = {**zq4_results, **hyg_results}
    # 保存到数据库
    for stock,df in results.items():
        code = stock[0]
        name = stock[1]
        price = df.iloc[0]['收盘']
        strategy = df.iloc[0]['strategy']
        add_watch_stock(code, name, price, strategy)
    if len(results) > 0:
        zq4_msg = '周期4: '+','.join(str(x[1]) for x in list(zq4_results.keys()))
        hyg_msg = '活跃股: '+','.join(str(x[1]) for x in list(hyg_results.keys()))
        time  = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        wx_pusher.wx_push('选股: '+hyg_msg+ '-----'+zq4_msg+ ' '+time)

#  todo  后期可能要加上科创板
@handle_api_error(default_return=[])
def get_all_stocks():
    """获取所有主板+创业板股票数据"""
    all_data = ak.stock_zh_a_spot_em()
    if all_data is None:
        logging.error("获取所有股票数据失败")
        return []
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



