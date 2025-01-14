# -*- encoding: UTF-8 -*-

from datetime import datetime
import talib
import pandas as pd
import logging
# 关闭 SettingWithCopyWarning 警告
pd.options.mode.chained_assignment = None
from utils import DateHelper
#  筛选活跃股(一阳四线)
# @param stock 股票代码
# @param data 股票日线数据
# @param end_date 结束日期
def check_hyg(stock, df, end_date=None):
    # todo 环境系数 通过主板+创业板+涨跌家数+平均股价+涨跌停家属联合判断判断环境
    env_factor = 1.0
    # 大阳线当天涨幅阈值(%)
    cross_day_threshold = 8 * env_factor
    # 大阳线当天成交额系数
    cross_day_volume_factor = 1.5 * env_factor
    # 阳线后平均成交额系数
    after_cross_day_volume_factor = 1.5 * env_factor
    # 阳线当天换手率阈值(%)
    cross_day_turnover_threshold = 3.5 * env_factor
    # 兑现涨幅阈值(.)
    trigger_threshold = 0.1 * env_factor
    # 大阴线跌幅阈值(.)
    big_drop_threshold = -0.06 * env_factor
    # 以前的最高点涨幅阈值(%)
    previous_highest_threshold = 1.05 * env_factor
    # 均线穿越窗口期
    cross_ma_window = 5

    # 过滤次新股
    if check_new(stock, df, end_date):
        return False
    """
    检查股票是否满足选股条件(一阳四线选股)
    df: DataFrame，需要包含 'open' 和 'close' 列
    """
    # 计算各均线
    df['MA4'] = df['收盘'].rolling(window=4).mean()
    df['MA5'] = df['收盘'].rolling(window=5).mean()
    df['MA10'] = df['收盘'].rolling(window=10).mean()
    df['MA20'] = df['收盘'].rolling(window=20).mean()
    df['MA30'] = df['收盘'].rolling(window=30).mean()
    
    # 计算开盘价低于均线条件
    df['below_ma'] = (df['开盘'] < df['MA5']) & \
               (df['开盘'] < df['MA10']) & \
               (df['开盘'] < df['MA20']) & \
               (df['开盘'] < df['MA30'])
    
    # 计算收盘价高于均线条件
    df['above_ma'] = (df['收盘'] > df['MA5']) & \
               (df['收盘'] > df['MA10']) & \
               (df['收盘'] > df['MA20']) & \
               (df['收盘'] > df['MA30'])
    # 计算当天是否出现均线穿越信号（开盘价低于均线且收盘价高于均线）
    df['cross_ma'] = df['below_ma'] & df['above_ma']
    # 判断最近5天内是否存在均线穿越信号
    # 1. rolling(window=5) 取最近5天的数据
    # 2. sum() 计算5天内穿越信号的出现次数
    # 3. > 0 表示只要5天内出现过一次穿越信号就为True
    df['cross_ma_exist'] = df['cross_ma'].rolling(window=cross_ma_window).sum() > 0
    
    # 均线多头排列条件
    df['MA_trend'] = (df['MA4'] > df['MA10']) & (df['MA10'] > df['MA30'])
    
    # 最终XG条件
    df['yx_signal'] = df['cross_ma_exist'] & df['MA_trend']
    # 判断最后一天是否满足均线多头排列
    result = df['yx_signal'].iloc[-1]
    if not  result:
        return False
    last_5_days = df.iloc[-5:]
    # 找出最近5天内满足穿越条件的具体日期
    cross_day = last_5_days[last_5_days['cross_ma']]
    cross_day_index = cross_day.index[0]
    cross_day_info = cross_day.iloc[0]


    level = 1
    # 放量2倍以上
    after_cross_day = last_5_days.loc[cross_day_index:]
    # 阳线后的天数
    after_cross_day_count = after_cross_day.shape[0]
    # 阳线后成交额总和
    after_cross_day_volume = after_cross_day['成交额'].sum()    


    level += 1
    # 过滤大阳线当天涨幅小于5
    if cross_day_info['涨跌幅'] <  5:
        print(f"{level}. 阳线当天涨幅不足: {cross_day_info['涨跌幅']}小于5%,{stock}")
        logging.info(f"{level}. 阳线当天涨幅不足: {cross_day_info['涨跌幅']}小于5%,{stock}")
        return False

    level += 1
    # 阳线当天换手率
    if cross_day_info['换手率'] < cross_day_turnover_threshold:
        print(f"{level}. 换手率不足: 阳线当天换手率{cross_day_info['换手率']}%小于{cross_day_turnover_threshold}%,{stock}")
        logging.info(f"{level}. 换手率不足: 阳线当天换手率{cross_day_info['换手率']}%小于{cross_day_turnover_threshold}%,{stock}")
        return False
    
    level += 1
    # 阳线前成交额总和
    before_cross_day = df.loc[cross_day.index[0]-after_cross_day_count:cross_day.index[0]-1]
    before_cross_day_volume = before_cross_day['成交额'].sum()
    if after_cross_day_count > 0 and after_cross_day_volume  < before_cross_day_volume * after_cross_day_volume_factor:
        print(f"{level}. 成交额不足: 阳线后成交额{after_cross_day_volume/100000000:.2f}亿小于阳线前成交额{before_cross_day_volume/100000000:.2f}亿的{after_cross_day_volume_factor}倍,{stock}")
        logging.info(f"{level}. 成交额不足: 阳线后成交额{after_cross_day_volume/100000000:.2f}亿小于阳线前成交额{before_cross_day_volume/100000000:.2f}亿的{after_cross_day_volume_factor}倍,{stock}")
        return False

    level += 1
    # 阳线当天成交额2亿以上
    if cross_day_info['成交额'] < 200000000:
        print(f"{level}. 成交额不足: 阳线当天成交额{cross_day_info['成交额']/100000000:.2f}亿小于2亿,{stock}")
        logging.info(f"{level}. 成交额不足: 阳线当天成交额{cross_day_info['成交额']/100000000:.2f}亿小于2亿,{stock}")
        return False


    level += 1
    # 阳线当天成交额是前2天平均的1.5倍以上
    avg_vol_before_cross_day = df.loc[cross_day.index[0]-3:cross_day.index[0]-1]['成交额'].mean() / 2
    if cross_day_info['成交额'] < avg_vol_before_cross_day * cross_day_volume_factor:
        print(f"{level}. 成交额倍数不足: 阳线当天成交额{cross_day_info['成交额']/100000000:.2f}小于阳线前2天平均的{cross_day_volume_factor}倍,{stock}")
        logging.info(f"{level}. 成交额倍数不足: 阳线当天成交额{cross_day_info['成交额']/100000000:.2f}小于阳线前2天平均的{cross_day_volume_factor}倍,{stock}")
        return False

    level += 1
    # 过滤阳线后出现大阴线 任意一天开收幅大于阈值
    after_cross_day['开收幅'] = (after_cross_day['收盘'] - after_cross_day['开盘']) / after_cross_day['开盘']
    if (after_cross_day['开收幅'] < big_drop_threshold).any():
        print(f"{level}. 阳线后出现大阴线: {','.join(f'{x*100:.2f}%' for x in after_cross_day['开收幅'])},{stock}")
        logging.info(f"{level}. 阳线后出现大阴线: {','.join(f'{x*100:.2f}%' for x in after_cross_day['开收幅'])},{stock}")
        return False
    
    

    level += 1
    #  过滤阳线后累计涨幅, 涨幅大于阈值
    last_close = df.iloc[-1]['收盘']
    cross_day_close = cross_day_info['收盘']
    # 阳线当日均价计算
    cross_day_avg = (cross_day_info['最高'] + cross_day_info['最低'] + cross_day_info['收盘']) / 3
    # 涨幅
    increase_rate_after_cross_day = (last_close - cross_day_close) / cross_day_close
    if increase_rate_after_cross_day > trigger_threshold:
        print(f"{level}. 涨幅兑现: 阳线后累计涨幅{increase_rate_after_cross_day*100:.2f}%,{stock}")
        logging.info(f"{level}. 涨幅兑现: 阳线后累计涨幅{increase_rate_after_cross_day*100:.2f}%,{stock}")
        return False



    
    # level += 1
    # # 过滤跌破阳线均价
    # if last_close < cross_day_avg:
    #     print(f"{level}. 跌破阳线均价: {last_close},{stock}")
    #     logging.info(f"{level}. 跌破阳线均价: {last_close},{stock}")
    #     return False



    level += 1
    # 过滤跌破阳线开盘价
    if last_close < cross_day_info['开盘']:
        print(f"{level}. 跌破阳线开盘价: {last_close},{stock}")
        logging.info(f"{level}. 跌破阳线开盘价: {last_close},{stock}")
        return False

 
    level += 1
    # 过滤大阳线后, 任意一天涨停
    if (after_cross_day[1:]['涨跌幅'] > 10).any():
        print(f"{level}. 大阳线后涨停任意一天: {','.join(f'{x:.2f}%' for x in after_cross_day['涨跌幅'])},{stock}")
        logging.info(f"{level}. 大阳线后涨停任意一天: {','.join(f'{x:.2f}%' for x in after_cross_day['涨跌幅'])},{stock}")
        return False
    

    
    level += 1
    # 过滤50天前到7天前,最高收盘价超过当前价5%以上
    max_price = df['收盘'][:-7].rolling(window=50).max()
    if max_price.iloc[-1] > last_close * previous_highest_threshold:
        print(f"{level}. 前期大涨: 前期最高收盘价{max_price.iloc[-1]}超过当前价{last_close}的{previous_highest_threshold}%以上,{stock}")
        logging.info(f"{level}. 前期大涨: 前期最高收盘价{max_price.iloc[-1]}超过当前价{last_close}的{previous_highest_threshold}%以上,{stock}")
        return False
    



    level += 1
    # 过滤大阳线当天涨幅小于阈值
    if cross_day_info['涨跌幅'] <  cross_day_threshold:
        print(f"{level}. 大阳线当天涨幅: {cross_day_info['涨跌幅']}小于{cross_day_threshold}%{stock}")
        logging.info(f"大阳线当天涨幅: {cross_day_info['涨跌幅']}小于{cross_day_threshold}%{stock}")
        return False
    
    
    level += 1
    # 过滤天量收绿
    after_cross_day['天量'] = (after_cross_day['成交额'] > cross_day_info['成交额'] * 2) & (after_cross_day['开收幅'] < -(0.1/100))
    if after_cross_day['天量'].any():
        print(f"{level}. 天量收绿: {stock}")
        logging.info(f"{level}. 天量收绿: {stock}")
        return False  
  
    df['strategy'] = '活跃股'
    df['cross_day_increase_rate'] = cross_day_info['涨跌幅']
    print(f"=========>>>>>>>>>>>>选中活跃股，{stock}")
    logging.info(f"=========>>>>>>>>>>>>选中活跃股，{stock}")

    # 形态识别,ps需要冗余的数据才能识别
    df_talib = df.loc[cross_day.index[0]-5:]
    check_pattern(df_talib, df_talib['开盘'], df_talib['最高'], df_talib['最低'], df_talib['收盘'])
    # 统计结果
    pattern_funcs = get_pattern()
    for index, value in df_talib.iterrows():
        for key in pattern_funcs.items():
            if value[key[0]] != 0:
                print(f"日期:{df['日期'][index]}, 值:{key[0]}{value[key[0]]}")
                logging.info(f"日期:{df['日期'][index]}, 值:{key[0]}{value[key[0]]}")

    return True
