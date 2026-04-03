@echo off
chcp 65001 >nul
echo ====================================
echo 北理班车抢票助手 - 安卓版
echo ====================================
echo.

echo 请选择操作：
echo 1. 在电脑上测试运行
echo 2. 打包APK（需要Linux环境）
echo 3. 查看使用说明
echo 4. 退出
echo.

set /p choice="请输入选项 (1-4): "

if "%choice%"=="1" goto run
if "%choice%"=="2" goto build
if "%choice%"=="3" goto readme
if "%choice%"=="4" goto end
echo 无效选项，请重新运行脚本
pause
goto end

:run
echo.
echo 正在启动应用...
python app.py
pause
goto end

:build
echo.
echo ====================================
echo 打包APK说明
echo ====================================
echo.
echo 打包APK需要在Linux环境下进行，步骤如下：
echo.
echo 1. 在Linux系统上安装依赖：
echo    sudo apt-get install -y build-essential git python3 python3-dev python3-pip openjdk-8-jdk
echo    pip3 install --user --upgrade Cython virtualenv
echo    pip3 install --user buildozer
echo.
echo 2. 进入android目录：
echo    cd android
echo.
echo 3. 打包APK：
echo    buildozer -v android debug
echo.
echo 4. 生成的APK文件位于 bin/ 目录
echo.
pause
goto end

:readme
echo.
echo 正在打开使用说明...
start README.md
goto end

:end
echo.
echo 感谢使用！
pause
