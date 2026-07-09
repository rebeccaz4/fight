"""CLI界面模块 - 处理用户交互和命令界面"""

import sys
from pathlib import Path
from typing import Optional

from rich.console import Console
from rich.panel import Panel
from rich.prompt import Prompt
from rich.table import Table

from fight.debate_manager import DebateManager
from fight.memory_store import MemoryStore

console = Console()


class FightCLI:
    """Fight CLI主类"""

    def __init__(self):
        self.memory_store: Optional[MemoryStore] = None
        self.debate_manager: Optional[DebateManager] = None
        self.running = True

    def initialize(self):
        """初始化系统组件"""
        try:
            console.print("[bold blue]初始化 Fight 系统中...[/bold blue]")

            # 初始化记忆存储
            self.memory_store = MemoryStore()
            console.print("[green]✓[/green] 记忆存储已初始化")

            # 初始化辩论管理器
            self.debate_manager = DebateManager(self.memory_store)
            console.print("[green]✓[/green] 辩论管理器已初始化")

            console.print("[bold green]系统初始化完成！[/bold green]")

        except Exception as e:
            console.print(f"[bold red]初始化失败: {e}[/bold red]")
            sys.exit(1)

    def show_welcome(self):
        """显示欢迎界面"""
        welcome_text = """
🗣️ 欢迎使用 Fight - 人机吵架决策系统

这是一个通过人机结构化辩论来帮助做出重大决策的系统。
你将与AI智能体进行辩论，系统会记录所有论点并最终生成决策建议。

使用说明：
- 输入论点进行辩论
- 输入 'quit' 退出辩论
- 输入 'summary' 查看辩论摘要
- 输入 'decision' 生成最终决策
        """

        console.print(Panel(welcome_text, title="Fight", border_style="bold blue"))

    def show_debate_state(self):
        """显示当前辩论状态"""
        if not self.debate_manager or not self.debate_manager.is_active():
            return

        table = Table(title="当前辩论状态")
        table.add_column("属性", style="cyan")
        table.add_column("值", style="white")

        table.add_row("辩论主题", self.debate_manager.topic or "未开始")
        table.add_row("轮次", str(self.debate_manager.round))
        table.add_row("论点数量", str(len(self.debate_manager.arguments)))
        table.add_row("当前状态", "进行中" if self.debate_manager.is_active() else "已结束")

        console.print(table)

    def start_debate(self):
        """开始新的辩论"""
        console.print("\n[bold yellow]开始新的辩论[/bold yellow]")

        # 获取辩论主题
        topic = Prompt.ask("请输入要决策的主题", console=console)
        if not topic.strip():
            console.print("[red]主题不能为空[/red]")
            return

        # 获取用户初始立场
        position = Prompt.ask("请输入你的初始立场", console=console)

        # 开始辩论
        try:
            self.debate_manager.start_debate(topic, position)
            console.print(f"[green]辩论已开始！主题: {topic}[/green]")

        except Exception as e:
            console.print(f"[red]开始辩论失败: {e}[/red]")

    def run_debate_loop(self):
        """运行辩论主循环"""
        if not self.debate_manager or not self.debate_manager.is_active():
            console.print("[yellow]请先开始一个辩论[/yellow]")
            return

        console.print("\n[bold green]辩论开始！输入你的论点（或输入命令）[/bold green]")

        while self.debate_manager.is_active():
            try:
                # 获取用户输入
                user_input = Prompt.ask("\n[你]", console=console)

                if not user_input.strip():
                    continue

                # 处理命令
                if user_input.lower() in ['quit', 'exit', 'q']:
                    console.print("[yellow]结束辩论[/yellow]")
                    self.debate_manager.end_debate()
                    break

                elif user_input.lower() == 'summary':
                    self.show_summary()
                    continue

                elif user_input.lower() == 'decision':
                    self.generate_decision()
                    break

                # 处理论点
                response = self.debate_manager.process_user_argument(user_input)

                # 显示AI回应
                console.print(f"\n[bold cyan][AI智能体][/bold cyan]")
                console.print(response)

                # 更新轮次
                self.debate_manager.next_round()

            except KeyboardInterrupt:
                console.print("\n[yellow]收到中断信号，结束辩论[/yellow]")
                self.debate_manager.end_debate()
                break

            except Exception as e:
                console.print(f"[red]处理论点时出错: {e}[/red]")

    def show_summary(self):
        """显示辩论摘要"""
        if not self.debate_manager:
            return

        summary = self.debate_manager.get_summary()

        console.print("\n[bold yellow]辩论摘要[/bold yellow]")
        console.print(f"主题: {summary['topic']}")
        console.print(f"轮次: {summary['round']}")
        console.print(f"总论点数: {summary['argument_count']}")

        if summary['key_arguments']:
            console.print("\n[bold]关键论点:[/bold]")
            for i, arg in enumerate(summary['key_arguments'], 1):
                console.print(f"{i}. {arg}")

    def generate_decision(self):
        """生成最终决策"""
        if not self.debate_manager:
            return

        console.print("\n[bold yellow]生成决策建议中...[/bold yellow]")

        try:
            decision = self.debate_manager.generate_decision()

            console.print("\n[bold green]=== 决策建议 ===[/bold green]")
            console.print(decision['recommendation'])
            console.print(f"\n置信度: {decision['confidence']}%")

            if decision['reasoning']:
                console.print("\n[bold]推理过程:[/bold]")
                console.print(decision['reasoning'])

            if decision['risks']:
                console.print("\n[bold red]主要风险:[/bold red]")
                for risk in decision['risks']:
                    console.print(f"- {risk}")

            # 结束辩论
            self.debate_manager.end_debate()

        except Exception as e:
            console.print(f"[red]生成决策失败: {e}[/red]")

    def run(self):
        """运行主程序"""
        self.show_welcome()
        self.initialize()

        while self.running:
            try:
                # 显示菜单
                console.print("\n[bold cyan]主菜单[/bold cyan]")
                console.print("1. 开始新的辩论")
                console.print("2. 查看辩论状态")
                console.print("3. 退出")

                choice = Prompt.ask("\n请选择", choices=["1", "2", "3"], console=console)

                if choice == "1":
                    self.start_debate()
                    if self.debate_manager and self.debate_manager.is_active():
                        self.run_debate_loop()

                elif choice == "2":
                    self.show_debate_state()
                    self.show_summary()

                elif choice == "3":
                    console.print("[yellow]再见！[/yellow]")
                    self.running = False

            except KeyboardInterrupt:
                console.print("\n[yellow]收到中断信号，程序退出[/yellow]")
                self.running = False

            except Exception as e:
                console.print(f"[red]发生错误: {e}[/red]")


def main():
    """主入口函数"""
    cli = FightCLI()
    cli.run()


if __name__ == "__main__":
    main()