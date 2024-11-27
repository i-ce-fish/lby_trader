import sqlite3
import logging
from datetime import datetime
from dataclasses import fields as dataclass_fields  # 重命名导入
from db.db_class import StockInfo, WatchingStock



class SqliteDB:
    def __enter__(self):
        """支持with语句"""
        self.connect()
        return self
        
    def __exit__(self, exc_type, exc_val, exc_tb):
        """支持with语句"""
        self.close()
        
    def __exit__(self, exc_type, exc_val, exc_tb):
        """支持with语句"""
        self.close()

    def __init__(self, db_file='stock.db'):
        """初始化数据库连接"""
        self.db_file = db_file
        self.conn = None
        self.cursor = None
        
    def connect(self):
        """连接数据库"""
        try:
            self.conn = sqlite3.connect(self.db_file)
            self.cursor = self.conn.cursor()
        except Exception as e:
            logging.error(f"连接数据库失败: {e}")
            
    def close(self):
        """关闭数据库连接"""
        if self.cursor:
            self.cursor.close()
        if self.conn:
            self.conn.close()
            
    def execute(self, sql, params=None):
        """执行SQL语句"""
        try:
            if params:
                self.cursor.execute(sql, params)
            else:
                self.cursor.execute(sql)
            # 立即提交事务
            self.conn.commit()
            # 返回受影响的行数
            return self.cursor.rowcount
        except Exception as e:
            logging.error(f"执行SQL失败: {sql}, 错误: {e}")
            self.conn.rollback()
            return 0
            
    def query_one(self, sql, params=None):
        """查询单条记录"""
        try:
            if params:
                self.cursor.execute(sql, params)
            else:
                self.cursor.execute(sql)
            return self.cursor.fetchone()
        except Exception as e:
            logging.error(f"查询失败: {sql}, 错误: {e}")
            return None
            
    def query_all(self, sql, params=None):
        """查询多条记录"""
        try:
            if params:
                self.cursor.execute(sql, params)
            else:
                self.cursor.execute(sql)
            return self.cursor.fetchall()
        except Exception as e:
            logging.error(f"查询失败: {sql}, 错误: {e}")
            return []

# 使用示例
def init_db():
    """初始化数据库表"""
    db_file = 'stock.db'
        
    logging.info("开始初始化数据库...")
    with SqliteDB() as db:
        # 创建股票基本信息表
        create_stocks_table = """
        CREATE TABLE IF NOT EXISTS stocks (
            code TEXT PRIMARY KEY,          -- 股票代码
            name TEXT,                      -- 股票名称
            price REAL,                     -- 当前价格
            change_pct REAL,                -- 涨跌幅
            float_shares REAL,              -- 流通股本(万股)
            total_shares REAL,              -- 总股本(万股)
            float_market_value REAL,        -- 流通市值(万元)
            total_market_value REAL,        -- 总市值(万元)
            pe_ratio REAL,                  -- 市盈率
            listing_date DATE,              -- 上市时间
            update_time TIMESTAMP           -- 更新时间
        )
        """
        
        # 创建交易记录表
        create_trades_table = """
        CREATE TABLE IF NOT EXISTS trades (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            code TEXT,                    -- 股票代码
            name TEXT,                    -- 股票名称
            current_price REAL,           -- 最新价格
            buy_price REAL,              -- 买入价格
            sell_price REAL,             -- 卖出价格
            quantity INTEGER,            -- 持有数量
            market_value REAL,           -- 持有市值
            status TEXT,                 -- 当前状态：持有/已卖出
            create_time TIMESTAMP,       -- 创建时间
            update_time TIMESTAMP        -- 更新时间
        )
        """

        # 创建股票监听
        create_watch_table = """
        CREATE TABLE IF NOT EXISTS stock_watch (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            code TEXT NOT NULL,           -- 股票代码
            name TEXT NOT NULL,           -- 股票名称
            current_price REAL,           -- 最新价格
            strategy TEXT NOT NULL,       -- 策略名称
            watch_status TEXT NOT NULL,   -- 监听状态：监听中/已停止/已触发
            create_time TIMESTAMP,        -- 创建时间
            update_time TIMESTAMP        -- 更新时间
        )
        """
        
        try:
            db.cursor.execute(create_stocks_table)
            db.cursor.execute(create_trades_table)
            db.cursor.execute(create_watch_table)
            db.conn.commit()
            logging.info("数据库初始化成功")
        except Exception as e:
            logging.error(f"初始化数据库失败: {e}")
            raise e


