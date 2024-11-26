# 顶底图
from tdx.MyTT import ABS, IF, LLV, HHV, SMA, RD, MA, WINNER
import matplotlib.pyplot as plt
import numpy as np
plt.rcParams['font.sans-serif'] = ['Microsoft YaHei']

def ddt(data):
    """
    DDT指标实现
    参数说明：
    CLOSE: 收盘价序列
    HIGH: 最高价序列
    LOW: 最低价序列
    """
    LOW = data['low']
    HIGH = data['high']
    CLOSE = data['close']
    OPEN = data['open']
    # 接口数据没有成交额， VWAP估算
    data['amount'] = ((data['high'] + data['low'] + data['close']) / 3) * data['volume']
    
    VAR1 = 1
    VAR2 = np.where(WINNER(data, CLOSE) > 0, 
                1/WINNER(data, CLOSE), 
                0)  # 当WINNER为0时返回0
    VAR3 = MA(CLOSE,13)
    VAR4 = 100 - ABS((CLOSE - VAR3) / VAR3 * 100)
    VAR5 = LLV(LOW, 75)                    # 75日最低价
    VAR6 = HHV(HIGH, 75)                   # 75日最高价
    VAR7 = (VAR6 - VAR5) / 100            # 价格区间的1%
    VAR8 = SMA((CLOSE - VAR5) / VAR7, 20, 1)  # 20日移动平均
    VAR9 = SMA((OPEN - VAR5) / VAR7, 20, 1)  # 20日移动平均
    VARA = 3 * VAR8 - 2 * SMA(VAR8, 15, 1)    # 计算VARA
    VARB = 3 * VAR9 - 2 * SMA(VAR9, 15, 1)    # 计算VARB
    VARC = 100 - VARB    # 计算VARC
    DZ = (100 - VARA) * VAR1   
    SP = MA(WINNER(data,CLOSE * 0.95) * 100, 3) * VAR1
    QS = (100 - IF(VAR2 > 5, IF(VAR2 < 100, VAR2, VAR4 - 10), 0)) * VAR1
    
    data['dz']  = RD(DZ)
    data['sp']  = RD(SP)
    data['qs']  = RD(QS)
    return  data

# 基础绘图
def plot_basic(data, file_name="test.png"):
    """
    绘制两条线的基础图
    data: DataFrame，包含 'dz' 和 'sp' 列
    """
    plt.figure(figsize=(10, 6))  # 设置图形大小
    
    # 将时间索引转换为分类型
    x = np.arange(len(data))
    
    # 绘制两条线，使用数字索引而不是时间
    plt.plot(x, data['dz'], 'b-', label='DZ')
    plt.plot(x, data['sp'], 'r-', label='SP')
    
    # 设置x轴刻度和标签，只在有数据的点显示
    # plt.gca().set_xticks(x)
    # plt.gca().set_xticklabels(data.index, rotation=45)
    

    # 筛选整点时间的刻度
    hour_ticks = []
    hour_labels = []
    for i, time in enumerate(data.index):
        if time.minute == 0 or time.minute == 30:  # 只选择整点时间
            hour_ticks.append(i)
            hour_labels.append(time.strftime('%H:%M'))
    
    # 设置x轴刻度和标签
    plt.xticks(hour_ticks, hour_labels, rotation=45)
   


    # 设置y轴范围
    plt.ylim(-10, 120)  # y轴范围设置为0-100

    start_time = data.index[0].strftime('%Y-%m-%d %H:%M')
    end_time = data.index[-1].strftime('%Y-%m-%d %H:%M')

    # 设置标题和标签
    plt.title(file_name+f' {start_time} - {end_time}')
    plt.xlabel('time')
    plt.ylabel('index')
    
    plt.legend()  # 显示图例
    plt.grid(True)  # 显示网格
    
    # 保存图片
    plt.savefig('tdx/images/'+file_name)
    plt.close()  # 关闭图形

# 使用示例
# plot_basic_two_lines(data, 'dz_sp_compare.png')

