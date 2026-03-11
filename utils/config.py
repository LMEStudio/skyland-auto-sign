import os, sys
from enum import Enum
import json
import logging

"""
是否启用调试模式
更详细的日志打印，浏览器操作可视化等
"""
DEBUG = False
CONFIGFILE = "config.json"
SECRETFILE = "secret.json"

config = None
secret = None

class Environment(Enum):
    GITHUBACTION = "GITHUB_ACTION"  # GitHub Action 运行
    LOCAL = "LOCAL"  # 本地代码运行
    PACKED = "PACKED"  # PyInstaller 打包运行

    def __str__(self):
        return self.value


def get_environment():
    if getattr(sys, "frozen", False) and hasattr(sys, "_MEIPASS"):
        return Environment.PACKED
    elif os.getenv("GITHUB_ACTIONS") == "true":
        return Environment.GITHUBACTION
    else:
        return Environment.LOCAL


def get_config():
    """
    获取配置信息
    :return: 配置字典
    """
    global config
    
    if config:
        return config
    
    env = get_environment()

    configFile = CONFIGFILE

    if env == Environment.PACKED:
        configFile = os.path.join(os.path.dirname(sys.executable), CONFIGFILE)

    with open(configFile, "r", encoding="utf-8") as f:
        config = json.loads(f.read())
    return config


def get_secret():
    """
    获取用户数据目录
    :return: 用户数据目录路径
    """
    global secret
    
    if secret:
        return secret
    
    env = get_environment()
    
    secretFile = SECRETFILE
    secretJson = ""

    if env == Environment.GITHUBACTION:
        secretJson = os.getenv("SECRET", None)
        if not secretJson:
            logging.error("环境变量 SECRET 未设置")
            exit(1)
    else:
        if env == Environment.PACKED:
            secretFile = os.path.join(os.path.dirname(sys.executable), SECRETFILE)
        with open(secretFile, "r", encoding="utf-8") as f:
            secretJson = f.read()

    secret = json.loads(secretJson)
    return secret
