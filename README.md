# 项目名称
一个基于Python的mysql_to_sqlite工具
用于将mysql备份的sql转换为sqlite语法格式，并且附带导入sqlite数据库功能。

## 快速开始
### 环境要求
- Git（版本≥2.0）
- Python 3.8+ / Node.js 14+（根据你的项目技术栈调整）
- 操作系统：Linux/macOS（Windows需适配WSL或Git Bash）

### 一键部署运行
1. 克隆本仓库（可选，直接运行脚本也会自动克隆）：
   ```bash
   git clone https://github.com/zzzx8888/mysql_to_sqlite.git
   cd mysql_to_sqlite
2. 赋予部署脚本执行权限：
   ```bash
   chmod +x deploy.sh   
3. 运行一键部署脚本
   ```bash
   ./deploy.sh
### 脚本功能说明
deploy.sh 脚本会自动完成以下操作：
1.  检查 Git 是否安装（未安装则提示并退出）；
2.  检测本地是否已有项目目录：
3.  有则拉取最新代码；
4.  无则克隆仓库到本地；
5.  自动识别项目依赖文件（requirements.txt/package.json）并安装对应依赖；
6.  启动项目（核心逻辑）。
### 常见问题
1. 脚本执行权限不足
解决：执行 chmod +x deploy.sh 赋予权限后重试。
2. 依赖安装失败
Python 项目：确保 pip3 已安装，且网络可访问 PyPI；
Node.js 项目：确保 npm 已安装，可切换淘宝源 npm config set registry https://registry.npm.taobao.org/ 后重试。
3. 项目启动失败
检查：
项目启动命令是否在脚本中正确配置；
系统是否缺少项目运行的底层依赖（如数据库 / 端口占用等）。
