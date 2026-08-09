import os
import tempfile
import logging
from telegram import Update
from telegram.ext import ContextTypes
from pypdf import PdfReader
from pdf2image import convert_from_path
import pytesseract
from PIL import Image

logger = logging.getLogger(__name__)


async def process_document(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handles incoming PDF documents for text extraction and OCR processing."""
    doc = update.message.document
    file_name = doc.file_name or "document.pdf"
    mime_type = doc.mime_type or ""
    caption = update.message.caption or ""

    status_msg = await update.message.reply_text("📥 Downloading file...")

    with tempfile.TemporaryDirectory() as temp_dir:
        input_path = os.path.join(temp_dir, file_name)
        telegram_file = await context.bot.get_file(doc.file_id)
        await telegram_file.download_to_drive(input_path)

        # 1. OCR Scanned Documents
        if "/ocr" in caption.lower() or "ocr" in caption.lower():
            await status_msg.edit_text("🔍 Running OCR scanning on document...")
            try:
                images = convert_from_path(input_path)
                extracted_text = ""
                for idx, img in enumerate(images):
                    text = pytesseract.image_to_string(img)
                    extracted_text += f"--- Page {idx + 1} ---\n{text}\n\n"

                output_path = os.path.join(temp_dir, "ocr_extracted.txt")
                with open(output_path, "w", encoding="utf-8") as f:
                    f.write(extracted_text if extracted_text.strip() else "No OCR text detected.")

                await status_msg.edit_text("📤 Uploading OCR results...")
                await update.message.reply_document(
                    document=open(output_path, "rb"),
                    caption="✅ OCR extraction completed."
                )
            except Exception as e:
                logger.error(f"OCR Error: {e}")
                await status_msg.edit_text("❌ OCR processing failed.")
            return

        # 2. Extract Text from PDF
        if mime_type == "application/pdf":
            await status_msg.edit_text("⚙️ Reading PDF content...")
            try:
                reader = PdfReader(input_path)
                extracted_text = ""
                for idx, page in enumerate(reader.pages):
                    extracted_text += f"--- Page {idx + 1} ---\n" + (page.extract_text() or "") + "\n\n"

                txt_path = os.path.join(temp_dir, f"{os.path.splitext(file_name)[0]}_text.txt")
                with open(txt_path, "w", encoding="utf-8") as f:
                    f.write(extracted_text if extracted_text.strip() else "No readable text found.")

                await status_msg.edit_text("📤 Uploading extracted text...")
                await update.message.reply_document(
                    document=open(txt_path, "rb"),
                    caption=f"📄 Total Pages: {len(reader.pages)}"
                )
            except Exception as e:
                logger.error(f"PDF Error: {e}")
                await status_msg.edit_text("❌ Error processing PDF file.")


async def process_photo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Converts uploaded photo/images directly into a PDF."""
    status_msg = await update.message.reply_text("📷 Converting image to PDF...")
    photo = update.message.photo[-1]  # Fetch highest resolution

    with tempfile.TemporaryDirectory() as temp_dir:
        img_path = os.path.join(temp_dir, "input.jpg")
        pdf_path = os.path.join(temp_dir, "converted.pdf")

        telegram_file = await context.bot.get_file(photo.file_id)
        await telegram_file.download_to_drive(img_path)

        image = Image.open(img_path)
        if image.mode != "RGB":
            image = image.convert("RGB")
        image.save(pdf_path, "PDF", resolution=100.0)

        await status_msg.edit_text("📤 Uploading converted PDF...")
        await update.message.reply_document(
            document=open(pdf_path, "rb"),
            filename="Image_Converted.pdf",
            caption="✅ Image successfully converted to PDF."
        )
