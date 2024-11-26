import threading
import time
from db.sqlite_utils import init_db
import easyquant
from easyquant import DefaultLogHandler
from scheduler.task_scheduler import TaskScheduler
import settings
import utils
print('启动')

broker = None
need_data = None

log_type = 'file'

log_handler = DefaultLogHandler(name='主引擎', log_type=log_type, filepath='logs.log')
settings.init()
init_db()  # 初始化数据库

# 创建定时任务管理器
scheduler = None
def run_scheduler():
    scheduler = TaskScheduler(log_handler=log_handler)
    scheduler.start()  # 启动调度器
    log_handler.info("定时任务已启动")

# if __name__ == '__main__':

# 创建并启动调度器进程
scheduler_thread = threading.Thread(target=run_scheduler, daemon=True)
scheduler_thread.start()


    
# 初始化主引擎
m = easyquant.MainEngine(broker, # 券商
                        need_data, # 账号信息
                        quotation='online', # 行情
                        bar_type="1m", # 1分钟K线, 只有腾讯有
                        log_handler=log_handler)
m.is_watch_strategy = True  # 策略文件出现改动时,自动重载,不建议在生产环境下使用
m.load_strategy() # 加载策略



# 启动前准备
end_date = utils.DateHelper.get_end_date()
log_handler.info(f"选股回测日期: {end_date}")
print(f"选股回测日期: {end_date}")

try:
    m.start()  # 启动引擎
    while True:  # 无限循环
        time.sleep(1)  # 每秒检查一次
except (KeyboardInterrupt, SystemExit):
    print('主引擎退出', KeyboardInterrupt, SystemExit)
    # 停止调度器进程
    scheduler.stop()  # 强制终止调度器进程
    log_handler.info("定时任务已关闭")
    raise
finally:
    # 确保调度器进程在退出时被关闭
    log_handler.info("定时任务进程已停止")
