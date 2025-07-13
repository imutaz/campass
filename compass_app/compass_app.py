from flask import Flask, render_template, request
import os

app = Flask(__name__)

# Folder to store uploaded files
UPLOAD_FOLDER = 'uploads'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

@app.route('/')
def home():
    return render_template('home.html')

@app.route('/upload-file', methods=['POST'])
def upload_file():
    file = request.files.get('icsfile')
    if file:
        filepath = os.path.join(UPLOAD_FOLDER, file.filename)
        file.save(filepath)
        return f"<p>✅ File '{file.filename}' uploaded and saved!</p><a href='/'>Back to Home</a>"
    return "<p>❌ No file uploaded.</p><a href='/'>Back</a>"

if __name__ == '__main__':
    app.run(debug=True)
