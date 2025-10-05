import os
import pytesseract
from flask import Flask, request, render_template, url_for, send_from_directory
from werkzeug.utils import secure_filename
from PIL import Image
from datetime import datetime
import openai

app = Flask(__name__)

UPLOAD_FOLDER = "uploads"
OUTPUT_FOLDER = "static/outputs"
ALLOWED_EXTENSIONS = {"png", "jpg", "jpeg", "bmp", "tiff"}

app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER
app.config["OUTPUT_FOLDER"] = OUTPUT_FOLDER

os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(OUTPUT_FOLDER, exist_ok=True)

pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"

openai.api_key = os.getenv("my_key")

def allowed_file(filename):
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS

def ai_process_text(extracted_text, task="summarize"):
    if task == "summarize":
        prompt = f"Summarize the following text breifly and concisely:\n\n{extracted_text}"
    elif task == "question":
        prompt = f"Answer the questions very breif and consisely based on the following text:\n\n{extracted_text}"
    elif task == "correct":
        prompt = f"Just Correct grammatical errors and improve clarity of the following text:\n\n{extracted_text}"
    else:
        prompt = extracted_text

    try:
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are a helpful AI assistant."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.5
        )
        return response['choices'][0]['message']['content']
    except Exception as e:
        return f"AI processing error: {e}"

@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        if "file" not in request.files:
            return render_template("index.html", error="No file uploaded")

        file = request.files["file"]
        language = request.form.get("language", "eng")
        ai_task = request.form.get("ai_task", "summarize")

        if file.filename == "":
            return render_template("index.html", error="No selected file")

        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            file_path = os.path.join(app.config["UPLOAD_FOLDER"], filename)
            file.save(file_path)

            img = Image.open(file_path)
            extracted_text = pytesseract.image_to_string(img, lang=language)

            ai_text = ai_process_text(extracted_text, task=ai_task)

            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            output_filename = f"ai_output_{timestamp}.txt"
            output_path = os.path.join(app.config["OUTPUT_FOLDER"], output_filename)
            with open(output_path, "w", encoding="utf-8") as f:
                f.write(ai_text)

            return render_template("result.html", 
                                   raw_text=extracted_text,
                                   ai_text=ai_text,
                                   image_url=url_for("uploaded_file", filename=filename),
                                   output_file=output_filename)

    return render_template("index.html")

@app.route("/uploads/<filename>")
def uploaded_file(filename):
    return send_from_directory(app.config["UPLOAD_FOLDER"], filename)

@app.route("/static/outputs/<filename>")
def download_output(filename):
    return send_from_directory(app.config["OUTPUT_FOLDER"], filename, as_attachment=True)

if __name__ == "__main__":
    app.run(debug=True)
