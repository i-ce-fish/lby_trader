import pandas as pd
import data_fetcher
from db.sqlite_utils import StockInfo, update_stock_info
from decorators import timer
import settings
from select_stock_strategy import check_ea
from tdx.MyTT import WINNER
from work_flow import check_enter
import akshare as ak
from talib_ext_cpp.tdx_indicator_base import WINNER  as winner2

def test():
    settings.init()
    # print(check_zq4())   
    # 11
    # stocks =   ["000066","603529","002428","601117"]
    # for code in stocks:
    #     check_update_stock_info(code)
    # 22
    check_winner()

def check_winner():
    # 更有代表性的测试数据
    test_data = pd.DataFrame({
        'high':   [10, 11, 9],     # 先上涨后下跌
        'low':    [9,  10, 8],
        'volume': [1000, 1000, 1000],
        'amount': [9500, 10500, 8500],
        'close':  [9.5, 10.5, 8.5]
})
    
    print('test winner')
    print(my_winner(test_data))
    print('---')
    print(WINNER(test_data, test_data['close']*0.95))


@timer
def my_winner(data, price_series=None):
    return WINNER(data, price_series)
# 测试周期4选股
def check_zq4():
    # 获取股票数据  
    stock = (55, '000099', '中信海直')
    stock_data = data_fetcher.run([stock])
    result = check_ea(stock, stock_data[stock],  settings.config['end_date'])
    return result

# 测试更新股票信息
def check_update_stock_info(stock_code:str):
    stock_info = ak.stock_individual_info_em(symbol=stock_code)
    update_stock_info(StockInfo(code=stock_code,
                                    listing_date=stock_info['value'][7],
                                    float_shares=stock_info['value'][3],
                                    total_shares=stock_info['value'][2]))


if __name__ == '__main__':
    test()
