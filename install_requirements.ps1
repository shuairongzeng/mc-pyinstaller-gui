# PowerShell脚本：安装requirements.txt到虚拟环境
# 使用方法: .\install_requirements.ps1

Write-Host "========================================" -ForegroundColor Green
Write-Host " 安装 requirements.txt 到虚拟环境" -ForegroundColor Green  
Write-Host "========================================" -ForegroundColor Green

# 检查虚拟环境是否存在
$pythonPath = ".\.conda\python.exe"
if (-not (Test-Path $pythonPath)) {
    Write-Host "✗ 错误: 虚拟环境不存在!" -ForegroundColor Red
    Write-Host "请先创建虚拟环境" -ForegroundColor Yellow
    Read-Host "按回车键退出"
    exit 1
}

# 检查requirements.txt是否存在
if (-not (Test-Path "requirements.txt")) {
    Write-Host "✗ 错误: requirements.txt 文件不存在!" -ForegroundColor Red
    Read-Host "按回车键退出"
    exit 1
}

Write-Host "✓ 虚拟环境路径: $(Get-Location)\.conda" -ForegroundColor Green
Write-Host "✓ Python路径: $pythonPath" -ForegroundColor Green
Write-Host "✓ requirements.txt 文件存在" -ForegroundColor Green

Write-Host "`n显示requirements.txt内容:" -ForegroundColor Cyan
Write-Host "----------------------------------------" -ForegroundColor Gray
Get-Content "requirements.txt"
Write-Host "----------------------------------------" -ForegroundColor Gray

Write-Host "`n开始安装依赖..." -ForegroundColor Yellow

# 升级pip
Write-Host "`n1. 升级pip..." -ForegroundColor Cyan
& $pythonPath -m pip install --upgrade pip

# 安装requirements.txt中的依赖
Write-Host "`n2. 安装requirements.txt中的依赖..." -ForegroundColor Cyan
& $pythonPath -m pip install -r requirements.txt

# 验证安装结果
Write-Host "`n3. 验证安装结果..." -ForegroundColor Cyan

Write-Host "`n检查PyQt5:" -ForegroundColor Yellow
& $pythonPath -c "from PyQt5.QtCore import QT_VERSION_STR; print('PyQt5版本:', QT_VERSION_STR)"

Write-Host "`n检查PyInstaller:" -ForegroundColor Yellow  
& $pythonPath -c "import PyInstaller; print('PyInstaller版本:', PyInstaller.__version__)"

Write-Host "`n检查Pillow:" -ForegroundColor Yellow
& $pythonPath -c "import PIL; print('Pillow版本:', PIL.__version__)"

Write-Host "`n检查importlib-metadata:" -ForegroundColor Yellow
& $pythonPath -c "import importlib_metadata; print('importlib-metadata版本:', importlib_metadata.version('importlib-metadata'))"

Write-Host "`n4. 显示所有已安装的包:" -ForegroundColor Cyan
Write-Host "----------------------------------------" -ForegroundColor Gray
& $pythonPath -m pip list
Write-Host "----------------------------------------" -ForegroundColor Gray

Write-Host "`n✓ requirements.txt 安装完成!" -ForegroundColor Green
Write-Host "`n提示: 要使用虚拟环境，请运行: .\.conda\python.exe" -ForegroundColor Yellow
Write-Host "或者运行 activate_env.bat 来激活环境" -ForegroundColor Yellow

Read-Host "`n按回车键退出"
