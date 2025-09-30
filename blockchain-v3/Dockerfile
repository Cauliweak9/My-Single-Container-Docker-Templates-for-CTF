FROM ghcr.io/foundry-rs/foundry:latest AS foundry

COPY project /project

USER root
RUN true && \
    cd /project && \
    forge build --out /artifacts/out --cache-path /artifacts/cache && \
    true

# 第二阶段：集成所有组件
FROM python:3.11.6-slim

# 安装系统依赖
RUN apt-get update && apt-get install -y \
    curl git socat bsdmainutils libssl-dev ca-certificates \
    && rm -rf /var/lib/apt/lists/* \
    && pip config set global.index-url https://pypi.tuna.tsinghua.edu.cn/simple

# 安装Foundry
ENV FOUNDRY_DIR=/opt/foundry

ENV PATH=${FOUNDRY_DIR}/bin/:${PATH}

RUN true && \
    curl -L https://foundry.paradigm.xyz | bash && \
    foundryup && \
    true

# 安装huff
ENV HUFF_DIR=/opt/huff

ENV PATH=${HUFF_DIR}/bin/:${PATH}

RUN true && \
    curl -L http://get.huff.sh | bash && \
    huffup && \
    true

RUN pip install flask markdown web3 pymdown-extensions pygments

# 复制应用文件
COPY --from=foundry /artifacts /artifacts
COPY solc-static-linux /usr/bin/solc
COPY . /app
WORKDIR /app

# 配置环境变量
ENV FLASK_APP=app.py

# 暴露端口
EXPOSE 5000

ENTRYPOINT ["/bin/bash","/app/service/docker-entrypoint.sh"]
CMD [ "python", "/app/src/app.py" ]