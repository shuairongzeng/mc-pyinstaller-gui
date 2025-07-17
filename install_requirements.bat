@echo off
REM 安装requirements.txt到虚拟环境的批处理脚本

echo ========================================
echo 安装 requirements.txt 到虚拟环境
echo ========================================

REM 检查虚拟环境是否存在
if not exist "%~dp0.conda\python.exe" (
    echo ✗ 错误: 虚拟环境不存在!
    echo 请先创建虚拟环境
    pause
    exit /b 1
)

REM 检查requirements.txt是否存在
if not exist "%~dp0requirements.txt" (
    echo ✗ 错误: requirements.txt 文件不存在!
    pause
    exit /b 1
)

echo ✓ 虚拟环境路径: %~dp0.conda
echo ✓ Python路径: %~dp0.conda\python.exe
echo ✓ requirements.txt 文件存在

echo.
echo 显示requirements.txt内容:
echo ----------------------------------------
type "%~dp0requirements.txt"
echo ----------------------------------------

echo.
echo 开始安装依赖...

REM 首先升级pip
echo.
echo 1. 升级pip...
"%~dp0.conda\python.exe" -m pip install --upgrade pip

REM 安装requirements.txt中的依赖
echo.
echo 2. 安装requirements.txt中的依赖...
"%~dp0.conda\python.exe" -m pip install -r requirements.txt

REM 检查安装结果
echo.
echo 3. 验证安装结果...
echo.
echo 检查PyQt5:
"%~dp0.conda\python.exe" -c "import PyQt5; print('PyQt5版本:', PyQt5.QtCore.QT_VERSION_STR)"

echo.
echo 检查PyInstaller:
"%~dp0.conda\python.exe" -c "import PyInstaller; print('PyInstaller版本:', PyInstaller.__version__)"

echo.
echo 检查Pillow:
"%~dp0.conda\python.exe" -c "import PIL; print('Pillow版本:', PIL.__version__)"

echo.
echo 检查importlib-metadata:
"%~dp0.conda\python.exe" -c "import importlib_metadata; print('importlib-metadata版本:', importlib_metadata.version('importlib-metadata'))"

echo.
echo 4. 显示所有已安装的包:
echo ----------------------------------------
"%~dp0.conda\python.exe" -m pip list
echo ----------------------------------------

echo.
echo ✓ requirements.txt 安装完成!
echo.
echo 提示: 如果要在其他终端中使用这个环境，请运行 activate_env.bat
pause
