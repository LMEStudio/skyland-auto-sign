import requests
import os, sys, json
from datetime import date
import logging
from rich.console import Console
from rich.prompt import Prompt
from rich.panel import Panel
from utils.config import get_config, get_secret

'''
消息推送模块
'''

configJson = get_config()
secretJson = get_secret()
console = Console()

LOGFILE = f"logs/{date.today().strftime("%Y-%m-%d")}.log"

title = f'森空岛自动签到结果 - {date.today().strftime("%Y-%m-%d")}'

def composeMessage(all_logs: list[str]):
    logFile = os.path.join(os.path.dirname(os.path.abspath(sys.argv[0])), LOGFILE)
    with open(logFile, 'r', encoding='utf-8') as f:
        logs = [log.rstrip('\n') for log in f]
    if not all_logs:
        message = ['今日无可用账号或无输出']
    else:
        br = ["日志如下: "]
        message = '\n'.join(all_logs + br + logs)
    return message

def _format_serverchan_desp(message) -> str:
    if not message:
        return '今日无可用账号或无输出'
    message = message.splitlines()
    lines: list[str] = []
    for item in message:
        text = item.replace('\r\n', '\n')
        parts = text.split('\n\n')
        if not parts:
            lines.append('')
            continue
        lines.extend(parts)

    # Server酱 desp 使用 Markdown，单换行会折叠为一个空格，需要显式换行。
    return '  \n'.join(line.rstrip() for line in lines)

def serverChanTurbo(message, pushToken):
    url = f"https://sctapi.ftqq.com/{pushToken}.send"

    data = {
        'title': title or "通知",
        'desp': message
        }

    response = requests.post(url, data=data)
    if not response.status_code == 200:
        logging.error(f"Server Chan Turbo 推送失败: {response.status_code}, {response.text}")
    return response.text

def serverChanCubed(message, pushToken, uid):
    url = f"https://{uid}.push.ft07.com/send/{pushToken}.send"

    data = {
        "title": title or "通知",
        "desp": message or "",
        }   

    response = requests.post(url, json=data)
    if not response.status_code == 200:
        logging.error(f"pushplus 推送失败: {response.status_code}, {response.text}")
    return response.text

def pushplus(message, pushToken, topic):
    url = f"https://www.pushplus.plus/send?token={pushToken}"

    data = {
        'title': title or "通知", 
        "content": message or "",
        "topic": topic or "",
        }
    
    response = requests.post(url, json=data)
    if not response.status_code == 200:
        logging.error(f"pushplus 推送失败: {response.status_code}, {response.text}")
    return response.text

def qmsg(message, pushToken, qq, bot, type):
    if type == "send":
        url = f"https://qmsg.zendee.cn/jsend/{pushToken}" #私聊
    elif type == "group":
        url = f"https://qmsg.zendee.cn/jgroup/{pushToken}" #群聊

    data = {
        "msg": f"{title}\n{message}",
        "qq": qq,
        "bot": bot,
        }

    response = requests.post(url, json=data)
    if not response.status_code == 200:
        logging.error(f"pushplus 推送失败: {response.status_code}, {response.text}")
    return response.text

