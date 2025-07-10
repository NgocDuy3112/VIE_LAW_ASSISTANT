import logging


# Configure the global logger only once
logging.basicConfig(
    level=logging.INFO,  # or DEBUG for dev
    format="%(asctime)s | %(name)s | %(levelname)s | %(message)s"
)

# Export a single shared logger
logger = logging.getLogger("rag-backend")  # your service name