# PyInstaller GUI 依赖管理指南

## 📋 依赖文件说明

本项目提供了多个requirements文件，以满足不同使用场景的需求：

### 1. requirements.txt（标准安装）
- **用途**：日常使用的标准依赖
- **包含**：核心功能 + 必需依赖 + 基础增强功能
- **推荐**：大多数用户使用此文件

### 2. requirements-minimal.txt（最小安装）
- **用途**：仅包含运行应用程序的最基本依赖
- **包含**：PyQt5 + PyInstaller + 基础支持库
- **适用**：资源受限环境或快速部署

### 3. requirements-dev.txt（开发安装）
- **用途**：完整的开发环境依赖
- **包含**：所有功能 + 开发工具 + 测试框架 + 文档工具
- **适用**：开发者和贡献者

## 🚀 快速安装

### 方法一：使用安装脚本（推荐）
```bash
python install_dependencies.py
```

### 方法二：直接安装
```bash
# 标准安装（推荐）
pip install -r requirements.txt

# 最小安装
pip install -r requirements-minimal.txt

# 完整开发环境
pip install -r requirements-dev.txt
```

## 📦 核心依赖详解

### GUI框架
- **PyQt5 >= 5.15.0**
  - 应用程序的图形界面框架
  - 提供窗口、控件、事件处理等功能

### 打包工具
- **pyinstaller >= 5.13.0**
  - Python应用程序打包工具
  - 将Python脚本转换为可执行文件

### 支持库
- **importlib-metadata >= 4.0.0**
  - 模块导入和元数据处理
  - 用于动态模块检测功能

- **Pillow >= 8.0.0**
  - 图像处理库
  - 用于处理应用程序图标和界面图像

- **typing-extensions >= 4.0.0**
  - 类型注解支持
  - 提供更好的代码类型检查

## 🔧 可选依赖

### 网络功能
```bash
pip install requests urllib3 certifi
```

### 数据处理
```bash
pip install pandas numpy
```

### 图像处理增强
```bash
pip install opencv-python
```

### 科学计算
```bash
pip install scipy matplotlib scikit-learn
```

## 🖥️ 平台特定依赖

### Windows
- **pywin32 >= 306**
  - Windows API访问
  - 自动检测Windows平台并安装

### Linux/macOS
- 无特殊平台依赖
- 使用系统标准库

## 🐍 Python版本支持

- **最低要求**：Python 3.8+
- **推荐版本**：Python 3.9-3.11
- **测试版本**：Python 3.8, 3.9, 3.10, 3.11

## 🔍 依赖检查

### 检查已安装的包
```bash
pip list
```

### 检查特定包
```bash
pip show PyQt5
pip show pyinstaller
```

### 验证安装
```bash
python -c "import PyQt5; print('PyQt5 OK')"
python -c "import PyInstaller; print('PyInstaller OK')"
```

## 🛠️ 故障排除

### 常见问题

1. **PyQt5安装失败**
   ```bash
   # 尝试使用conda安装
   conda install pyqt
   
   # 或者安装预编译版本
   pip install PyQt5-Qt5
   ```

2. **pywin32安装失败（Windows）**
   ```bash
   # 手动安装
   pip install --upgrade pywin32
   
   # 或者使用conda
   conda install pywin32
   ```

3. **权限问题**
   ```bash
   # 使用用户安装
   pip install --user -r requirements.txt
   ```

4. **网络问题**
   ```bash
   # 使用国内镜像
   pip install -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple/
   ```

## 📈 版本更新

### 更新所有依赖
```bash
pip install --upgrade -r requirements.txt
```

### 更新特定包
```bash
pip install --upgrade PyQt5 pyinstaller
```

### 生成当前环境的requirements
```bash
pip freeze > current-requirements.txt
```

## 🤝 贡献指南

如果您要为项目贡献代码：

1. 安装开发环境：
   ```bash
   pip install -r requirements-dev.txt
   ```

2. 运行测试：
   ```bash
   pytest
   ```

3. 代码格式化：
   ```bash
   black .
   isort .
   ```

4. 代码检查：
   ```bash
   flake8 .
   pylint .
   ```

## 📞 获取帮助

如果遇到依赖安装问题：

1. 查看项目的Issue页面
2. 运行 `python install_dependencies.py` 获取交互式帮助
3. 检查Python和pip版本是否符合要求
4. 尝试在虚拟环境中安装