def save_stock_info(stock: StockInfo) -> bool:
    """
    保存或更新股票基本信息
    
    参数:
        stock: StockInfo对象，包含股票信息
    返回:
        bool: 是否保存成功
    """
    with SqliteDB() as db:
        # 构建SQL语句和参数
        fields = ['code', 'name', 'update_time']
        values = [stock.code, stock.name, datetime.now()]
        placeholders = ['?', '?', '?']
        
        # 动态添加非空字段
        optional_fields = {
            'price': stock.price,
            'change_pct': stock.change_pct,
            'float_shares': stock.float_shares,
            'total_shares': stock.total_shares,
            'float_market_value': stock.float_market_value,
            'total_market_value': stock.total_market_value,
            'pe_ratio': stock.pe_ratio,
            'listing_date': stock.listing_date
        }
        
        for field, value in optional_fields.items():
            if value is not None:
                fields.append(field)
                values.append(value)
                placeholders.append('?')
        
        # 构建SQL语句
        fields_str = ', '.join(fields)
        placeholders_str = ', '.join(placeholders)
        update_str = ', '.join(f"{field}=excluded.{field}" 
                             for field in fields if field != 'code')
        
        sql = f"""
        INSERT INTO stocks ({fields_str})
        VALUES ({placeholders_str})
        ON CONFLICT(code) DO UPDATE SET {update_str}
        """
        
        try:
            db.execute(sql, values)
            return True
        except Exception as e:
            logging.error(f"保存股票信息失败: {e}")
            return False
def update_stock_info(stock: StockInfo) -> bool:
    """
    更新股票信息
    
    参数:
        stock: StockInfo对象，包含要更新的股票信息
        
    返回:
        bool: 是否更新成功
        
    示例:
        stock = StockInfo(
            code='000001',
            name='平安银行',
            price=10.5,
            change_pct=2.5
        )
        update_stock_info(stock)
    """
    with SqliteDB() as db:
        # 检查股票是否存在
        check_sql = "SELECT code FROM stocks WHERE code = ?"
        if not db.query_one(check_sql, (stock.code,)):
            logging.error(f"股票代码不存在: {stock.code}")
            return False
            
        # 构建更新字段
        update_fields = []
        values = []
        
        # 所有可更新字段
        fields_map = {
            'name': stock.name,
            'price': stock.price,
            'change_pct': stock.change_pct,
            'float_shares': stock.float_shares,
            'total_shares': stock.total_shares,
            'float_market_value': stock.float_market_value,
            'total_market_value': stock.total_market_value,
            'pe_ratio': stock.pe_ratio,
            'listing_date': stock.listing_date
        }
        
        # 添加非空字段到更新列表
        for field, value in fields_map.items():
            if value is not None:
                update_fields.append(f"{field} = ?")
                values.append(value)
                
        if not update_fields:
            logging.warning("没有有效的更新字段")
            return False
            
        # 添加更新时间
        update_fields.append("update_time = ?")
        values.append(datetime.now())
        
        # 添加WHERE条件的值
        values.append(stock.code)
        
        # 构建SQL语句
        sql = f"""
        UPDATE stocks 
        SET {', '.join(update_fields)}
        WHERE code = ?
        """
        
        try:
            rows = db.execute(sql, values)
            if rows == 0:
                logging.warning(f"没有记录被更新: {stock.code}")
                return False
            return True
        except Exception as e:
            logging.error(f"更新股f票信息失败: {e}")
            return False        

