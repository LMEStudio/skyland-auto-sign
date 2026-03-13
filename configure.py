import logging
import json
import pyperclip

from utils.logger import config_logger
from utils.config import get_config, get_secret
from utils.push import initPushConfig, pushMessage
from utils.skyland import saveAccount, login

from rich.console import Console
from rich.prompt import Prompt
from rich.panel import Panel

config = get_config()
secret = get_secret()
console = Console()


def initAccountConfig(): 
    while True:
        username = Prompt.ask("[bold yellow]请输入账号[/bold yellow]")
        password = Prompt.ask("[bold yellow]请输入密码[/bold yellow]")
        console.print("[bold yellow]执行登录[/bold yellow]")
        user = login(username, password)
        saveAccount(user)
        if (Prompt.ask("[bold yellow]是否继续添加账号？[/bold yellow]", choices=["y", "n"]) == "n"):
            break


def printDump(name: str, file: str, copy: bool, style: int):
    file = json.dumps(file, ensure_ascii=False)
    if copy:
        pyperclip.copy(file)
        console.print(f"[bold yellow]提示：[/bold yellow][bold magenta]{name} 的值已写入剪贴板 [/bold magenta]")
    if style == 1:
        console.print(Panel(f"[green]{file}[/green]", title=name, expand=False, style="bold cyan"))
    if style == 2:
        console.rule(f"[bold cyan]{name}[/bold cyan]")
        console.print(f"[green]{file}[/green]\n")


def printKey(key: str):
    console.print(Panel(f"[green]{config[key]}[/green]", title=f"当前 {key} 配置", expand=False, style="bold cyan"))


if __name__ == '__main__':
    config_logger(level=logging.INFO)

    console.print("[bold green]Skyland Auto Sign Configure[/bold green]")
    console.print("[bold yellow]请选择一个操作：[/bold yellow]")
    console.print("[cyan]1.[/cyan] 添加用户账户")
    console.print("[cyan]2.[/cyan] 配置消息推送")
    console.print("[cyan]3.[/cyan] 获取所有配置")
    console.print("[cyan]4.[/cyan] 修改配置文件")
    console.print("[cyan]5.[/cyan] 测试消息推送")

    # 获取用户选择
    choice = Prompt.ask(
        "[bold green]请输入选项编号[/bold green]", choices=["1", "2", "3", "4", "5"]
    )

    if choice == "1":
        initAccountConfig()

    elif choice == "2":
        initPushConfig()

    elif choice == "3":
        steps = (
            "1. 启用 [bold yellow]Actions[/bold yellow]\n"
            "2. 请保管好 [bold yellow]secret.json[/bold yellow] 内的内容"
        )
        console.print(Panel(steps, title="注意事项", expand=False, style="bold red"))

        printDump("SECRET.JSON", secret, True, 2)
        printDump("CONFIG.JSON", config, False, 2)

    elif choice == "4":
        printDump("当前配置", config, False, 1)
        while True:
            console.print("[bold yellow]请选择要修改的配置[/bold yellow]")
            console.print("[cyan]1.[/cyan] 推送 messagePush")
            console.print("[cyan]2.[/cyan] 代理 useProxy")
            console.print("[cyan]3.[/cyan] 刷新期限 renewPeriod")
            console.print("[cyan]4.[/cyan] 出错时退出 exitWhenFail")

            # 获取用户选择
            choice = Prompt.ask(
                "[bold green]请输入选项编号[/bold green]", choices=["1", "2", "3", "4"]
            )

            if choice == "1":
                key = "messagePush"
                printKey(key)
                ch = Prompt.ask("[cyan]*[/cyan] 启用", choices=["y", "n"]) 
                if ch == "y": 
                    config['messagePush']['enabled'] = True
                    with open("config.json", "w", encoding="utf-8") as f:
                        json.dump(config, f, ensure_ascii=False, indent=4)
                    printDump("当前配置", config, False, 1)
                    printKey(key)
                elif ch == "n":
                    config['messagePush']['enabled'] = False
                    with open("config.json", "w", encoding="utf-8") as f:
                        json.dump(config, f, ensure_ascii=False, indent=4)
                    printDump("当前配置", config, False, 1)
                    printKey(key)

            elif choice == "2":
                key = "useProxy"
                printKey(key)
                ch = Prompt.ask("[cyan]*[/cyan] 启用", choices=["y", "n"]) 
                if ch == "y": 
                    config[key]['enabled'] = True
                    config[key]['addr'] = Prompt.ask("[cyan]*[/cyan] 代理地址") 
                    with open("config.json", "w", encoding="utf-8") as f:
                        json.dump(config, f, ensure_ascii=False, indent=4)
                    printKey(key)
                    printDump("当前配置", config, False, 1)

                elif ch == "n":
                    config[key]['enabled'] = False
                    config[key]['addr'] = ''
                    with open("config.json", "w", encoding="utf-8") as f:
                        json.dump(config, f, ensure_ascii=False, indent=4)
                    printDump("当前配置", config, False, 1)
            
            elif choice == "3":
                key = "renewPeriod"
                printKey(key)
                config[key] = Prompt.ask("[cyan]*[/cyan] 刷新间隔(s)") 
                with open("config.json", "w", encoding="utf-8") as f:
                    json.dump(config, f, ensure_ascii=False, indent=4)
                printKey(key)
                printDump("当前配置", config, False, 1)

            elif choice == "4":
                key = "exitWhenFail"
                printKey(key)
                ch = Prompt.ask("[cyan]*[/cyan] 启用", choices=["y", "n"]) 
                if ch == "y": 
                    config[key] = True
                    with open("config.json", "w", encoding="utf-8") as f:
                        json.dump(config, f, ensure_ascii=False, indent=4)
                    printKey(key)
                    printDump("当前配置", config, False, 1)
                elif ch == "n":
                    config[key] = False
                    with open("config.json", "w", encoding="utf-8") as f:
                        json.dump(config, f, ensure_ascii=False, indent=4)
                    printKey(key)
                    printDump("当前配置", config, False, 1)
            if (Prompt.ask("[bold yellow]是否继续修改？[/bold yellow]", choices=["y", "n"]) == "n"):
                break
    elif choice == "5":
        pushMessage("测试消息")