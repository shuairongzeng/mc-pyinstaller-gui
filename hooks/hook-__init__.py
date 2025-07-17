"""
PyInstaller hook for this application
"""

hiddenimports = [
    # PyQt5 相关
    'PyQt5.sip',
    'sip',
    'PyQt5.QtCore',
    'PyQt5.QtGui',
    'PyQt5.QtWidgets',
    
    # 系统模块
    'platform',
    'subprocess',
    'shutil',
    'tempfile',
    'pathlib',
    'os.path',
    
    # 编码模块
    'encodings.utf_8',
    'encodings.cp1252',
    'encodings.ascii',
    'encodings.latin1',
    'encodings.gbk',
    
    # JSON和配置
    'json',
    'configparser',
    
    # 日志模块
    'logging.handlers',
    'logging.config',
    
    # 类型检查
    'typing_extensions',
    
    # 导入工具
    'importlib.util',
    'importlib.metadata',
    'pkg_resources',
    'setuptools',
    
    # 项目特定模块
    'config.app_config',
    'models.packer_model',
    'views.main_window',
    'controllers.main_controller',
    'services.package_service',
    'services.module_detector',
    'utils.logger',
    'utils.exceptions',
]

# 数据文件
datas = [
    ('config.json', '.'),
    ('icon.png', '.'),
    ('images', 'images'),
    ('templates', 'templates'),
]
