# OCR + AI Flask App

This is a Flask web application that:
1. Uploads an image (PNG, JPG, JPEG, BMP, TIFF).
2. Extracts text using Tesseract OCR.
3. Processes the text using OpenAI GPT for tasks like:
   - Summarization
   - Question answering
   - Grammar correction
4. Provides both raw OCR output and AI-processed text.
5. Saves AI results into a `.txt` file for download.

---

## Features
- Upload image files for OCR
- Choose language for OCR (`eng` default)
- Select AI task: summarize, question, correct
- View extracted text and AI-enhanced output
- Download AI-processed results as `.txt`
- Simple web interface with Flask

---

## Project Structure
