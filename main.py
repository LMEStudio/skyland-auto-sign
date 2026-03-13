import time
import logging

from utils.skyland import start
from utils.logger import config_logger
from utils.config import get_config
from utils.push import pushMessage, composeMessage

config = get_config()

if __name__ == '__main__':
    config_logger(level=logging.INFO)
    start_time = time.time()
    success, all_logs = start()
    end_time = time.time()
    logging.info(f'complete within {(end_time - start_time) * 1000} ms')
    logging.info(f'exit_when_fail_env: {config.get("exitWhenFail", False)}, success: {success}')
    if (config.get("exitWhenFail", False) == True) and not success:
        exit(1)
    if config.get("messagePush", {}).get("enabled", False):
        message = composeMessage(all_logs)
        pushMessage(message)