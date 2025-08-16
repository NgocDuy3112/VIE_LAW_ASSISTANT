from dotenv import load_dotenv
import os


load_dotenv("/src/configs/.env", override=True)



LEGAL_LAW_URL = os.getenv("LEGAL_LAW_URL", 'https://vanban.chinhphu.vn/he-thong-van-ban')
TIMEOUT = int(os.getenv("TIMEOUT", 300))
LIMIT = int(os.getenv("LIMIT", 3))