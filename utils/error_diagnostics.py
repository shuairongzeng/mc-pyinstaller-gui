"""
错误诊断和自动修复建议系统
"""
import os
import re
import sys
import subprocess
from typing import Dict, List, Optional, Tuple, Any
from pathlib import Path
import importlib.util

from utils.logger import log_info, log_error, log_warning


class ErrorDiagnostics:
    """错误诊断系统"""
    
    def __init__(self):
        self.diagnostic_rules = self._load_diagnostic_rules()
        self.auto_fix_handlers = self._load_auto_fix_handlers()
    
    def diagnose_error(self, error_type: str, error_message: str, context: Dict[str, Any] = None) -> Dict[str, Any]:
        """诊断错误并提供解决方案"""
        context = context or {}
        
        diagnosis = {
            'error_type': error_type,
            'error_message': error_message,
            'severity': 'medium',
            'category': 'unknown',
            'root_cause': '',
            'solutions': [],
            'auto_fix_available': False,
            'prevention_tips': [],
            'related_docs': []
        }
        
        # 查找匹配的诊断规则
        for rule_name, rule in self.diagnostic_rules.items():
            if self._match_rule(rule, error_type, error_message, context):
                diagnosis.update(rule.get('diagnosis', {}))
                diagnosis['solutions'].extend(rule.get('solutions', []))
                diagnosis['prevention_tips'].extend(rule.get('prevention_tips', []))
                diagnosis['related_docs'].extend(rule.get('related_docs', []))
                
                # 检查是否有自动修复
                if rule_name in self.auto_fix_handlers:
                    diagnosis['auto_fix_available'] = True
                
                break
        
        return diagnosis
    
    def auto_fix_error(self, error_type: str, error_message: str, context: Dict[str, Any] = None) -> Tuple[bool, str]:
        """尝试自动修复错误"""
        context = context or {}
        
        # 查找匹配的自动修复处理器
        for rule_name, rule in self.diagnostic_rules.items():
            if self._match_rule(rule, error_type, error_message, context):
                if rule_name in self.auto_fix_handlers:
                    try:
                        handler = self.auto_fix_handlers[rule_name]
                        success, message = handler(error_type, error_message, context)
                        log_info(f"自动修复尝试: {rule_name}, 结果: {success}, 消息: {message}")
                        return success, message
                    except Exception as e:
                        log_error(f"自动修复失败: {rule_name}, 错误: {e}")
                        return False, f"自动修复过程中出错: {e}"
        
        return False, "没有找到适用的自动修复方案"
    
    def _match_rule(self, rule: Dict, error_type: str, error_message: str, context: Dict) -> bool:
        """检查规则是否匹配当前错误"""
        # 检查错误类型匹配
        if 'error_types' in rule:
            if error_type not in rule['error_types']:
                return False
        
        # 检查错误消息模式匹配
        if 'patterns' in rule:
            for pattern in rule['patterns']:
                if re.search(pattern, error_message, re.IGNORECASE):
                    return True
            return False
        
        # 检查上下文条件
        if 'conditions' in rule:
            for condition in rule['conditions']:
                if not self._check_condition(condition, context):
                    return False
        
        return True
    
    def _check_condition(self, condition: Dict, context: Dict) -> bool:
        """检查上下文条件"""
        condition_type = condition.get('type')
        
        if condition_type == 'file_exists':
            return os.path.exists(condition['path'])
        elif condition_type == 'module_available':
            return self._is_module_available(condition['module'])
        elif condition_type == 'context_key':
            return condition['key'] in context
        elif condition_type == 'context_value':
            return context.get(condition['key']) == condition['value']
        
        return True
    
    def _is_module_available(self, module_name: str) -> bool:
        """检查模块是否可用"""
        try:
            spec = importlib.util.find_spec(module_name)
            return spec is not None
        except (ImportError, ValueError, ModuleNotFoundError):
            return False
    
    def _load_diagnostic_rules(self) -> Dict[str, Dict]:
        """加载诊断规则"""
        return {
            'missing_module': {
                'error_types': ['ModuleNotFoundError', 'ImportError'],
                'patterns': [r'No module named [\'"]([^\'"]+)[\'"]', r'cannot import name'],
                'diagnosis': {
                    'severity': 'high',
                    'category': 'dependency',
                    'root_cause': '缺少必要的Python模块或模块安装不正确'
                },
                'solutions': [
                    '使用pip安装缺失的模块',
                    '检查模块名称拼写是否正确',
                    '确认虚拟环境已正确激活',
                    '检查Python路径配置',
                    '更新requirements.txt文件'
                ],
                'prevention_tips': [
                    '使用requirements.txt管理依赖',
                    '定期更新依赖版本',
                    '使用虚拟环境隔离项目依赖'
                ],
                'related_docs': [
                    'https://pip.pypa.io/en/stable/',
                    'https://docs.python.org/3/tutorial/venv.html'
                ]
            },
            'file_not_found': {
                'error_types': ['FileNotFoundError'],
                'patterns': [r'No such file or directory', r'cannot find the file'],
                'diagnosis': {
                    'severity': 'high',
                    'category': 'filesystem',
                    'root_cause': '指定的文件或目录不存在'
                },
                'solutions': [
                    '检查文件路径是否正确',
                    '确认文件是否存在',
                    '使用绝对路径而非相对路径',
                    '检查文件权限',
                    '确认文件名大小写正确'
                ],
                'prevention_tips': [
                    '使用pathlib处理路径',
                    '在使用文件前先检查存在性',
                    '使用配置文件管理路径'
                ]
            },
            'permission_denied': {
                'error_types': ['PermissionError'],
                'patterns': [r'Permission denied', r'Access is denied'],
                'diagnosis': {
                    'severity': 'medium',
                    'category': 'security',
                    'root_cause': '没有足够的权限访问文件或目录'
                },
                'solutions': [
                    '以管理员身份运行程序',
                    '检查文件/目录权限设置',
                    '确认文件未被其他程序占用',
                    '检查防病毒软件设置',
                    '修改文件所有者或权限'
                ],
                'prevention_tips': [
                    '避免在系统目录中操作文件',
                    '使用用户目录存储应用数据',
                    '正确设置文件权限'
                ]
            },
            'pyinstaller_error': {
                'error_types': ['subprocess.CalledProcessError', 'RuntimeError'],
                'patterns': [r'PyInstaller', r'pyinstaller', r'failed to execute script'],
                'diagnosis': {
                    'severity': 'high',
                    'category': 'packaging',
                    'root_cause': 'PyInstaller打包过程中出现错误'
                },
                'solutions': [
                    '检查PyInstaller版本兼容性',
                    '清理build和dist目录',
                    '添加缺失的隐藏导入',
                    '检查脚本路径和依赖',
                    '使用--debug选项获取详细信息'
                ],
                'prevention_tips': [
                    '保持PyInstaller版本更新',
                    '使用spec文件管理复杂配置',
                    '定期清理构建缓存'
                ]
            },
            'encoding_error': {
                'error_types': ['UnicodeDecodeError', 'UnicodeEncodeError'],
                'patterns': [r'codec can\'t decode', r'codec can\'t encode'],
                'diagnosis': {
                    'severity': 'medium',
                    'category': 'encoding',
                    'root_cause': '文件编码问题或字符编码不匹配'
                },
                'solutions': [
                    '指定正确的文件编码（如UTF-8）',
                    '使用encoding参数打开文件',
                    '转换文件编码格式',
                    '处理特殊字符'
                ],
                'prevention_tips': [
                    '统一使用UTF-8编码',
                    '在文件操作时明确指定编码',
                    '避免使用特殊字符作为文件名'
                ]
            }
        }
    
    def _load_auto_fix_handlers(self) -> Dict[str, callable]:
        """加载自动修复处理器"""
        return {
            'missing_module': self._auto_fix_missing_module,
            'file_not_found': self._auto_fix_file_not_found,
            'permission_denied': self._auto_fix_permission_denied
        }
    
    def _auto_fix_missing_module(self, error_type: str, error_message: str, context: Dict) -> Tuple[bool, str]:
        """自动修复缺失模块问题"""
        # 提取模块名
        match = re.search(r'No module named [\'"]([^\'"]+)[\'"]', error_message)
        if not match:
            return False, "无法提取模块名称"
        
        module_name = match.group(1)
        
        try:
            # 尝试安装模块
            python_exe = sys.executable
            result = subprocess.run(
                [python_exe, '-m', 'pip', 'install', module_name],
                capture_output=True,
                text=True,
                timeout=60
            )
            
            if result.returncode == 0:
                return True, f"成功安装模块: {module_name}"
            else:
                return False, f"安装失败: {result.stderr}"
                
        except subprocess.TimeoutExpired:
            return False, "安装超时"
        except Exception as e:
            return False, f"安装过程出错: {e}"
    
    def _auto_fix_file_not_found(self, error_type: str, error_message: str, context: Dict) -> Tuple[bool, str]:
        """自动修复文件未找到问题"""
        # 这里可以实现一些简单的文件路径修复逻辑
        # 比如检查常见的路径变体、创建缺失的目录等
        
        # 从上下文中获取文件路径
        file_path = context.get('file_path')
        if not file_path:
            return False, "无法获取文件路径信息"
        
        # 尝试创建父目录
        try:
            parent_dir = Path(file_path).parent
            if not parent_dir.exists():
                parent_dir.mkdir(parents=True, exist_ok=True)
                return True, f"创建了缺失的目录: {parent_dir}"
        except Exception as e:
            return False, f"创建目录失败: {e}"
        
        return False, "无法自动修复文件路径问题"
    
    def _auto_fix_permission_denied(self, error_type: str, error_message: str, context: Dict) -> Tuple[bool, str]:
        """自动修复权限问题"""
        # 权限问题通常需要用户手动处理，这里只能提供建议
        return False, "权限问题需要手动解决，建议以管理员身份运行程序"


# 全局错误诊断实例
_error_diagnostics: Optional[ErrorDiagnostics] = None


def get_error_diagnostics() -> ErrorDiagnostics:
    """获取错误诊断实例"""
    global _error_diagnostics
    if _error_diagnostics is None:
        _error_diagnostics = ErrorDiagnostics()
    return _error_diagnostics


def diagnose_and_suggest(error_type: str, error_message: str, context: Dict[str, Any] = None) -> Dict[str, Any]:
    """诊断错误并提供建议"""
    diagnostics = get_error_diagnostics()
    return diagnostics.diagnose_error(error_type, error_message, context)


def try_auto_fix(error_type: str, error_message: str, context: Dict[str, Any] = None) -> Tuple[bool, str]:
    """尝试自动修复错误"""
    diagnostics = get_error_diagnostics()
    return diagnostics.auto_fix_error(error_type, error_message, context)
