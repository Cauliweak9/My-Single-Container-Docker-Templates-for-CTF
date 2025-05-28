FROM python:3.10.12-slim-bullseye

# apt更换镜像源，并更新软件包列表信息
RUN  sed -i s@/archive.ubuntu.com/@/mirrors.aliyun.com/@g /etc/apt/sources.list
RUN apt-get update 

RUN pip install pymodbus

# 部署程序
COPY ./server.py /app/server.py
COPY ./client.py /app/client.py
COPY ./init_script.sh /app/init_script.sh

CMD ["bash","/app/init_script.sh"]

EXPOSE 504