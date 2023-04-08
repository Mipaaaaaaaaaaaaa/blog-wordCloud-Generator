import time

BASE_URL = "https://magicmipamipa.zeabur.app/"
ARCHIVE_URL = BASE_URL + "archive/"
ARTICLE_URL = BASE_URL + "article/"
TARGET_IMG_PATH = "targetCloud-" + time.strftime("%Y-%m-%d", time.localtime()) +".png"
FRONT_PATH = "/font/汉仪粗黑简.ttf"
TEXT_PATH = "constitution.txt"
IMAGE_UPLOAD_URL = "" #你的图床地址
NOTION_TOKEN = "" #你的notion token
PAGE_CODE = "" #你的notion page code