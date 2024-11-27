# -*- encoding: UTF-8 -*-

import utils
import logging
import work_flow
import settings
from db.sqlite_utils import init_db
from scheduler.task_scheduler import TaskScheduler

import os
# 禁用 PyDev 调试器大变量提示
os.environ['PYDEVD_WARN_SLOW_RESOLVE_TIMEOUT'] = 'false'


logging.basicConfig(
    format='%(asctime)s %(message)s', 
    filename='log_select_stocks.log',
    encoding='utf-8'
)
logging.getLogger().setLevel(logging.INFO)

# 初始化配置
settings.init()
# 获取回测日期
end_date = utils.DateHelper.get_end_date()
logging.info(f"回测日期: {end_date}")
print(f"回测日期: {end_date}")
# 初始化数据库
init_db()
# 更新股票数据库 + 基金数据库, todo    定时任务

# 创建定时任务管理器
# scheduler = None
# if settings.config['cron']:
#     scheduler = TaskScheduler(logging)
#     scheduler.start()
# else:
print("不配置定时任务, 直接执行")
work_flow.update_listen_stocks()


# 保持主线程运行
# try:
#     while settings.config['cron']:
#         time.sleep(60)
# except (KeyboardInterrupt, SystemExit):
#     if scheduler:
#         scheduler.stop()