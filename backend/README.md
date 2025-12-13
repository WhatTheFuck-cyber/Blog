# 博客后端

## 基于 FastAPI 开发

### 1. 项目结构

```plaintext
backend
├── README.md
├── requirements.txt
├── .gitignore
├── imports.py
├── main.py
├── .key
│   ├── openssl.cnf
│   ├── cert.pem            # 自行生成，仅供测试
│   └── key.pem             # 自行生成，仅供测试
├── app
│   ├── __init__.py
│   ├── database.py
│   ├── auth.py
│   ├── utils.py
│   ├── models
│   │   ├── __init__.py
|   │   ├── articles.py
│   │   ├── base.py
│   │   ├── categories.py
│   │   ├── comments.py
│   │   ├── interactions.py
│   │   ├── messages.py
│   │   ├── tokens.py
│   │   └── users.py
│   ├── routes
│   │   ├── __init__.py
│   │   ├── articles.py
│   │   ├── categories.py
│   │   ├── comments.py
│   │   ├── home.py
│   │   ├── interactions.py
│   │   ├── messages.py
│   │   ├── search.py
│   │   └── users.py
│   ├── schemas
│   │   ├── __init__.py
│   │   ├── articles.py
│   │   ├── categories.py
│   │   ├── comments.py
│   │   ├── home.py
│   │   ├── interactions.py
│   │   ├── messages.py
│   │   ├── minimal.py
│   │   ├── token.py
│   │   └── users.py
...... (可接续开发)
```

### 2. 启动项目

1. 安装依赖
```bash
pip install -r requirements.txt
conda install -c conda-forge openssl -y
```

2. 密钥与证书生成
```bash
cd /path/to/backend
mkdir .key
openssl genrsa -out .key/key.pem 2048
                        # 1. 生成私钥
openssl req -x509 -new -nodes -key .key/key.pem -sha256 -days 365 -out .key/cert.pem -subj "/C=CN/ST=Province/L=City/O=Organization/OU=Department/CN=localhost" -config "D:\_Compiler\Anaconda\envs\blog\Library\ssl\openssl.cnf"
                        # 2. 生成自签名证书
```

3. 项目后端启动
```bash
python main.py
```

4. FastAPI 的交互测试路径
```bash
https://localhost:8888/docs
```

5. FastAPI 的 API 文档路径
```bash
https://localhost:8888/redoc
```