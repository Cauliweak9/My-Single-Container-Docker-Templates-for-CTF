#!/bin/bash


# 直接启动Modbus服务器（确保初始化脚本能连接）
python /app/server.py &

# 等待服务就绪
sleep 5

# 执行初始化
python /app/client.py

# 保持容器运行
wait