def get_stock_info(code):
    with SqliteDB() as db:
        # 查询数据
        sql = "SELECT * FROM stocks WHERE code = ?"
        result = db.query_one(sql, (code,))
        
        if result:
            # 获取 StockInfo 类的字段名
            field_names = [field.name for field in dataclass_fields(StockInfo)]
            # 将查询结果转换为字典
            result_dict = dict(zip(field_names, result))
            return StockInfo(**result_dict)  # 使用字典解包创建StockInfo对象
        return None

def get_stock_info_by_name(name):
    with SqliteDB() as db:
        sql = "SELECT * FROM stocks WHERE name = ?"
        return db.query_one(sql, (name,))

def get_all_stocks():
    with SqliteDB() as db:
        sql = "SELECT * FROM stocks"
        return db.query_all(sql)
    



# 交易记录相关的操作函数
def add_trade(code, name, current_price, buy_price, quantity):
    """添加新的交易记录"""
    with SqliteDB() as db:
        data = {
            'code': code,
            'name': name,
            'current_price': current_price,
            'buy_price': buy_price,
            'sell_price': 0,
            'quantity': quantity,
            'market_value': current_price * quantity,
            'status': '持有',
            'create_time': datetime.now(),
            'update_time': datetime.now()
        }
        return db.insert('trades', data)

def update_trade_price(trade_id, current_price):
    """更新交易记录的最新价格和市值"""
    with SqliteDB() as db:
        # 先获取当前记录
        result = db.select('trades', condition={'id': trade_id})
        if not result:
            return False
            
        trade = result[0]
        quantity = trade[6]  # 持有数量在第7列
        
        update_data = {
            'current_price': current_price,
            'market_value': current_price * quantity,
            'update_time': datetime.now()
        }
        return db.update('trades', update_data, {'id': trade_id})

def close_trade(trade_id, sell_price):
    """结束交易（卖出）"""
    with SqliteDB() as db:
        update_data = {
            'sell_price': sell_price,
            'status': '已卖出',
            'update_time': datetime.now()
        }
        return db.update('trades', update_data, {'id': trade_id})

def get_active_trades():
    """获取所有持有中的交易"""
    with SqliteDB() as db:
        return db.select('trades', condition={'status': '持有'})

def get_trade_history(code=None):
    """获取交易历史"""
    with SqliteDB() as db:
        if code:
            return db.select('trades', condition={'code': code})
        return db.select('trades')





# 股票监听相关的操作函数
def add_watch_stock(code, name, current_price, strategy):
    """
    添加股票监听
    如果已存在"监听中"的记录则不能添加
    如果之前的记录是"已触发"状态则可以添加新的监听
    """
    with SqliteDB() as db:
        try:
            # 检查是否存在"监听中"的记录
            check_sql = """
            SELECT * FROM stock_watch 
            WHERE code = ? AND strategy = ? AND watch_status = '监听中'
            """
            existing = db.query_one(check_sql, (code, strategy))
            
            if existing:
                logging.warning(f"股票{code}的{strategy}策略已在监听中")
                return False
            
            # 添加新记录
            sql = """
            INSERT INTO stock_watch 
            (code, name, current_price, strategy, watch_status, create_time, update_time)
            VALUES (?, ?, ?, ?, ?, ?, ?)
            """
            now = datetime.now()
            params = (code, name, current_price, strategy, '监听中', now, now)
            db.execute(sql, params)
            logging.info(f"添加股票监听: {code} {name} - {strategy}")
            return True
            
        except Exception as e:
            logging.error(f"添加股票监听失败: {e}")
            return False

def update_watch_status(code, strategy, status, current_price=None):
    """
    更新股票监听状态
    :param code: 股票代码
    :param strategy: 策略名称
    :param status: 新状态
    :param current_price: 最新价格（可选）
    :return: 是否更新成功
    """
    with SqliteDB() as db:
        try:
            if current_price is not None:
                sql = """
                UPDATE stock_watch 
                SET watch_status = ?, current_price = ?, update_time = ?
                WHERE code = ? AND strategy = ?
                """
                params = (status, current_price, datetime.now(), code, strategy)
            else:
                sql = """
                UPDATE stock_watch 
                SET watch_status = ?, update_time = ?
                WHERE code = ? AND strategy = ?
                """
                params = (status, datetime.now(), code, strategy)
                
            rows_affected = db.execute(sql, params)
            
            if rows_affected == 0:
                logging.warning(f"没有找到要更新的记录: {code} - {strategy}")
                return False
               
            logging.info(f"更新股票监听状态: {code} - {strategy} -> {status}")
            return True
        except Exception as e:
            logging.error(f"更新股票监听状态失败: {e}")
            return False

