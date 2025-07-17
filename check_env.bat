@echo off
REM 检查虚拟环境状态的批处理脚本

echo ========================================
echo 虚拟环境状态检查
echo ========================================

echo.
echo 1. 检查虚拟环境是否存在...
if exist "%~dp0.conda\python.exe" (
    echo ✓ 虚拟环境存在
) else (
    echo ✗ 虚拟环境不存在
    goto :end
)

echo.
echo 2. 检查Python版本...
"%~dp0.conda\python.exe" --version

echo.
echo 3. 检查pip版本...
"%~dp0.conda\python.exe" -m pip --version

echo.
echo 4. 运行环境调试脚本...
"%~dp0.conda\python.exe" debug_environment.py

echo.
echo 5. 检查已安装的包...
"%~dp0.conda\python.exe" -m pip list

:end
echo.
echo 检查完成!
pause
