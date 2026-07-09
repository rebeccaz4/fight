#!/bin/bash

# Fight应用启动脚本

echo "🗣️ 启动 Fight - 人机吵架决策系统"

# 检查Python环境
if ! command -v python &> /dev/null; then
    echo "错误: 未找到Python，请先安装Python 3.8+"
    exit 1
fi

# 检查虚拟环境
if [[ "$VIRTUAL_ENV" == "" ]]; then
    echo "警告: 未检测到虚拟环境，建议使用虚拟环境"
    echo "创建虚拟环境: python -m venv venv"
    echo "激活虚拟环境: source venv/bin/activate"
fi

# 检查环境变量文件
if [ ! -f ".env" ]; then
    echo "错误: 未找到.env文件"
    echo "请复制.env.example为.env并配置必要的环境变量"
    echo "cp .env.example .env"
    exit 1
fi

# 加载环境变量
export $(cat .env | grep -v '^#' | xargs)

# 检查必要的环境变量
if [ -z "$ANTHROPIC_API_KEY" ]; then
    echo "错误: 未设置ANTHROPIC_API_KEY环境变量"
    exit 1
fi

if [ -z "$AGENTS_MEMORY_DSN" ]; then
    echo "错误: 未设置AGENTS_MEMORY_DSN环境变量"
    exit 1
fi

if [ -z "$AGENTS_MEMORY_API_KEY" ]; then
    echo "错误: 未设置AGENTS_MEMORY_API_KEY环境变量"
    exit 1
fi

# 检查依赖
echo "检查依赖..."
python -c "
import sys
required = ['anthropic', 'sqlalchemy', 'rich', 'prompt_toolkit']
missing = []
for module in required:
    try:
        __import__(module)
    except ImportError:
        missing.append(module)
if missing:
    print(f'缺少依赖: {\", \".join(missing)}')
    print('请运行: pip install -r requirements.txt')
    sys.exit(1)
" || exit 1

echo "依赖检查通过，启动应用..."
echo ""

# 启动应用
python -m fight.cli