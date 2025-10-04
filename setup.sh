#!/bin/bash

# 设置错误时退出
set -e

echo "=== FastAPI项目启动脚本 ==="

# 检查Python环境
if ! command -v python3 &> /dev/null; then
    echo "错误: 未找到Python3，请先安装Python3"
    exit 1
fi

# 检查虚拟环境
if [ ! -d "venv" ]; then
    echo "创建虚拟环境..."
    python3 -m venv venv
fi

# 激活虚拟环境
echo "激活虚拟环境..."
source venv/bin/activate

# 升级pip
echo "升级pip..."
pip install --upgrade pip

# 安装依赖
echo "安装项目依赖..."
pip install -r requirements.txt

# 检查.env文件
if [ ! -f ".env" ]; then
    echo "创建.env配置文件..."
    cp .env.example .env
    echo "请编辑.env文件配置您的环境变量"
fi

# 创建必要的目录
echo "创建必要目录..."
mkdir -p uploads logs migrations

# 数据库迁移
echo "执行数据库迁移..."
aerich init -t config.database.TORTOISE_ORM
aerich init-db

echo "=== 项目配置完成 ==="
echo ""
echo "启动开发服务器:"
echo "  python main.py"
echo ""
echo "或使用uvicorn:"
echo "  uvicorn main:app --reload --host 0.0.0.0 --port 8000"
echo ""
echo "启动Celery Worker:"
echo "  celery -A celery_app.celery worker --loglevel=info"
echo ""
echo "启动Celery Beat:"
echo "  celery -A celery_app.celery beat --loglevel=info"
echo ""
echo "启动Flower监控:"
echo "  celery -A celery_app.celery flower --port=5555"
echo ""
echo "Docker启动:"
echo "  docker-compose up -d"