def get_pattern():
    # https://github.com/HuaRongSAO/talib-document/blob/master/func_groups/pattern_recognition.md
    # https://zhuanlan.zhihu.com/p/12576661931
    # 定义形态识别函数字典
    pattern_funcs = {
        '两只乌鸦': talib.CDL2CROWS,
        '三只乌鸦': talib.CDL3BLACKCROWS,
        '三内部上涨和下跌': talib.CDL3INSIDE,
        '三线打击': talib.CDL3LINESTRIKE,
        '三外部上涨和下跌': talib.CDL3OUTSIDE,
        '南方三星': talib.CDL3STARSINSOUTH,
        '三个白兵': talib.CDL3WHITESOLDIERS,
        '弃婴': talib.CDLABANDONEDBABY,
        '大敌当前': talib.CDLADVANCEBLOCK,
        '捉腰带线': talib.CDLBELTHOLD,
        '脱离': talib.CDLBREAKAWAY,
        '收盘缺影线': talib.CDLCLOSINGMARUBOZU,
        '藏婴吞没': talib.CDLCONCEALBABYSWALL,
        '反击线': talib.CDLCOUNTERATTACK,
        '乌云压顶': talib.CDLDARKCLOUDCOVER,
        '十字': talib.CDLDOJI,
        '十字星': talib.CDLDOJISTAR,
        '蜻蜓十字': talib.CDLDRAGONFLYDOJI,
        '吞噬模式': talib.CDLENGULFING,
        '十字暮星': talib.CDLEVENINGDOJISTAR,
        '暮星': talib.CDLEVENINGSTAR,
        '跳空并列阳线': talib.CDLGAPSIDESIDEWHITE,
        '墓碑十字': talib.CDLGRAVESTONEDOJI,
        '锤头': talib.CDLHAMMER,
        '上吊线': talib.CDLHANGINGMAN,
        '母子线': talib.CDLHARAMI,
        '十字孕线': talib.CDLHARAMICROSS,
        '风高浪大线': talib.CDLHIGHWAVE,
        '陷阱': talib.CDLHIKKAKE,
        '修正陷阱': talib.CDLHIKKAKEMOD,
        '家鸽': talib.CDLHOMINGPIGEON,
        '三胞胎乌鸦': talib.CDLIDENTICAL3CROWS,
        '颈内线': talib.CDLINNECK,
        '倒锤头': talib.CDLINVERTEDHAMMER,
        '反冲形态': talib.CDLKICKING,
        '长缺影反冲': talib.CDLKICKINGBYLENGTH,
        '梯底': talib.CDLLADDERBOTTOM,
        '长脚十字': talib.CDLLONGLEGGEDDOJI,
        '长蜡烛': talib.CDLLONGLINE,
        '光头光脚': talib.CDLMARUBOZU,
        '相同低价': talib.CDLMATCHINGLOW,
        '铺垫': talib.CDLMATHOLD,
        '十字晨星': talib.CDLMORNINGDOJISTAR,
        '晨星': talib.CDLMORNINGSTAR,
        '颈上线': talib.CDLONNECK,
        '刺透形态': talib.CDLPIERCING,
        '黄包车夫': talib.CDLRICKSHAWMAN,
        '上升下降三法': talib.CDLRISEFALL3METHODS,
        '分离线': talib.CDLSEPARATINGLINES,
        '射击之星': talib.CDLSHOOTINGSTAR,
        '短蜡烛': talib.CDLSHORTLINE,
        '纺锤': talib.CDLSPINNINGTOP,
        '停顿形态': talib.CDLSTALLEDPATTERN,
        '条形三明治': talib.CDLSTICKSANDWICH,
        '探水竿': talib.CDLTAKURI,
        '跳空并列阴阳线': talib.CDLTASUKIGAP,
        '插入': talib.CDLTHRUSTING,
        '三星': talib.CDLTRISTAR,
        '奇特三河床': talib.CDLUNIQUE3RIVER,
        '向上跳空两乌鸦': talib.CDLUPSIDEGAP2CROWS,
        '跳空三法': talib.CDLXSIDEGAP3METHODS
    }
    return pattern_funcs

