#!/bin/bash

# 检查操作系统类型
if [[ "$OSTYPE" == "linux-gnu"* ]]; then
    # Linux系统
    echo "Running on Linux system..."
    
    # 检查是否存在screen
    if ! command -v screen &> /dev/null; then
        echo "Screen is not installed. Installing..."
        sudo apt-get update && sudo apt-get install screen -y
    fi
    
    # 使用screen启动web服务
    screen -dmS web python3 web_server.py
    echo "Web server started in screen session 'web'"
    
    # 使用screen启动交易程序
    screen -dmS trader python3 lby_trader_main.py
    echo "Trader started in screen session 'trader'"
    
    # 显示运行中的screen会话
    echo "Running screen sessions:"
    screen -ls
    
else
    # Windows系统
    echo "Running on Windows system..."
    
    # 启动web服务
    start  python web_server.py
    echo "Web server started"
    
    # 启动交易程序
    start  python lby_trader_main.py
    echo "Trader started"
fi

echo "All services started successfully!"