def configPush(pushProvider):
    if os.path.exists("secret.json"):
        with open("secret.json", "r", encoding="utf-8", newline="\n") as f:
            secretJson = json.load(f)
    else:
        secretJson["pushProvider"] = []
    
    if pushProvider == "server_chan_turbo":
        pushToken = input("请输入提供商提供的Token: ")
        pushConfig = {
            "provider": "server_chan_turbo",
            "token": pushToken
        }

    if pushProvider == "server_chan_cubed":
        pushToken = input("请输入提供商提供的Token: ")
        pushUID = input("请输入提供商提供的UID: ")
        pushConfig = {
            "provider": "server_chan_cubed",
            "token": pushToken,
            "uid": pushUID
        }

    if pushProvider == "pushplus":
        pushToken = input("请输入提供商提供的Token: ")
        pushTopic = input("(可选)请指定群组编码, 不填仅发送给自己: ")
        pushConfig = {
            "provider": "pushplus",
            "topic": pushTopic,
            "token": pushToken
        }

    if pushProvider == "qmsg":
        # === QMSG 推送 ===
        # 在本地或 GitHub Actions 设置：
        #   TOKEN: 必填
        #   QQ: 可选，指定要接收消息的QQ号或者QQ群。多个以英文逗号分割，例如：12345,12346。
        #   BOT： 可选，机器人的QQ号。
        console.print("[bold yellow]请选择: [/bold yellow]")
        console.print("[cyan]1.[/cyan] 使用QQ接收消息")
        console.print("[cyan]2.[/cyan] 使用QQ群接收消息")

        choice = Prompt.ask("[bold green]请输入选项编号 (1/2)[/bold green]", choices=["1", "2"])
        if choice == "1":
            pushType = "send"
        elif choice == "2":
            pushType = "group"
        pushToken = input("请输入提供商提供的Token: ")
        pushQQ = input("(可选)请指定要接收消息的QQ号或者QQ群(多个以英文逗号分割): ")
        pushBOT = input("(可选)请指定机器人的QQ号")
        pushConfig = {
            "provider": "qmsg",
            "type": pushType,
            "token": pushToken,
            "qq": pushQQ,
            "bot": pushBOT
        }

    secretJson["pushProvider"].append(pushConfig)

    # "uuid": str(uuid.uuid4())
    with open("secret.json", "w", encoding="utf-8") as f:
        json.dump(secretJson, f, ensure_ascii=False, indent=4)
    console.rule(f"[bold cyan]SECRET_JSON[/bold cyan]")
    console.print(f"[bold green]{secretJson}[/bold green]")

def pushMessage(message):
    for provider in secretJson["pushProvider"]:
        pushToken = provider["token"]
        #TODO: 判断是否失败
        if provider["provider"] == "server_chan_turbo":
            message = _format_serverchan_desp(message)
            console.print(f"[bold cyan]完成 {provider["provider"]} 推送\n{serverChanTurbo(message, pushToken)}[/bold cyan]")
        if provider["provider"] == "server_chan_cubed":
            message = _format_serverchan_desp(message)
            uid = provider["uid"]
            console.print(f"[bold cyan]完成 {provider["provider"]} 推送\n{serverChanCubed(message, pushToken, uid)}[/bold cyan]")
        if provider["provider"] == "pushplus":
            topic = provider["topic"]
            console.print(f"[bold cyan]完成 {provider["provider"]} 推送\n{pushplus(message, pushToken, topic)}[/bold cyan]")
        if provider["provider"] == "qmsg":
            type = provider["type"]
            qq = provider.get("qq", "")
            bot = provider.get("bot", "")
            console.print(f"[bold cyan]完成 {provider["provider"]} 推送\n{qmsg(message, pushToken, qq, bot, type)}[/bold cyan]")
        else:
            continue

    console.print(f"[bold cyan]消息推送全部完成[/bold cyan]")

def initPushConfig():
    if configJson.get("messagePush", {}).get("enabled", False):
        while True:
            console.print("[bold yellow]请选择一个提供商：[/bold yellow]")
            console.print("[cyan]1.[/cyan] Server Chan Turbo")
            console.print("[cyan]2.[/cyan] Server Chan Cubed (Server Chan 3)")
            console.print("[cyan]3.[/cyan] pushplus")
            console.print("[cyan]4.[/cyan] qmsg")

            choice = Prompt.ask("[bold green]请输入选项编号 (1/2/3/4)[/bold green]", choices=["1", "2", "3", "4"])
            if choice == "1":
                configPush("server_chan_turbo")
            elif choice == "2":
                configPush("server_chan_cubed")
            elif choice == "3":
                configPush("pushplus")
            elif choice == "4":
                configPush("qmsg")
            
            if (Prompt.ask("[bold yellow]是否继续添加消息推送？(y/n)[/bold yellow]", choices=["y", "n"]) == "n"):
                break
    else:
        steps = (
            "0. 请在 [bold yellow]config.json[/bold yellow] 内启用 [bold yellow]messagePush[/bold yellow]"
        )
        console.print(Panel(steps, title="未启用消息推送", expand=False, style="bold red"))
        exit