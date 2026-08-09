import os
import logging
import tempfile
import asyncio
from typing import List

from telegram import Update
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    ContextTypes,
    filters,
)

from pypdf import PdfWriter, PdfReader
from pdf2image import convert_from_path
import pytesseract
from PIL import Image
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter

# Logging configuration
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)
logger = logging.getLogger(__name__)

# Retrieve Telegram Bot Token from Environment Variables
TELEGRAM_TOKEN = os.environ.get("TELEGRAM_TOKEN")


async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Initial onboarding response."""
    await update.message.reply_text(
        "👋 Welcome to **DocMaster Bot**!\n\n"
        "Send or forward me files to perform document operations:\n"
        "• Send multiple PDFs to **Merge**\n"
        "• Send images (JPG/PNG) to convert **Images → PDF**\n"
        "• Send a PDF with `/ocr` in the caption to perform **OCR Text Extraction**\n"
        "• Send a PDF to **Extract Text** or inspect metadata.\n\n"
        "Commands:\n"
        "/start - Show welcome message\n"
        "/cancel - Clear current temporary processing queue",
        parse_mode="Markdown"
    )


async def cancel_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Clear user context state."""
    context.user_data.clear()
    await update.message.reply_text("🧹 Processing queue reset.")


async def handle_document(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Processes incoming PDF and document files."""
    doc = update.message.document
    file_name = doc.file_name or "document.pdf"
    mime_type = doc.mime_type or ""
    caption = update.message.caption or ""

    status_msg = await update.message.reply_text("📥 Downloading file...")

    with tempfile.TemporaryDirectory() as temp_dir:
        input_path = os.path.join(temp_dir, file_name)
        telegram_file = await context.bot.get_file(doc.file_id)
        await telegram_file.download_to_drive(input_path)

        # 1. OCR scanned documents
        if "/ocr" in caption.lower() or "ocr" in caption.lower():
            await status_msg.edit_text("🔍 Running OCR scanning on document...")
            try:
                images = convert_from_path(input_path)
                extracted_text = ""
                for i, img in enumerate(images):
                    text = pytesseract.image_to_string(img)
                    extracted_text += f"--- Page {i+1} ---\n{text}\n\n"

                txt_path = os.path.join(temp_dir, "ocr_output.txt")
                with open(txt_path, "w", encoding="utf-8") as f:
                    f.write(extracted_text)

                await status_msg.edit_text("📤 Uploading OCR results...")
                await update.message.reply_document(
                    document=open(txt_path, "rb"),
                    caption="✅ OCR extraction complete."
                )
            except Exception as e:
                logger.error(f"OCR Error: {e}")
                await status_msg.edit_text("❌ OCR processing failed. Ensure document contains readable images.")
            return

        # 2. Extract Text from PDF
        if mime_type == "application/pdf":
            await status_msg.edit_text("⚙️ Reading PDF content...")
            try:
                reader = PdfReader(input_path)
                extracted_text = ""
                for idx, page in enumerate(reader.pages):
                    extracted_text += f"--- Page {idx+1} ---\n" + (page.extract_text() or "") + "\n\n"

                txt_path = os.path.join(temp_dir, f"{os.path.splitext(file_name)[0]}_text.txt")
                with open(txt_path, "w", encoding="utf-8") as f:
                    f.write(extracted_text if extracted_text.strip() else "No readable text found.")

                await status_msg.edit_text("📤 Uploading extracted text...")
                await update.message.reply_document(
                    document=open(txt_path, "rb"),
                    caption=f"📄 Page Count: {len(reader.pages)} | Size: {round(doc.file_size / 1024, 2)} KB"
                )
            except Exception as e:
                logger.error(f"PDF Error: {e}")
                await status_msg.edit_text("❌ Error processing PDF file.")


async def handle_photo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Converts uploaded photo/images to PDF."""
    status_msg = await update.message.reply_text("📷 Converting image to PDF...")
    photo = update.message.photo[-1]  # Highest resolution

    with tempfile.TemporaryDirectory() as temp_dir:
        img_path = os.path.join(temp_dir, "input.jpg")
        pdf_path = os.path.join(temp_dir, "converted.pdf")

        telegram_file = await context.bot.get_file(photo.file_id)
        await telegram_file.download_to_drive(img_path)

        image = Image.open(img_path)
        if image.mode != "RGB":
            image = image.convert("RGB")
        image.save(pdf_path, "PDF", resolution=100.0)

        await status_msg.edit_text("📤 Uploading PDF...")
        await update.message.reply_document(
            document=open(pdf_path, "rb"),
            filename="Image_Converted.pdf",
            caption="✅ Image successfully converted to PDF."
        )


def main():
    if not TELEGRAM_TOKEN:
        raise ValueError("TELEGRAM_TOKEN environment variable is missing.")

    # Initialize Telegram Bot Application
    app = Application.builder().token(TELEGRAM_TOKEN).build()

    # Register Handlers
    app.add_handler(CommandHandler("start", start_command))
    app.add_handler(CommandHandler("cancel", cancel_command))
    app.add_handler(MessageHandler(filters.Document.ALL, handle_document))
    app.add_handler(MessageHandler(filters.PHOTO, handle_photo))

    logger.info("DocMaster Bot starting polling...")
    app.run_polling(drop_pending_updates=True)


if __name__ == "__main__":
    main()
