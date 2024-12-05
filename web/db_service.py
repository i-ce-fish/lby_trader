from typing import List

from db import sqlite_utils
from db.db_class import StockDailyData, WatchStock
from web.database import Database
from web.models import WatchStocks, User, Strategies
from web.settings import APISettings


class DbService:

    def __init__(self, config: APISettings, database: Database):
        self.config = config
        self.database = database

    def get_stock_daily_data(self, code: str, start_date: str, end_date: str = None) -> List[StockDailyData]:
        return sqlite_utils.get_stock_daily_data(code, start_date, end_date)

    def get_watching_or_stopped_stock(self, code: str) -> WatchStocks:
        return sqlite_utils.get_watching_or_stopped_stock(code)

    def get_watch_stocks(self,watching:str, user: str | None = None) -> List[WatchStock]:
        return sqlite_utils.get_watch_stocks(watching, user)

    def update_watch_stock_status(self, id: int, status: str) -> WatchStocks:
        if status == '监听中':
            res = sqlite_utils.start_watch_stock(id)
        elif status == '停止监听':
            res = sqlite_utils.stop_watch_stock(id)
        elif status == '结束监听':
            res = sqlite_utils.end_watch_stock(id)
        return res

    def add_watch_stock(self, watch_stock: WatchStock) -> WatchStocks:
        return sqlite_utils.add_watch_stock_by_user(watch_stock)   

    def watch_stock(self, code: str, name: str, close: float) -> WatchStocks:
        session = self.database.get_session()
        dbitem = session.query(WatchStocks).filter(WatchStocks.code == code).first()
        if not dbitem:
            dbitem = WatchStocks()
            dbitem.code = code
            dbitem.watch_price = close
            dbitem.name = name
            dbitem.close = close
            session.add(dbitem)
            session.commit()
        return dbitem

    def remove_stock(self, code):
        session = self.database.get_session()
        db_item = session.query(WatchStocks).filter(WatchStocks.code == code).first()
        if db_item:
            session.delete(db_item)
            session.commit()
        return db_item

    def get_user(self, username: str):
        session = self.database.get_session()
        return session.query(User).filter(User.username == username).first()

    def add_user(self, username: str, hashed_password: str):
        session = self.database.get_session()
        db_item = session.query(User).filter(User.username == username).first()
        if not db_item:
            db_item = User()
            db_item.username = username
            db_item.hashed_password = hashed_password
            db_item.full_name = username
            db_item.roles = '["admin"]'
            db_item.email = 'admin@example.com'
            session.add(db_item)
            session.commit()
        return db_item

    def list_strategies(self) -> List[Strategies]:
        session = self.database.get_session()
        return session.query(Strategies).all()

    def add_strategy(self, name: str, code: str):
        session = self.database.get_session()
        db_item = Strategies()
        db_item.name = name
        db_item.code = code
        session.add(db_item)
        session.commit()
        return db_item

    def update_strategy(self, id: int, name: str, code: str):
        session = self.database.get_session()
        db_item = session.query(Strategies).filter(Strategies.id == id).first()
        db_item.name = name
        db_item.code = code
        session.update(db_item)
        session.commit()
        return db_item