def get_watching_stocks(strategy=None):
    """
    获取监听中的股票列表
    :param strategy: 策略名称（可选）
    :return: 监听中的股票列表
    """
    with SqliteDB() as db:
        try:
            if strategy:
                sql = """
                SELECT * FROM stock_watch 
                WHERE watch_status = '监听中' AND strategy = ?
                ORDER BY code
                """
                return db.query_all(sql, (strategy,))
            else:
                sql = """
                SELECT * FROM stock_watch 
                WHERE watch_status = '监听中'
                ORDER BY code
                """
                results =  db.query_all(sql)
            # 将查询结果转换为WatchingStock对象列表
            watching_stocks = []
            for row in results:
                watching_stock = WatchingStock(
                    id=row[0],
                    code=row[1],
                    name=row[2],
                    current_price=row[3],
                    strategy=row[4],
                    watch_status=row[5],
                    create_time=datetime.fromisoformat(row[6]) if row[6] else None,
                    update_time=datetime.fromisoformat(row[7]) if row[7] else None
                )
                watching_stocks.append(watching_stock)
            return watching_stocks            
        except Exception as e:
            logging.error(f"获取监听股票列表失败: {e}")
            return []

def get_watch_history(code=None, strategy=None):
    """
    获取股票监听历史
    :param code: 股票代码（可选）
    :param strategy: 策略名称（可选）
    :return: 监听历史记录
    """
    with SqliteDB() as db:
        try:
            if code and strategy:
                sql = "SELECT * FROM stock_watch WHERE code = ? AND strategy = ?"
                return db.query_all(sql, (code, strategy))
            elif code:
                sql = "SELECT * FROM stock_watch WHERE code = ?"
                return db.query_all(sql, (code,))
            elif strategy:
                sql = "SELECT * FROM stock_watch WHERE strategy = ?"
                return db.query_all(sql, (strategy,))
            else:
                sql = "SELECT * FROM stock_watch ORDER BY update_time DESC"
                return db.query_all(sql)
        except Exception as e:
            logging.error(f"获取监听历史失败: {e}")
            return []
          
if __name__ == "__main__":
     with SqliteDB() as db:
        # 删除id大于26的记录
        db.execute("DELETE FROM stock_watch WHERE id > 26")
         
    # with SqliteDB() as db:
    #     # 删除旧表
    #     drop_tables = [
    #         "DROP TABLE IF EXISTS stock_watch"
    #     ]
    #     for sql in drop_tables:
    #         db.execute(sql)

    #     # 创建股票监听表
    #     create_watch_table = """
    #     CREATE TABLE IF NOT EXISTS stock_watch (
    #         id INTEGER PRIMARY KEY AUTOINCREMENT,
    #         code TEXT NOT NULL,           -- 股票代码
    #         name TEXT NOT NULL,           -- 股票名称
    #         current_price REAL,           -- 最新价格
    #         strategy TEXT NOT NULL,       -- 策略名称
    #         watch_status TEXT NOT NULL,   -- 监听状态：监听中/已停止/已触发
    #         create_time TIMESTAMP,        -- 创建时间
    #         update_time TIMESTAMP        -- 更新时间
    #     )
    #     """
    #     db.cursor.execute(create_watch_table)
    #     db.conn.commit()
        
    # add_watch_stock('000001', '平安银行', 10.5, '测试策略')
    # update_watch_status('000001', '测试策略', '已触发', 11.0)
    # # 添加股票监听
    # add_watch_stock('000001', '平安银行', 10.5, '测试策略')
    # # 更新监听状态

    # # 获取所有监听中的股票
    # watching_stocks = get_watching_stocks()

    # # 获取监听历史
    # print(watching_stocks)

