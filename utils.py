import logging
import yaml
import hashlib
from constants import CONFIG_FILE, USERS_FILE, TRAFFIC_FILE

logging.basicConfig(level=logging.INFO, format='[%(asctime)s] %(message)s')
LOGGER = logging.getLogger()

def load_config():
    try:
        config = yaml.load(open(CONFIG_FILE))
        return config
    except Exception:
        LOGGER.error('missing configuration.yaml or format incorrect')
        return None

def save_config(config):
    try:
        f = open(CONFIG_FILE, 'w+')
        yaml.dump(config, f)
        return True
    except Exception:
        LOGGER.error('error writing configuration')
        return False

def load_tokens():
    try:
        users = yaml.load(open(USERS_FILE))['users']
        tokens = []
        for item in users:
            token = hashlib.sha1(item.encode('utf-8')).digest()
            tokens.append(token)
        return tokens
    except Exception:
        LOGGER.error('missing users.yaml or format incorrect')
        return None

def save_traffic(traffic_map):
    traffic = {}
    try:
        traffic = yaml.load(open(TRAFFIC_FILE))
    except Exception:
        pass

    user_list = None
    try:
        user_list = yaml.load(open(USERS_FILE))['users']
    except Exception:
        return False

    user_map = {}
    for item in user_list:
        key = hashlib.sha1(item.encode('utf-8')).digest()
        user_map[key] = item

    for key in traffic_map:
        if user_map[key] not in traffic:
            traffic[user_map[key]] = 0
        traffic[user_map[key]] += traffic_map[key]

    try:
        f = open(TRAFFIC_FILE, 'w+')
        yaml.dump(traffic, f)
        return True
    except Exception:
        LOGGER.error('error writing traffic')
        return False
