from collections import defaultdict
from datetime import datetime
from queue import Queue, Empty
from threading import Thread


class Event:
    """事件对象"""

    def __init__(self, event_type, data=None):
        self.event_type = event_type
        self.data = data


class EventEngine:
    """事件驱动引擎"""

    def __init__(self):
        """初始化事件引擎"""
        # 事件队列
        self.__queue = Queue()

        # 事件引擎开关
        self.__active = False

        # 事件引擎处理线程
        self.__thread = Thread(target=self.__run, name="EventEngine.__thread")

        # 事件字典，key 为时间， value 为对应监听事件函数的列表
        self.__handlers = defaultdict(list)

    def __run(self):
        """启动引擎"""
        while self.__active:
            try:
                event = self.__queue.get(block=True, timeout=1)
                handle_thread = Thread(target=self.__process, name="EventEngine.__process", args=(event,))
                handle_thread.start()
            except Empty:
                pass

    def __process(self, event):
        """事件处理"""
        # 检查该事件是否有对应的处理函数
        if event.event_type in self.__handlers:
            # 若存在,则按顺序将时间传递给处理函数执行
            for handler in self.__handlers[event.event_type]:
                handler(event)

    def start(self):
        """引擎启动"""
        self.__active = True
        self.__thread.start()

    def stop(self):
        """停止引擎"""
        self.__active = False
        self.__thread.join()

    def register(self, event_type, handler):
        """注册事件处理函数监听"""
        if handler not in self.__handlers[event_type]:
            self.__handlers[event_type].append(handler)
            # print(f"事件引擎：注册事件处理器 - 类型：{event_type}")

    def unregister(self, event_type, handler):
        """注销事件处理函数"""
        handler_list = self.__handlers.get(event_type)
        if handler_list is None:
            return
        if handler in handler_list:
            handler_list.remove(handler)
        if len(handler_list) == 0:
            self.__handlers.pop(event_type)

    def put(self, event):
        """放入事件"""
        print(f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S')} 事件引擎：添加新事件: {event.event_type}")  # 添加日志
        self.__queue.put(event)

    @property
    def queue_size(self):
        return self.__queue.qsize()
