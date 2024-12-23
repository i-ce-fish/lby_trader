import json
from datetime import datetime, timedelta
from typing import List

import pandas as pd
import uvicorn
from fastapi import Depends, FastAPI, HTTPException, Query, status, Path
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi import Body

from jose import jwt, JWTError
from starlette.responses import RedirectResponse

from db.db_class import WatchStock
from db.sqlite_utils import get_stock_info
from utils import beautify_time
from web.database import Database
from web.db_service import DbService
from web.dto import LoginRequest
from web.models import User
from web.settings import APISettings
from web.user_service import Token, route_data, UserService, oauth2_scheme, TokenData, UserModel

# fix mimetypes error, default .js is text/plain
import mimetypes

mimetypes.add_type("application/javascript; charset=utf-8", ".js")



SECRET_KEY = "09d25e094faa6ca2556c818166b7a9563b93f7099f6f0f4caa6cf63b88e8d3e7"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 3000

app = FastAPI()
settings = APISettings()
database = Database()
db_service = DbService(settings, database)
user_service = UserService(db_service)

origins = ["*"]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.mount("/static", StaticFiles(directory="static"), name="static")

# 返回定义fastapi返回的属性(数组)
def toList(data:List[dict]):
    result = []
    for item in data:
        result.append(item.__dict__)
    return result

# 返回定义fastapi返回的属性(对象)
def toDict(data:dict):
    return data.__dict__

async def get_current_user(token: str = Depends(oauth2_scheme)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
        token_data = TokenData(username=username)
    except JWTError:
        raise credentials_exception
    user = user_service.get_user(username=token_data.username)
    if user is None:
        raise credentials_exception
    return user


async def get_current_active_user(current_user: User = Depends(get_current_user)):
    return current_user


@app.get("/")
async def root():
    return RedirectResponse("/static/index.html")



@app.post("/api/login", response_model=Token)
async def login_for_access_token(login: LoginRequest):
    user = user_service.authenticate_user(login.username, login.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = user_service.create_access_token(
        data={"sub": user.username}, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}


@app.get("/api/me", response_model=UserModel)
async def read_users_me(current_user: User = Depends(get_current_active_user)):
    user = UserModel(
        email=current_user.email,
        full_name=current_user.full_name,
        roles=json.loads(current_user.roles),
        username=current_user.username,
        disabled=False)
    return user


@app.get("/api/route")
async def read_user_routes(current_user: User = Depends(get_current_active_user)):
    assert current_user is not None
    return route_data


@app.get("/api/getWatchStocks")
async def get_watch_stocks(watch_status: str = Query(default=None, description='监听状态')):
    stocks = db_service.get_watch_stocks(watch_status)
    now = datetime.now()
    for stock in stocks:
        end_time  = stock.end_time if stock.end_time else now
        end_time = pd.to_datetime(end_time).strftime('%Y%m%d')
        start_time = stock.start_time if stock.start_time else stock.create_time
        start_time = pd.to_datetime(start_time).strftime('%Y%m%d')
        list_daily_data = db_service.get_stock_daily_data(stock.code,start_time, end_time)
        if len(list_daily_data) > 0:
            stock.daily_data = pd.DataFrame(list_daily_data)
            #  百分比格式

            # 收盘涨幅 
            stock.daily_data['daily_change'] = (stock.daily_data['close'].pct_change().fillna(0) * 100 ).round(2)
            # 计算当日最高价相对前一日收盘价的涨幅
            stock.daily_data['max_daily_change'] = ((stock.daily_data['high'] - stock.daily_data['close'].shift(1)) / stock.daily_data['close'].shift(1) * 100).fillna(0).round(2)
            # 计算当日最低价相对前一日收盘价的涨幅
            stock.daily_data['min_daily_change'] = ((stock.daily_data['low'] - stock.daily_data['close'].shift(1)) / stock.daily_data['close'].shift(1) * 100).fillna(0).round(2)

            # 区间累计涨幅
            stock.total_return = (stock.daily_data['daily_change'].sum()).round(2)
            # 区间累计最大涨幅
            stock.max_total_return = (stock.daily_data['max_daily_change'].sum()).round(2)
            stock.daily_data = stock.daily_data[['trade_date','daily_change','max_daily_change','min_daily_change']].to_dict('records')
        stock.end_time = beautify_time(stock.end_time)
        stock.start_time = beautify_time(stock.start_time)
        stock.create_time = beautify_time(stock.create_time)
        stock.update_time = beautify_time(stock.update_time)
    return toList(stocks)

@app.post("/api/updateWatchStockStatus")
async def update_watch_stock_status(id: int = Body(...), status: str = Body(...)):
    return db_service.update_watch_stock_status(id, status)

@app.post("/api/addWatchStock")
async def add_watch_stock(code: str = Body(...),strategy: str = Body(default='活跃股')):
    # 是否已经存在监听中/停止监听的股票
    if db_service.get_watching_or_stopped_stock(code):
        return {"message": "已经存在监听中/停止监听的股票"}
    stock_info = get_stock_info(code)
    watch_stock = WatchStock(code=code, name=stock_info.name, current_price=stock_info.price, strategy=strategy, watch_status='监听中',create_time=datetime.now(), update_time=datetime.now())
    insert_result = db_service.add_watch_stock(watch_stock)
    return {"message": "添加成功" , "data": insert_result}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
