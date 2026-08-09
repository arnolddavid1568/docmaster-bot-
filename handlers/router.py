from telegram.ext import Application, CommandHandler, MessageHandler, filters
from handlers.menu import start_command, cancel_command
from handlers.admin import admin_command
from handlers.instant_tools import process_document, process_photo


def register_routes(app: Application):
    """Binds all command and message handlers to the application instance."""
    app.add_handler(CommandHandler("start", start_command))
    app.add_handler(CommandHandler("cancel", cancel_command))
    app.add_handler(CommandHandler("admin", admin_command))

    app.add_handler(MessageHandler(filters.Document.ALL, process_document))
    app.add_handler(MessageHandler(filters.PHOTO, process_photo))
