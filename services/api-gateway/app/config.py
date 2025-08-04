from dotenv import load_dotenv
import os


load_dotenv("/src/configs/.env", override=True)


DOCUMENT_SERVICE_URL = os.getenv("DOCUMENT_SERVICE_URL")
LLM_SERVICE_URL = os.getenv("LLM_SERVICE_URL")