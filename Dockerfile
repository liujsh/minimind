FROM pytorch/pytorch:2.2.0-cuda11.8-cudnn8-runtime

# 安装系统依赖
RUN apt-get update && apt-get install -y --no-install-recommends \
    git curl wget build-essential ca-certificates && \
    rm -rf /var/lib/apt/lists/*

WORKDIR /workspace/minimind

# 复制项目文件（在构建镜像时请把代码放在上下文根）
COPY . /workspace/minimind

# 使用 pip 安装依赖（优先使用项目 requirements.txt）
RUN python -m pip install --upgrade pip setuptools wheel && \
    pip install -r requirements.txt

ENV LANG C.UTF-8

# 切换为非交互模式
ENV DEBIAN_FRONTEND=noninteractive

# 默认命令：启动 bash，用户可覆盖为训练命令
CMD ["/bin/bash"]
