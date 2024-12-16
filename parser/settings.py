import os
from dotenv import load_dotenv
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
load_dotenv()

#Basic settings
TARGET_URL = os.getenv('TARGET_URL')
TIMEOUT = int(os.getenv('TIMEOUT'))
DELAY = int(os.getenv('DELAY'))
MAX_RETRIES = int(os.getenv('MAX_RETRIES'))
MAX_WORKERS = int(os.getenv('MAX_WORKERS'))

#Chrome settings
USER_AGENT = os.getenv('USER_AGENT')

#Database settings
DB_PATH = BASE_DIR / os.getenv('DB_PATH')

#Proxy testing script
PATH_TO_VALID_PROXIES = BASE_DIR / os.getenv('PATH_TO_VALID_PROXIES')
UPDATE_PROXIES = os.getenv('UPDATE_PROXIES',False)
TEST_IP_URL = os.getenv('TEST_IP_URL','https://atomurl.net/myip/')

print(PATH_TO_VALID_PROXIES)
