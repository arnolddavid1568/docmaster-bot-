from telegram import Update
from telegram.ext import ContextTypes


async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Sends the welcome menu and command instructions."""
    welcome_text = (
        "📄 **Welcome to DocMaster Bot!**\n\n"
        "Send me files to trigger automated workflows:\n"
        "• **PDF Text Extraction:** Upload any digital PDF\n"
        "• **OCR Extraction:** Upload a scanned document/image with `/ocr` in the caption\n"
        "• **Image to PDF:** Send JPG or PNG images\n\n"
        "**Available Commands:**\n"
        "/start - Display main menu\n"
        "/cancel - Reset temporary processing queue\n"
        "/admin - Admin statistics (Admin restricted)"
    )
    await update.message.reply_text(welcome_text, parse_mode="Markdown")


async def cancel_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Resets user-level state and clears current actions."""
    context.user_data.clear()
    await update.message.reply_text("🧹 Processing queue reset successfully.")
