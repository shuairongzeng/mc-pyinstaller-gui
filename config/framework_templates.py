"""
框架配置模板
定义各种Python框架的打包配置模板
"""
from typing import Dict, List, Any

class FrameworkTemplates:
    """框架配置模板管理器"""
    
    @staticmethod
    def get_all_templates() -> Dict[str, Dict[str, Any]]:
        """获取所有框架模板"""
        return {
            'django': FrameworkTemplates.get_django_template(),
            'flask': FrameworkTemplates.get_flask_template(),
            'fastapi': FrameworkTemplates.get_fastapi_template(),
            'opencv': FrameworkTemplates.get_opencv_template(),
            'matplotlib': FrameworkTemplates.get_matplotlib_template(),
            'numpy': FrameworkTemplates.get_numpy_template(),
            'pandas': FrameworkTemplates.get_pandas_template(),
            'tensorflow': FrameworkTemplates.get_tensorflow_template(),
            'pytorch': FrameworkTemplates.get_pytorch_template(),
            'scikit_learn': FrameworkTemplates.get_sklearn_template(),
            'pyqt5': FrameworkTemplates.get_pyqt5_template(),
            'pyqt6': FrameworkTemplates.get_pyqt6_template(),
            'tkinter': FrameworkTemplates.get_tkinter_template(),
            'requests': FrameworkTemplates.get_requests_template(),
            'selenium': FrameworkTemplates.get_selenium_template(),
            'pillow': FrameworkTemplates.get_pillow_template(),
        }
    
    @staticmethod
    def get_django_template() -> Dict[str, Any]:
        """Django框架配置模板"""
        return {
            'name': 'Django',
            'description': 'Django Web框架',
            'indicators': ['django', 'django.core', 'django.conf', 'django.urls'],
            'hidden_imports': [
                'django.core.management',
                'django.core.management.commands',
                'django.contrib.auth',
                'django.contrib.contenttypes',
                'django.contrib.sessions',
                'django.contrib.messages',
                'django.contrib.staticfiles',
                'django.contrib.admin',
                'django.db.backends.sqlite3',
                'django.template.loaders.filesystem',
                'django.template.loaders.app_directories',
            ],
            'collect_all': ['django'],
            'collect_data': ['django'],
            'data_files': [
                'templates',
                'static',
                'locale',
                'media',
                'staticfiles'
            ],
            'exclude_modules': [],
            'additional_args': [
                '--collect-all=django',
                '--collect-data=django'
            ],
            'recommendations': [
                '建议使用 --collect-all django',
                '确保包含模板和静态文件目录',
                '检查数据库配置文件',
                '可能需要包含locale文件夹'
            ],
            'common_issues': [
                '模板文件未找到：使用 --add-data 包含templates目录',
                '静态文件缺失：使用 --add-data 包含static目录',
                '数据库连接问题：检查数据库配置'
            ]
        }
    
    @staticmethod
    def get_flask_template() -> Dict[str, Any]:
        """Flask框架配置模板"""
        return {
            'name': 'Flask',
            'description': 'Flask Web框架',
            'indicators': ['flask', 'flask.app', 'Flask'],
            'hidden_imports': [
                'flask.json',
                'flask.logging',
                'jinja2.ext',
                'werkzeug.serving',
                'werkzeug.middleware',
                'werkzeug.middleware.proxy_fix',
                'click',
                'itsdangerous'
            ],
            'collect_all': ['flask', 'jinja2', 'werkzeug'],
            'collect_data': ['flask'],
            'data_files': ['templates', 'static'],
            'additional_args': [
                '--collect-all=flask',
                '--collect-all=jinja2'
            ],
            'recommendations': [
                '建议使用 --collect-all flask',
                '包含模板和静态文件目录',
                '检查Jinja2模板配置'
            ]
        }
    
    @staticmethod
    def get_fastapi_template() -> Dict[str, Any]:
        """FastAPI框架配置模板"""
        return {
            'name': 'FastAPI',
            'description': 'FastAPI Web框架',
            'indicators': ['fastapi', 'FastAPI'],
            'hidden_imports': [
                'uvicorn',
                'uvicorn.main',
                'uvicorn.config',
                'starlette',
                'pydantic',
                'pydantic.validators',
                'pydantic.typing'
            ],
            'collect_all': ['fastapi', 'uvicorn', 'starlette', 'pydantic'],
            'recommendations': [
                '建议使用 --collect-all fastapi',
                '包含uvicorn服务器',
                '检查pydantic模型定义'
            ]
        }
    
    @staticmethod
    def get_opencv_template() -> Dict[str, Any]:
        """OpenCV配置模板"""
        return {
            'name': 'OpenCV',
            'description': 'OpenCV计算机视觉库',
            'indicators': ['cv2', 'opencv'],
            'hidden_imports': [
                'numpy.core._multiarray_umath',
                'numpy.core._multiarray_tests',
                'numpy.linalg._umath_linalg',
                'numpy.fft._pocketfft_internal'
            ],
            'collect_all': ['cv2', 'numpy'],
            'collect_binaries': ['cv2'],
            'additional_args': [
                '--collect-all=cv2',
                '--collect-binaries=cv2'
            ],
            'recommendations': [
                '建议使用 --collect-all cv2',
                '可能需要额外的DLL文件',
                '确保numpy版本兼容'
            ]
        }
    
    @staticmethod
    def get_matplotlib_template() -> Dict[str, Any]:
        """Matplotlib配置模板"""
        return {
            'name': 'Matplotlib',
            'description': 'Matplotlib绘图库',
            'indicators': ['matplotlib', 'matplotlib.pyplot', 'plt'],
            'hidden_imports': [
                'matplotlib.backends.backend_tkagg',
                'matplotlib.backends.backend_qt5agg',
                'matplotlib.backends.backend_agg',
                'matplotlib.figure',
                'matplotlib.font_manager',
                'matplotlib._path',
                'matplotlib.ft2font'
            ],
            'collect_all': ['matplotlib'],
            'collect_data': ['matplotlib'],
            'data_files': ['matplotlib/mpl-data'],
            'additional_args': [
                '--collect-all=matplotlib',
                '--collect-data=matplotlib'
            ],
            'recommendations': [
                '建议使用 --collect-all matplotlib',
                '包含字体和配置文件',
                '可能需要指定后端'
            ]
        }
    
    @staticmethod
    def get_numpy_template() -> Dict[str, Any]:
        """NumPy配置模板"""
        return {
            'name': 'NumPy',
            'description': 'NumPy科学计算库',
            'indicators': ['numpy', 'np'],
            'hidden_imports': [
                'numpy.core._multiarray_umath',
                'numpy.core._multiarray_tests',
                'numpy.linalg._umath_linalg',
                'numpy.fft._pocketfft_internal',
                'numpy.random._common',
                'numpy.random.bit_generator',
                'numpy.random._bounded_integers',
                'numpy.random._mt19937',
                'numpy.random.mtrand'
            ],
            'collect_all': ['numpy'],
            'additional_args': ['--collect-all=numpy'],
            'recommendations': [
                '建议使用 --collect-all numpy',
                '科学计算库，建议增加内存限制',
                '确保所有数学函数可用'
            ]
        }
    
    @staticmethod
    def get_pandas_template() -> Dict[str, Any]:
        """Pandas配置模板"""
        return {
            'name': 'Pandas',
            'description': 'Pandas数据分析库',
            'indicators': ['pandas', 'pd'],
            'hidden_imports': [
                'pandas._libs.tslibs.timedeltas',
                'pandas._libs.tslibs.np_datetime',
                'pandas._libs.tslibs.nattype',
                'pandas._libs.tslibs.timestamps',
                'pandas._libs.properties',
                'pandas.io.formats.style'
            ],
            'collect_all': ['pandas'],
            'additional_args': ['--collect-all=pandas'],
            'recommendations': [
                '建议使用 --collect-all pandas',
                '数据分析库，建议增加内存限制',
                '确保包含所有IO模块'
            ]
        }
    
    @staticmethod
    def get_tensorflow_template() -> Dict[str, Any]:
        """TensorFlow配置模板"""
        return {
            'name': 'TensorFlow',
            'description': 'TensorFlow机器学习库',
            'indicators': ['tensorflow', 'tf'],
            'hidden_imports': [
                'tensorflow.python',
                'tensorflow.python.platform',
                'tensorflow.python.ops'
            ],
            'collect_all': ['tensorflow'],
            'recommendations': [
                '建议使用 --collect-all tensorflow',
                '机器学习库，需要大量内存',
                '可能与tensorflow-gpu冲突'
            ]
        }
    
    @staticmethod
    def get_pytorch_template() -> Dict[str, Any]:
        """PyTorch配置模板"""
        return {
            'name': 'PyTorch',
            'description': 'PyTorch机器学习库',
            'indicators': ['torch', 'torchvision', 'pytorch'],
            'hidden_imports': [
                'torch._C',
                'torch.nn',
                'torch.optim'
            ],
            'collect_all': ['torch', 'torchvision'],
            'recommendations': [
                '建议使用 --collect-all torch',
                '机器学习库，需要大量内存',
                '确保CUDA版本兼容（如果使用GPU）'
            ]
        }
    
    @staticmethod
    def get_sklearn_template() -> Dict[str, Any]:
        """Scikit-learn配置模板"""
        return {
            'name': 'Scikit-learn',
            'description': 'Scikit-learn机器学习库',
            'indicators': ['sklearn', 'scikit-learn'],
            'hidden_imports': [
                'sklearn.utils._cython_blas',
                'sklearn.neighbors.typedefs',
                'sklearn.neighbors.quad_tree',
                'sklearn.tree._utils'
            ],
            'collect_all': ['sklearn'],
            'recommendations': [
                '建议使用 --collect-all sklearn',
                '机器学习库，包含大量C扩展',
                '确保包含所有算法模块'
            ]
        }
    
    @staticmethod
    def get_pyqt5_template() -> Dict[str, Any]:
        """PyQt5配置模板"""
        return {
            'name': 'PyQt5',
            'description': 'PyQt5 GUI框架',
            'indicators': ['PyQt5', 'PyQt5.QtWidgets', 'PyQt5.QtCore'],
            'hidden_imports': [
                'PyQt5.sip',
                'sip',
                'PyQt5.QtCore',
                'PyQt5.QtGui',
                'PyQt5.QtWidgets',
                'PyQt5.QtNetwork',
                'PyQt5.QtMultimedia'
            ],
            'collect_all': ['PyQt5'],
            'recommendations': [
                '建议使用 --collect-all PyQt5',
                'GUI应用，可能需要额外的Qt插件',
                '确保包含所需的Qt模块'
            ]
        }
    
    @staticmethod
    def get_pyqt6_template() -> Dict[str, Any]:
        """PyQt6配置模板"""
        return {
            'name': 'PyQt6',
            'description': 'PyQt6 GUI框架',
            'indicators': ['PyQt6', 'PyQt6.QtWidgets', 'PyQt6.QtCore'],
            'hidden_imports': [
                'PyQt6.sip',
                'PyQt6.QtCore',
                'PyQt6.QtGui',
                'PyQt6.QtWidgets'
            ],
            'collect_all': ['PyQt6'],
            'recommendations': [
                '建议使用 --collect-all PyQt6',
                'GUI应用，注意与PyQt5的兼容性',
                '确保包含所需的Qt模块'
            ]
        }
    
    @staticmethod
    def get_tkinter_template() -> Dict[str, Any]:
        """Tkinter配置模板"""
        return {
            'name': 'Tkinter',
            'description': 'Tkinter GUI框架',
            'indicators': ['tkinter', 'Tkinter'],
            'hidden_imports': [
                'tkinter.ttk',
                'tkinter.messagebox',
                'tkinter.filedialog',
                '_tkinter'
            ],
            'recommendations': [
                'Tkinter通常内置在Python中',
                '确保包含所有子模块',
                '可能需要tcl/tk库文件'
            ]
        }
    
    @staticmethod
    def get_requests_template() -> Dict[str, Any]:
        """Requests配置模板"""
        return {
            'name': 'Requests',
            'description': 'Requests HTTP库',
            'indicators': ['requests'],
            'hidden_imports': [
                'urllib3',
                'certifi',
                'chardet',
                'idna'
            ],
            'collect_all': ['requests', 'urllib3', 'certifi'],
            'recommendations': [
                '建议使用 --collect-all requests',
                '确保包含SSL证书文件',
                '网络库，可能需要代理配置'
            ]
        }
    
    @staticmethod
    def get_selenium_template() -> Dict[str, Any]:
        """Selenium配置模板"""
        return {
            'name': 'Selenium',
            'description': 'Selenium Web自动化库',
            'indicators': ['selenium'],
            'hidden_imports': [
                'selenium.webdriver.chrome',
                'selenium.webdriver.firefox',
                'selenium.webdriver.edge',
                'selenium.webdriver.common'
            ],
            'collect_all': ['selenium'],
            'recommendations': [
                '建议使用 --collect-all selenium',
                '需要单独下载浏览器驱动',
                '确保包含所有webdriver模块'
            ]
        }
    
    @staticmethod
    def get_pillow_template() -> Dict[str, Any]:
        """Pillow配置模板"""
        return {
            'name': 'Pillow',
            'description': 'Pillow图像处理库',
            'indicators': ['PIL', 'Pillow'],
            'hidden_imports': [
                'PIL._imaging',
                'PIL._imagingft',
                'PIL._imagingmath'
            ],
            'collect_all': ['PIL'],
            'recommendations': [
                '建议使用 --collect-all PIL',
                '图像处理库，确保包含所有格式支持',
                '可能需要额外的图像库文件'
            ]
        }
