from dotenv import load_dotenv
import os


load_dotenv("/src/configs/.env", override=True)

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
BASE_URL = os.getenv("BASE_URL")
MODEL_NAME = os.getenv("MODEL_NAME")


LEGAL_LAW_URL = os.getenv("LEGAL_LAW_URL", 'https://vanban.chinhphu.vn/he-thong-van-ban')
TIMEOUT = int(os.getenv("TIMEOUT", 300))
LIMIT = int(os.getenv("LIMIT", 3))

WEB_CRAWLER_URL = os.getenv("WEB_CRAWLER_URL")