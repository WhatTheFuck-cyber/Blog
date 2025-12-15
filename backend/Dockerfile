# 基础镜像：Python 3.9
FROM python:3.9-slim

# 设置工作目录
WORKDIR /app

# 复制依赖文件
COPY requirements.txt .
COPY .key/openssl.cnf .key/openssl.cnf

# 安装系统依赖（openssl）
RUN apt-get update && apt-get install -y openssl && rm -rf /var/lib/apt/lists/*

# 安装Python依赖
RUN pip install --no-cache-dir -r requirements.txt

# 生成密钥和证书
RUN mkdir -p .key && \
    openssl genrsa -out .key/key.pem 2048 && \
    openssl req -x509 -new -nodes \
      -key .key/key.pem \
      -sha256 -days 365 \
      -out .key/cert.pem \
      -subj "/C=CN/ST=Province/L=City/O=Organization/OU=Department/CN=localhost" \
      -config ".key/openssl.cnf"

# 复制项目文件
COPY . .

# 暴露端口
EXPOSE 8888

# 启动命令
CMD ["python", "main.py"]

# 构建镜像
# docker build -t my-python-app .
# 运行容器
# docker run -d -p 8888:8888 --name my-app my-python-app