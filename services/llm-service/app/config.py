from dotenv import load_dotenv
import os


load_dotenv("/src/configs/.env", override=True)


OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
BASE_URL = os.getenv("BASE_URL")
MODEL_NAME = os.getenv("MODEL_NAME")

NUM_REQUESTS_PER_MINUTE = int(os.getenv("NUM_REQUESTS_PER_MINUTE", 10))
REQUEST_TIMEOUT_SECONDS = int(os.getenv("REQUEST_TIMEOUT_SECONDS", 60))
RATE_LIMIT_URI = os.getenv("RATE_LIMIT_URI")