def check_pattern(df, open_values, high_values, low_values, close_values):
    """识别K线形态
    
    Args:
        df: DataFrame对象
        open_values: 开盘价序列 
        high_values: 最高价序列
        low_values: 最低价序列
        close_values: 收盘价序列
        
    Returns:
        添加了形态识别结果的DataFrame
    """
    pattern_funcs = get_pattern()
    for pattern_name, pattern_func in pattern_funcs.items():
        df[pattern_name] = pattern_func(open_values, high_values, low_values, close_values)
    return df

    
# 检查股票收盘价是否高于55日均线,  而且低于10均线, 
# @param stock 股票代码
# @param data 股票日线数据
# @param end_date 结束日期
# @param ema_days 均线天数
def check_ea(stock, df, end_date=None, ema_days=20):
    # 数据量不足，返回False
    if df is None or len(df) < ema_days:
        logging.debug("{0}:样本小于{1}天...\n".format(stock, ema_days))
        return False

    # 过滤次新股
    if check_new(stock, df, end_date):
        return False

    # 计算移动平均线
    ema_tag = 'ema' + str(ema_days)
    #  20日指数移动平均线
    df[ema_tag] = talib.EMA(df['收盘'],ema_days)
    df['ma10'] = talib.MA(df['收盘'],10)

    
    # 如果结束日期小于当前日期, 则只取结束日期之前的数据
    if end_date is not None:
        if end_date <  datetime.now().strftime("%Y-%m-%d"):
            mask = (df['日期'] <= DateHelper.str_to_date(end_date).date())
            df = df.loc[mask]

    # 获取结束日期的收盘价和均线价格
    last_close = df.iloc[-1]['收盘']
    last_ema = df.iloc[-1][ema_tag]
    last_ma10 = df.iloc[-1]['ma10']
    # 判断收盘价是否大于20日均线, 且小于10日均线, 不满足则返回false
    if last_close < last_ema or last_close > last_ma10:
        return False

    # 获取最近20天数据
    recent_data = df.tail(20)  
    # 所有天的成交额都要大于3亿
    # volume_condition = ((recent_data['成交额']/ 100000000) >= 0.5).all()  
    # 所有天的换手率都要大于1%
    # turnover_condition = (recent_data['换手率'] >= 0.5).all()  
    # if not volume_condition or not turnover_condition:
    # return False

    # 计算20天内收盘价最高价格的那天
    # 找到最高价的那天
    max_price_idx = recent_data['收盘'].idxmax()
    # 获取最高价那天之后的数据
    recent_after_max_data = df.loc[max_price_idx:]
    # 判断高点回撤反弹
    recent_data_count = recent_after_max_data.shape[0]
    rsi_rebound = check_rsi_rebound(df,recent_data_count)
    rebound = check_rebound(recent_after_max_data)
    if rsi_rebound or rebound:
        return False
   
    # 收盘价条件:  55EMA < x < 55EMA * 1.05
    if last_close > last_ema * 1.05:
        return False
    # 判断缩量
    df['strategy'] = '周期4'
    print(f"周期4选中{df['股票代码'][0]}")
    logging.info(f"周期4选中{df['股票代码'][0]}")
    return True


