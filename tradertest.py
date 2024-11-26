import easyquant
from easyquant import DefaultLogHandler
import settings

print('测试 DEMO')

# 东财
# broker = 'eastmoney'
broker = None

# 自己准备
# {
#     "user": "",
#     "password": ""#
# }
need_data = None

log_type = 'file'

log_handler = DefaultLogHandler(name='分时策略', log_type=log_type, filepath='logs.log')
settings.init()
# 初始化主引擎
m = easyquant.MainEngine(broker, # 券商
                         need_data, # 账号信息
                         quotation='online', # 行情
                         bar_type="1m", # 1分钟K线, 只有腾讯有
                         log_handler=log_handler)
m.is_watch_strategy = True  # 策略文件出现改动时,自动重载,不建议在生产环境下使用
m.load_strategy() # 加载策略
m.start() # 启动引擎
