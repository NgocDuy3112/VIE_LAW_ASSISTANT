from dotenv import load_dotenv
import os


load_dotenv("/src/configs/.env", override=True)


LEGAL_LAW_URL = os.getenv("LEGAL_LAW_URL")