# 方法2：通过RSI指标判断
def check_rsi_rebound(df,recent_data_count, period=6, threshold=5):
    """
    通过RSI指标判断是否有反弹
    period: RSI周期
    threshold: RSI反弹阈值
    """
    # 计算RSI
    df['rsi'] = talib.RSI(df['收盘'], timeperiod=period)
    # 获取最近的RSI值
    recent_rsi = df['rsi'].tail(recent_data_count)
    # 找到最小值及其位置
    rsi_min = recent_rsi.min()
    min_idx = recent_rsi.idxmin()  # 获取最小值的索引
    
    # 获取最小值之后的数据
    rsi_after_min = recent_rsi.loc[min_idx:]
    
    # 如果最小值在最后一天，直接返回False
    if min_idx == recent_rsi.index[-1]:
        return False
    
    # 计算反弹幅度
    rsi_rebound = rsi_after_min.max() - rsi_min
    
    # 判断是否反弹
    if rsi_rebound > threshold:
        return True
        
    return False

# 方法1：通过高点回撤判断
def check_rebound(data, threshold=0.05):
    """
    检查高点之后是否有反弹
    prices: 价格序列
    threshold: 反弹幅度阈值（默认5%）
    """
    prices = data['收盘'].values
    max_price = prices[0]  # 初始最高价
    min_after_max =  prices[0]  # 最高价后的最低价
    for price in  prices[1:]:
        if price > max_price:
            # 创新高，重置最低价
            max_price = price
            min_after_max = price
        else:
            # 更新最低价
            min_after_max = min(min_after_max, price)
            # 检查从最低点是否有超过threshold的反弹
            current_rebound = (price - min_after_max) / min_after_max
            if current_rebound > threshold:
                return True
    return False
    

