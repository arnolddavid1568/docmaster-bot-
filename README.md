# 📄 DocMaster Bot

DocMaster Bot is a full-featured Telegram bot for document processing, PDF manipulation, and OCR text extraction. Built with Python and containerized with Docker, it runs seamlessly on cloud platforms like **Railway**.

---

## ✨ Features

- **📄 Text Extraction:** Extract plain text directly from digital PDFs.
- **🔍 OCR Processing:** Extract editable text from scanned documents and images using Tesseract OCR (trigger by typing `/ocr` in the caption).
- **📷 Image to PDF:** Instantly convert photos (JPG, PNG) into PDF documents.
- **🧹 Auto-Cleanup:** All processing occurs in temporary directories that clear automatically after execution to ensure user data privacy.

---

## 🛠️ Project Structure

```text
docmaster-bot/
├── main.py            # Core Telegram bot application logic
├── requirements.txt    # Python dependency specifications
├── Dockerfile          # Container setup with OCR & PDF system packages
├── .gitignore          # File exclusions for Git
└── README.md           # Project documentation
