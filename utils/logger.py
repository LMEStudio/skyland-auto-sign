import logging
import os
from datetime import date
import json
import requests

from utils.config import get_config

# use_proxy = os.environ.get('USE_PROXY')

config = get_config()
use_proxy = config.get("useProxy", {}).get("enabled", False)

def config_logger(level=logging.DEBUG):
    current_date = date.today().strftime('%Y-%m-%d')
    if not os.path.exists('logs'):
        os.mkdir('logs')
    logger = logging.getLogger()

    file_handler = logging.FileHandler(f'./logs/{current_date}.log', encoding='utf-8')
    logger.addHandler(file_handler)
    logger.setLevel(level)
    file_handler.setLevel(level)
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    file_handler.setFormatter(formatter)

    console_handler = logging.StreamHandler()
    # console_formatter = logging.Formatter('%(message)s')
    # console_handler.setFormatter(console_formatter)
    console_handler.setLevel(level)
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)

    def filter_code(text):
        filter_key = ['code', 'cred', 'token']
        try:
            j = json.loads(text)
            if not j.get('data'):
                return text
            data = j['data']
            for i in filter_key:
                if i in data:
                    data[i] = '*****'
            return json.dumps(j, ensure_ascii=False)
        except:
            return text
        
    _get = requests.get
    _post = requests.post

    def get(*args, **kwargs):
        if use_proxy:
            kwargs.update({
                'proxies': {
                    'https': 'http://localhost:8000',
                },
                'verify': False
            })
        response = _get(*args, **kwargs)
        logging.debug(f'GET {args[0]} - {response.status_code} - {filter_code(response.text)}')
        return response

    def post(*args, **kwargs):
        if use_proxy:
            kwargs.update({
                'proxies': {
                    'https': 'http://localhost:8000',
                },
                'verify': False
            })
        response = _post(*args, **kwargs)
        logging.debug(f'POST {args[0]} - {response.status_code} - {filter_code(response.text)}')
        return response

    # 替换 requests 中的方法
    requests.get = get
    requests.post = post