@echo off
chcp 65001 > nul 2>&1  :: 强制设置编码为UTF-8，解决中文乱码问题
setlocal enabledelayedexpansion

:: ====================== 配置项（请根据实际情况修改）======================
set "REPO_URL=https://github.com/zzzx8888/mysql_to_sqlite.git"  :: 替换为GitHub仓库地址
set "PROJECT_DIR=mysql_to_sqlite"                             :: 替换为本地项目文件夹名
set "BRANCH=main"                                           :: 仓库分支名（如master）
:: 项目启动命令（根据技术栈修改，示例为Python/Node.js，择一保留/修改）
:: Python示例：set "START_CMD=python main.py"
:: Node.js示例：set "START_CMD=npm start"
set "START_CMD=python main.py"
:: =========================================================================

:: 1. 检查Git是否安装
where git > nul 2>&1
if %errorlevel% neq 0 (
    echo [错误] 未检测到Git，请先安装Git并配置到系统环境变量！
    echo 下载地址：https://git-scm.com/download/win
    pause
    exit /b 1
)

:: 2. 检测/克隆/拉取代码
echo [信息] 检查本地项目目录...
if exist "%PROJECT_DIR%" (
    echo [信息] 检测到已有项目目录，拉取最新代码...
    cd /d "%PROJECT_DIR%"
    git pull origin %BRANCH%
    if !errorlevel! neq 0 (
        echo [错误] 拉取代码失败，请检查网络或仓库权限！
        pause
        exit /b 1
    )
) else (
    echo [信息] 本地无项目目录，开始克隆仓库...
    git clone %REPO_URL% "%PROJECT_DIR%"
    if !errorlevel! neq 0 (
        echo [错误] 克隆仓库失败，请检查仓库地址或网络！
        pause
        exit /b 1
    )
    cd /d "%PROJECT_DIR%"
)

:: 3. 自动安装依赖（适配Python/Node.js，可根据技术栈删减）
echo [信息] 检查项目依赖...
:: 3.1 Python依赖（requirements.txt）
if exist "requirements.txt" (
    where pip3 > nul 2>&1
    if !errorlevel! neq 0 (
        echo [错误] 检测到requirements.txt，但未安装pip3！请先安装Python并配置环境变量。
        pause
        exit /b 1
    )
    echo [信息] 安装Python依赖...
    pip3 install -r requirements.txt
    if !errorlevel! neq 0 (
        echo [警告] Python依赖安装可能存在异常，建议检查网络或依赖包名称！
    )
)
:: 3.2 Node.js依赖（package.json）
if exist "package.json" (
    where npm > nul 2>&1
    if !errorlevel! neq 0 (
        echo [错误] 检测到package.json，但未安装npm！请先安装Node.js并配置环境变量。
        pause
        exit /b 1
    )
    echo [信息] 安装Node.js依赖...
    npm install
    if !errorlevel! neq 0 (
        echo [警告] Node.js依赖安装可能存在异常，建议切换npm源后重试！
    )
)

:: 4. 启动项目
echo [信息] 启动项目...
%START_CMD%

:: 5. 异常兜底
if !errorlevel! neq 0 (
    echo [错误] 项目启动失败，请检查启动命令或项目依赖！
    pause
    exit /b 1
)

echo [成功] 项目部署并启动完成！
pause
