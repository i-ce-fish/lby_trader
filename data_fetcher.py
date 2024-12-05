# -*- encoding: UTF-8 -*-

import datetime
import akshare as ak
import logging
import talib as tl
import logging

import concurrent.futures

from utils import DateHelper


def fetch(stock_code):
    # 起始日期取回测时间+120天前的数据
    start_date = DateHelper.get_days_before(120, DateHelper.get_end_date())
    format_start_date = DateHelper.date_to_str(DateHelper.str_to_date(start_date),"%Y%m%d")
    # 使用akshare获取股票数据, 捕获异常,并打印
    data = ak.stock_zh_a_hist(
            symbol=stock_code,     # 股票代码
            period="daily",        # 日线数据
            start_date= format_start_date, # 起始日期
            adjust="qfq"           # 前复权
        )
    if data.empty:
        logging.info("股票日线数据缺失:{}".format(stock_code))
        return None
    # 计算涨跌幅
    data['p_change'] = tl.ROC(data['收盘'], 1)
    return data

# 并发获取多个股票数据
def run(stocks):
    stocks_data = {}
    # 创建线程池，最多16个线程同时运行
    with concurrent.futures.ThreadPoolExecutor(max_workers=24) as executor:
        # 为每个股票创建一个future对象
        future_to_stock = {executor.submit(fetch, stock[0]): stock for stock in stocks}
        # 当有future完成时获取结果, 并打印索引
        for idx,future in enumerate(concurrent.futures.as_completed(future_to_stock)):
            print('数据获取进度:[{}/{}]'.format(idx + 1, len(future_to_stock)))
            stock = future_to_stock[future]
            try:
                data = future.result()
                if data is not None:
                    # 将成交量转换为double类型
                    data = data.astype({'成交量': 'double'})
                    stocks_data[stock] = data
            except Exception as exc:
                # 记录错误日志
                print('%s(%r) generated an exception: %s' % (stock[1], stock[0], exc))
                logging.error('%s(%r) generated an exception: %s' % (stock[1], stock[0], exc))
    return stocks_data


# 使用示例
if __name__ == "__main__":
    stocks =[(55, '000099', '海能达'),
             (1, '000099', '苏州天脉')]
    run(stocks)
