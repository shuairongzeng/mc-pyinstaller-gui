@echo off
REM 激活本地conda虚拟环境的批处理脚本

echo 正在激活虚拟环境...
echo 环境路径: %~dp0.conda

REM 设置环境变量
set CONDA_PREFIX=%~dp0.conda
set CONDA_DEFAULT_ENV=%~dp0.conda
set CONDA_PROMPT_MODIFIER=(.conda) 

REM 将虚拟环境的Scripts和根目录添加到PATH前面
set PATH=%~dp0.conda\Scripts;%~dp0.conda;%PATH%

REM 显示当前Python信息
echo.
echo ========================================
echo 虚拟环境已激活
echo ========================================
echo Python路径: %~dp0.conda\python.exe
echo 环境路径: %CONDA_PREFIX%
echo.

REM 验证Python版本
"%~dp0.conda\python.exe" --version
echo.

REM 启动新的命令行会话
cmd /k "echo 虚拟环境已激活。使用 'python' 命令将使用虚拟环境中的Python。"
