import time
import logging
import argparse

from utils.skyland import start
from utils.logger import config_logger
from utils.config import get_config, get_secret
from utils.push import pushMessage, composeMessage

config = get_config()
secret = get_secret()

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("--checkValidity", action="store_true", help="是否直接运行任务（默认为 False）")
    args = parser.parse_args()

    if args.checkValidity:
        from utils.skyland import checkRenewal
        checkRenewal()
    else:
        config_logger(level=logging.INFO)
        start_time = time.time()
        success, all_logs = start(secret)
        end_time = time.time()
        logging.info(f'complete within {(end_time - start_time) * 1000} ms')
        logging.info(f'exit_when_fail_env: {config.get("exitWhenFail", False)}, success: {success}')
        if (config.get("exitWhenFail", False) == True) and not success:
            exit(1)
        if config.get("messagePush", {}).get("enabled", False):
            message = composeMessage(all_logs)
            pushMessage(message)
