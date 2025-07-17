@echo off
REM 安装项目依赖的批处理脚本

echo 正在安装项目依赖...
echo 使用环境: %~dp0.conda\python.exe

REM 升级pip
echo.
echo 升级pip...
"%~dp0.conda\python.exe" -m pip install --upgrade pip

REM 安装常用依赖
echo.
echo 安装基础依赖...
"%~dp0.conda\python.exe" -m pip install numpy pandas requests

REM 安装PyInstaller
echo.
echo 安装PyInstaller...
"%~dp0.conda\python.exe" -m pip install pyinstaller

REM 显示已安装的包
echo.
echo 已安装的包:
"%~dp0.conda\python.exe" -m pip list

echo.
echo 依赖安装完成!
pause
