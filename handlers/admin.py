import os
from telegram import Update
from telegram.ext import ContextTypes


async def admin_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Admin endpoint for status verification."""
    admin_id = os.environ.get("ADMIN_USER_ID", "")
    user_id = str(update.effective_user.id)

    if admin_id and user_id != admin_id:
        await update.message.reply_text("⛔ Unauthorized access.")
        return

    await update.message.reply_text(
        "⚙️ **DocMaster Admin Panel**\n\n"
        "Status: Operational\n"
        "Engine: Python 3.10 / Telegram Bot API v20+",
        parse_mode="Markdown"
    )
