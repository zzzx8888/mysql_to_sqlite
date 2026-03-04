#!/bin/bash
set -e  # 遇到错误立即退出

# 定义颜色输出（可选，提升交互体验）
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# 1. 检查是否安装git
if ! command -v git &> /dev/null; then
    echo -e "${RED}错误：未安装git，请先安装git后重试！${NC}"
    exit 1
fi

# 2. 拉取最新代码（如果是本地已克隆，先拉取；否则克隆仓库）
REPO_URL="https://github.com/zzzx8888/mysql_to_sqlite.git"  # 替换为实际仓库地址
PROJECT_DIR="mysql_to_sqlite"                             # 替换为项目本地目录名

if [ -d "$PROJECT_DIR" ]; then
    echo -e "${YELLOW}检测到已有项目目录，拉取最新代码...${NC}"
    cd "$PROJECT_DIR"
    git pull origin main  # 分支名如果不是main，替换为实际分支（如master）
else
    echo -e "${YELLOW}克隆仓库到本地...${NC}"
    git clone "$REPO_URL" "$PROJECT_DIR"
    cd "$PROJECT_DIR"
fi

# 3. 安装依赖（根据项目技术栈调整，以下示例覆盖Python/Node.js）
echo -e "${YELLOW}安装项目依赖...${NC}"
if [ -f "requirements.txt" ]; then
    # Python项目依赖安装
    if ! command -v pip3 &> /dev/null; then
        echo -e "${RED}错误：未安装pip3，请先安装Python和pip3！${NC}"
        exit 1
    fi
    pip3 install -r requirements.txt --user
elif [ -f "package.json" ]; then
    # Node.js项目依赖安装
    if ! command -v npm &> /dev/null; then
        echo -e "${RED}错误：未安装npm，请先安装Node.js！${NC}"
        exit 1
    fi
    npm install
else
    echo -e "${YELLOW}未检测到依赖文件（requirements.txt/package.json），跳过依赖安装${NC}"
fi

# 4. 运行项目（核心步骤，根据实际启动命令调整）
echo -e "${GREEN}启动项目...${NC}"
# 示例1：Python项目启动（替换为实际启动命令）
# python3 main.py
# 示例2：Node.js项目启动
# node app.js
# 示例3：Shell脚本启动
# ./run.sh

echo -e "${GREEN}项目部署运行成功！${NC}"
