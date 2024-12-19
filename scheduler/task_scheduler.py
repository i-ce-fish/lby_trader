# -*- encoding: UTF-8 -*-

import work_flow
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger

class TaskScheduler:
    def __init__(self, log_handler):
        self.scheduler = None
        self.init_scheduler()
        self.log = log_handler

    def init_scheduler(self):
        """初始化调度器"""
        if self.scheduler is None:
            self.scheduler = BackgroundScheduler()
    
    def update_listening_stocks_job(self):
        """更新监听股票的任务"""
        try:
            self.log.info("开始执行更新监听股票的任务")
            work_flow.update_listen_stocks()
            self.log.info("更新监听股票的任务执行完成")
        except Exception as e:
            print('定时任务执行失败:',e)
            self.log.error(f"定时任务执行失败: {e}", exc_info=True)

    def update_stocks_db_job(self):
        """更新股票数据库的任务"""
        try:
            self.log.info("开始执行更新数据库任务")
            work_flow.updateDb()
            self.log.info("更新数据库任务执行完成")
        except Exception as e:
            print('定时任务执行失败:',e)
            self.log.error(f"更新数据库任务执行失败: {e}", exc_info=True)

    def start(self):
        """启动定时任务"""
        # 每小时执行一次
        self.scheduler.add_job(
            self.update_listening_stocks_job,
            CronTrigger(
                day_of_week='mon-fri', 
                hour='9,10,12,13,14',
                minute='45,15,00,45,50'),           
            id='update_listening_stocks_job',
            max_instances=1,        # 最大实例数为1，防止任务重复执行
            coalesce=True          # 合并错过的任务
        )
        self.scheduler.add_job(
            self.update_stocks_db_job,
            CronTrigger(day='*/1'),  # 每1天执行
            id='update_stocks_db_job',
            max_instances=1,        # 最大实例数为1，防止任务重复执行
            coalesce=True          # 合并错过的任务
        )
        self.scheduler.start()
        self.log.info("定时任务已启动")

    def stop(self):
        """停止定时任务"""
        if self.scheduler:
            self.scheduler.shutdown()
            self.log.info("定时任务已关闭") 