# 量比大于3.0
def check_continuous_volume(code_name, data, end_date=None, threshold=60, window_size=3):
    stock = code_name[0]
    name = code_name[1]
    data['vol_ma5'] = pd.Series(talib.MA(data['成交量'].values, 5), index=data.index.values)
    if end_date is not None:
        mask = (data['日期'] <= end_date)
        data = data.loc[mask]
    data = data.tail(n=threshold + window_size)
    if len(data) < threshold + window_size:
        logging.debug("{0}:样本小于{1}天...\n".format(code_name, threshold+window_size))
        return False

    # 最后一天收盘价
    last_close = data.iloc[-1]['收盘']
    # 最后一天成交量
    last_vol = data.iloc[-1]['成交量']

    data_front = data.head(n=threshold)
    data_end = data.tail(n=window_size)

    mean_vol = data_front.iloc[-1]['vol_ma5']

    for index, row in data_end.iterrows():
        if float(row['成交量']) / mean_vol < 3.0:
            return False

    msg = "*{0} 量比：{1:.2f}\n\t收盘价：{2}\n".format(code_name, last_vol/mean_vol, last_close)
    logging.debug(msg)
    return True


# 收盘价高于N日均线
def check_ma(code_name, data, end_date=None, ma_days=250):
    if data is None or len(data) < ma_days:
        logging.debug("{0}:样本小于{1}天...\n".format(code_name, ma_days))
        return False

    ma_tag = 'ma' + str(ma_days)
    data[ma_tag] = pd.Series(talib.MA(data['收盘'].values, ma_days), index=data.index.values)

    if end_date is not None:
        mask = (data['日期'] <= end_date)
        data = data.loc[mask]

    last_close = data.iloc[-1]['收盘']
    last_ma = data.iloc[-1][ma_tag]
    if last_close > last_ma:
        return True
    else:
        return False


