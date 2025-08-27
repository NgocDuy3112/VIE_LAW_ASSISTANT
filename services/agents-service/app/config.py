from dotenv import load_dotenv
import os


load_dotenv("/src/configs/.env", override=True)


WEB_CRAWLER_SERVICE_URL = os.getenv("WEB_CRAWLER_SERVICE_URL")
TIMEOUT = int(os.getenv("TIMEOUT", 300))
LIMIT = int(os.getenv("LIMIT", 3))