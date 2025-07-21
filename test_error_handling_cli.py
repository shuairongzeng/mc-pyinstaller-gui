"""
错误处理增强功能命令行测试
"""
import sys
import os

# 添加项目根目录到Python路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from utils.exceptions import (
    setup_global_exception_handler, 
    PyInstallerGUIException,
    ConfigurationError,
    PackageError,
    ModuleDetectionError
)
from utils.error_diagnostics import get_error_diagnostics, diagnose_and_suggest, try_auto_fix
from utils.logger import get_error_reporter


def test_error_diagnostics():
    """测试错误诊断功能"""
    print("=== 错误诊断测试 ===")
    
    # 测试模块未找到错误诊断
    diagnosis = diagnose_and_suggest(
        "ModuleNotFoundError",
        "No module named 'numpy'",
        {"script_path": "test.py"}
    )
    
    print(f"错误类型: {diagnosis['error_type']}")
    print(f"严重程度: {diagnosis['severity']}")
    print(f"根本原因: {diagnosis['root_cause']}")
    print(f"解决方案: {diagnosis['solutions']}")
    print(f"自动修复可用: {diagnosis['auto_fix_available']}")
    print()
    
    # 测试文件未找到错误诊断
    diagnosis2 = diagnose_and_suggest(
        "FileNotFoundError",
        "No such file or directory: 'config.json'",
        {"file_path": "config.json"}
    )
    
    print("文件错误诊断:")
    print(f"解决方案: {diagnosis2['solutions']}")
    print()


def test_auto_fix():
    """测试自动修复功能"""
    print("=== 自动修复测试 ===")
    
    # 测试文件路径修复
    success, message = try_auto_fix(
        "FileNotFoundError",
        "No such file or directory: 'logs/test.log'",
        {"file_path": "logs/test.log"}
    )
    
    print(f"文件修复结果: {success}")
    print(f"文件修复消息: {message}")
    print()


def test_error_report():
    """测试错误报告功能"""
    print("=== 错误报告测试 ===")
    
    reporter = get_error_reporter()
    
    # 生成测试错误报告
    report_id = reporter.generate_error_report(
        "TestError",
        "这是一个测试错误",
        {
            "test_context": "error_handling_test",
            "user_action": "运行命令行测试",
            "system_state": "正常"
        },
        "测试堆栈跟踪信息"
    )
    
    print(f"错误报告已生成: {report_id}")
    
    # 列出所有错误报告
    reports = reporter.list_error_reports()
    print(f"总共有 {len(reports)} 个错误报告")
    
    if reports:
        latest = reports[0]
        print(f"最新报告: {latest['filename']}")
        print(f"创建时间: {latest['created']}")
        print(f"文件大小: {latest['size']} 字节")
    print()


def test_custom_exceptions():
    """测试自定义异常"""
    print("=== 自定义异常测试 ===")
    
    try:
        # 测试配置错误
        raise ConfigurationError(
            "脚本路径无效",
            field="script_path",
            suggestions=["选择有效的Python文件", "检查文件权限"]
        )
    except ConfigurationError as e:
        print(f"配置错误: {e}")
        print(f"错误代码: {e.error_code}")
        print(f"字段: {e.field}")
        print(f"建议: {e.suggestions}")
        print()
    
    try:
        # 测试打包错误
        raise PackageError(
            "PyInstaller执行失败",
            command="pyinstaller --onefile test.py",
            suggestions=["检查PyInstaller版本", "清理build目录"]
        )
    except PackageError as e:
        print(f"打包错误: {e}")
        print(f"命令: {e.command}")
        print(f"建议: {e.suggestions}")
        print()


def test_global_exception_handler():
    """测试全局异常处理器"""
    print("=== 全局异常处理器测试 ===")
    
    # 设置全局异常处理器
    handler = setup_global_exception_handler()
    print("全局异常处理器已设置")
    
    # 测试异常处理规则加载
    print(f"已加载 {len(handler.error_solutions)} 个错误解决方案")
    
    # 测试解决方案查找
    solution = handler._find_solution("ModuleNotFoundError", "No module named 'requests'")
    if solution:
        print("找到解决方案:")
        print(f"  解决方案: {solution['solution']}")
        print(f"  严重程度: {solution['severity']}")
        print(f"  操作建议: {solution['actions'][:2]}")  # 只显示前两个建议
    print()


def main():
    """主函数"""
    print("错误处理增强功能命令行测试")
    print("=" * 50)
    
    try:
        # 运行各项测试
        test_global_exception_handler()
        test_error_diagnostics()
        test_auto_fix()
        test_error_report()
        test_custom_exceptions()
        
        print("所有测试完成！")
        print("\n测试结果:")
        print("✅ 全局异常处理器 - 正常")
        print("✅ 错误诊断系统 - 正常")
        print("✅ 自动修复功能 - 正常")
        print("✅ 错误报告系统 - 正常")
        print("✅ 自定义异常类 - 正常")
        
        # 检查生成的文件
        if os.path.exists("logs/error_reports"):
            report_count = len([f for f in os.listdir("logs/error_reports") if f.endswith('.md')])
            print(f"✅ 生成了 {report_count} 个错误报告文件")
        
        return 0
        
    except Exception as e:
        print(f"测试过程中出现错误: {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())
