import os
import logging
from dotenv import load_dotenv

# Load local environment configuration
load_dotenv()

from telegram.ext import Application
from handlers.router import register_routes

# Configure logging
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO
)
logger = logging.getLogger(__name__)


def main():
    token = os.environ.get("TELEGRAM_TOKEN")
    if not token:
        raise ValueError("TELEGRAM_TOKEN environment variable is missing.")

    # Build Application
    app = Application.builder().token(token).build()

    # Register handlers via router
    register_routes(app)

    logger.info("DocMaster Bot successfully initialized and listening for updates...")
    app.run_polling(drop_pending_updates=True)


if __name__ == "__main__":
    main()