# 上市日小于60天
def check_new(code_name, data, end_date=None, threshold=60):
    size = len(data.index)
    if size < threshold:
        return True
    else:
        return False


# 量比大于2
# 例如：
#   2017-09-26 2019-02-11 京东方A
#   2019-03-22 浙江龙盛
#   2019-02-13 汇顶科技
#   2019-01-29 新城控股
#   2017-11-16 保利地产
def check_volume(code_name, data, end_date=None, threshold=60):
    if len(data) < threshold:
        logging.debug("{0}:样本小于250天...\n".format(code_name))
        return False
    data['vol_ma5'] = pd.Series(talib.MA(data['成交量'].values, 5), index=data.index.values)

    if end_date is not None:
        mask = (data['日期'] <= end_date)
        data = data.loc[mask]
    if data.empty:
        return False
    p_change = data.iloc[-1]['p_change']
    if p_change < 2 \
            or data.iloc[-1]['收盘'] < data.iloc[-1]['开盘']:
        return False
    data = data.tail(n=threshold + 1)
    if len(data) < threshold + 1:
        logging.debug("{0}:样本小于{1}天...\n".format(code_name, threshold))
        return False

    # 最后一天收盘价
    last_close = data.iloc[-1]['收盘']
    # 最后一天成交量
    last_vol = data.iloc[-1]['成交量']

    amount = last_close * last_vol * 100

    # ��交额不低于2亿
    if amount < 200000000:
        return False

    data = data.head(n=threshold)

    mean_vol = data.iloc[-1]['vol_ma5']

    vol_ratio = last_vol / mean_vol
    if vol_ratio >= 2:
        msg = "*{0}\n量比：{1:.2f}\t涨幅：{2}%\n".format(code_name, vol_ratio, p_change)
        logging.debug(msg)
        return True
    else:
        return False



# 检查股票是否突破指定区间内最高价
def check_breakthrough(code_name, data, end_date=None, threshold=30):
    # 初始化最高价为0
    max_price = 0
    
    # 如果指定了结束日期，只取该日期之前的数据
    if end_date is not None:
        mask = (data['日期'] <= end_date)
        data = data.loc[mask]
    
    # 取最后threshold+1天的数据
    data = data.tail(n=threshold+1)
    
    # 数据量不足，返回False
    if len(data) < threshold + 1:
        logging.debug("{0}:样本小于{1}天...\n".format(code_name, threshold))
        return False

    # 获取最后一天的收盘价和开盘价
    last_close = float(data.iloc[-1]['收盘'])  # iloc[-1]表示最后一行
    last_open = float(data.iloc[-1]['开盘'])

    # 获取倒数第二天的收盘价
    data = data.head(n=threshold)
    second_last_close = data.iloc[-1]['收盘']

    # 遍历数据找出最高价
    for index, row in data.iterrows():
        if row['收盘'] > max_price:
            max_price = float(row['收盘'])

    # 判断条件：
    # 1. 最后一天收盘价大于最高价
    # 2. 最高价大于倒数第二天收盘价
    # 3. 最高价大于最后一天开盘价
    # 4. 最后一天涨幅大于6%
    if last_close > max_price > second_last_close and max_price > last_open \
            and last_close / last_open > 1.06:
        return True
    else:
        return False
