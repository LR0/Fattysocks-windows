import logging
import yaml
import hashlib
from constants import CONFIG_FILE, USERS_FILE

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
