"""简单的测试脚本，用于验证Fight应用的基本功能"""

import sys
import os

# 添加项目路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

def test_basic_imports():
    """测试基本模块导入"""
    print("🧪 测试基本模块导入...")

    try:
        from rich.console import Console
        print("  ✓ rich.console imported")
    except ImportError as e:
        print(f"  ✗ rich import failed: {e}")
        return False

    try:
        from anthropic import Anthropic
        print("  ✓ anthropic imported")
    except ImportError as e:
        print(f"  ✗ anthropic import failed: {e}")
        return False

    try:
        from fight.memory_store import MemoryStore
        print("  ✓ fight.memory_store imported")
    except ImportError as e:
        print(f"  ✗ fight.memory_store import failed: {e}")
        return False

    try:
        from fight.debate_manager import DebateManager
        print("  ✓ fight.debate_manager imported")
    except ImportError as e:
        print(f"  ✗ fight.debate_manager import failed: {e}")
        return False

    try:
        from fight.cli import FightCLI
        print("  ✓ fight.cli imported")
    except ImportError as e:
        print(f"  ✗ fight.cli import failed: {e}")
        return False

    print("✅ 所有模块导入成功！")
    return True


def test_rich_console():
    """测试Rich控制台输出"""
    print("\n🎨 测试Rich控制台输出...")

    try:
        from rich.console import Console
        console = Console()

        console.print("[bold green]Fight应用测试[/bold green]")
        console.print("这是一个测试消息，检查Rich输出是否正常工作。")
        console.print("[yellow]警告信息测试[/yellow]")
        console.print("[red]错误信息测试[/red]")

        print("✅ Rich控制台测试成功！")
        return True

    except Exception as e:
        print(f"✗ Rich控制台测试失败: {e}")
        return False


def test_memory_store_structure():
    """测试记忆存储结构（不连接真实数据库）"""
    print("\n💾 测试记忆存储结构...")

    try:
        from fight.memory_store import MemoryStore

        # 检查类结构
        methods = ['start_debate_session', 'save_argument', 'save_evidence',
                  'get_debate_history', 'get_key_arguments', 'search_relevant_context']

        for method in methods:
            if not hasattr(MemoryStore, method):
                print(f"  ✗ MemoryStore缺少方法: {method}")
                return False

        print(f"  ✓ MemoryStore包含所有必需方法")

        # 注意：不实例化，因为会尝试连接数据库
        print("✅ 记忆存储结构测试成功！")
        return True

    except Exception as e:
        print(f"✗ 记忆存储结构测试失败: {e}")
        return False


def test_debate_manager_structure():
    """测试辩论管理器结构（不连接真实AI服务）"""
    print("\n🗣️ 测试辩论管理器结构...")

    try:
        from fight.debate_manager import DebateManager

        # 检查类结构
        methods = ['start_debate', 'process_user_argument', 'generate_decision',
                  'get_summary', 'end_debate', 'is_active']

        for method in methods:
            if not hasattr(DebateManager, method):
                print(f"  ✗ DebateManager缺少方法: {method}")
                return False

        print(f"  ✓ DebateManager包含所有必需方法")
        print("✅ 辩论管理器结构测试成功！")
        return True

    except Exception as e:
        print(f"✗ 辩论管理器结构测试失败: {e}")
        return False


def test_cli_structure():
    """测试CLI结构（不运行实际CLI）"""
    print("\n🖥️ 测试CLI结构...")

    try:
        from fight.cli import FightCLI

        # 检查类结构
        methods = ['initialize', 'show_welcome', 'start_debate',
                  'run_debate_loop', 'show_summary', 'generate_decision']

        for method in methods:
            if not hasattr(FightCLI, method):
                print(f"  ✗ FightCLI缺少方法: {method}")
                return False

        print(f"  ✓ FightCLI包含所有必需方法")
        print("✅ CLI结构测试成功！")
        return True

    except Exception as e:
        print(f"✗ CLI结构测试失败: {e}")
        return False


def test_file_structure():
    """测试文件结构"""
    print("\n📁 测试项目文件结构...")

    import os
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

    required_files = [
        'fight/__init__.py',
        'fight/cli.py',
        'fight/debate_manager.py',
        'fight/memory_store.py',
        'requirements.txt',
        'README.md',
        'run.sh'
    ]

    all_exist = True
    for file_path in required_files:
        full_path = os.path.join(base_dir, file_path)
        if os.path.exists(full_path):
            print(f"  ✓ {file_path} 存在")
        else:
            print(f"  ✗ {file_path} 不存在")
            all_exist = False

    if all_exist:
        print("✅ 所有必需文件都存在！")
        return True
    else:
        print("✗ 部分文件缺失")
        return False


def main():
    """运行所有测试"""
    print("🧪 Fight应用基础功能测试")
    print("=" * 50)

    tests = [
        test_file_structure,
        test_basic_imports,
        test_rich_console,
        test_memory_store_structure,
        test_debate_manager_structure,
        test_cli_structure
    ]

    results = []
    for test in tests:
        try:
            result = test()
            results.append(result)
        except Exception as e:
            print(f"测试 {test.__name__} 发生异常: {e}")
            results.append(False)

    print("\n" + "=" * 50)
    passed = sum(results)
    total = len(results)
    print(f"📊 测试结果: {passed}/{total} 通过")

    if passed == total:
        print("🎉 所有测试通过！Fight应用基础结构完整。")
        print("\n⚠️  注意：实际使用需要配置:")
        print("1. ANTHROPIC_API_KEY - 用于AI对话")
        print("2. AGENTS_MEMORY_DSN - 用于记忆存储")
        print("3. AGENTS_MEMORY_API_KEY - 用于记忆存储访问")
        return 0
    else:
        print("❌ 部分测试失败，请检查相关组件。")
        return 1


if __name__ == "__main__":
    sys.exit(main())