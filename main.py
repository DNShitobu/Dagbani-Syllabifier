from flask import Flask, render_template, request, jsonify, send_file
import pandas as pd
import os
import io
from syllabifier import process_text

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html', text="", result=None)

@app.route('/upload', methods=['POST'])
def upload_file():
    # Check if a text input is provided
    if 'text' in request.form and request.form['text'].strip():
        text = request.form['text'].strip()
        word_by_word = 'word_by_word' in request.form

        result = process_text(text, word_by_word=word_by_word)
        return render_template('index.html', text=text, result=result)

    # If file upload is used instead
    if 'file' not in request.files:
        return jsonify({"error": "No file uploaded"}), 400

    file = request.files['file']
    word_by_word = request.form.get('word_by_word') == 'true'
    filename = file.filename
    ext = os.path.splitext(filename)[1]

    if ext == '.csv':
        df = pd.read_csv(file)
    elif ext in ['.xls', '.xlsx']:
        df = pd.read_excel(file)
    else:
        return jsonify({"error": "Unsupported file format"}), 400

    results = []
    for text in df['DagbaniText'].dropna():
        output = process_text(str(text), word_by_word)
        if word_by_word:
            syll = "; ".join(f"{k} = {v[0]}" for k, v in output.items())
            ipa = "; ".join(f"{k} = {v[1]}" for k, v in output.items())
        else:
            syll, ipa = output['sentence']
        results.append({
            "original": text,
            "syllables": syll,
            "ipa": ipa
        })

    # Save to CSV in memory
    df_out = pd.DataFrame(results)
    buffer = io.StringIO()
    df_out.to_csv(buffer, index=False)
    buffer.seek(0)

    return send_file(
        io.BytesIO(buffer.getvalue().encode()),
        mimetype='text/csv',
        as_attachment=True,
        download_name='syllabified_output.csv'
    )

@app.route('/download')
def download_csv():
    # Fallback route — you can make this more dynamic if needed
    return "Download handler placeholder."

if __name__ == "__main__":
    app.run(debug=True)
