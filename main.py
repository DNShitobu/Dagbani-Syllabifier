from flask import Flask, render_template, request, jsonify, send_file
import pandas as pd
import os
import io
from syllabifier.processor import process_text
from syllabifier.utils import handle_uploaded_file, handle_google_sheet

app = Flask(__name__)

@app.route('/', methods=['GET', 'POST'])
def index():
    result = {}
    text = ""
    word_by_word = False

    if request.method == 'POST':
        text = request.form.get('text', '').strip()
        word_by_word = request.form.get('word_by_word') == 'on'
        file = request.files.get('file')
        sheet_url = request.form.get('sheet_url')

        if file:
            ext = os.path.splitext(file.filename)[1]
            try:
                df = handle_uploaded_file(file, ext, column_name="Text", word_by_word=word_by_word)
                result = {row['Text']: (row['Syllabified'], row['IPA']) for _, row in df.iterrows()}
            except Exception as e:
                return jsonify({"error": str(e)}), 400

        elif sheet_url:
            try:
                df = handle_google_sheet(sheet_url, 'credentials.json', column_name="Text", word_by_word=word_by_word)
                result = {row['Text']: (row['Syllabified'], row['IPA']) for _, row in df.iterrows()}
            except Exception as e:
                return jsonify({"error": str(e)}), 400

        elif text:
            result = process_text(text, word_by_word)
            if not word_by_word:
                result = {text: result['sentence']}

    return render_template('index.html', result=result, text=text)


@app.route('/download')
def download():
    # Sample CSV creation for download functionality
    data = [
        ['Word', 'Syllabified', 'IPA'],
        ['sample', 'sam.ple', 'sam.plɛ']
    ]
    df = pd.DataFrame(data[1:], columns=data[0])
    output = io.StringIO()
    df.to_csv(output, index=False)
    output.seek(0)

    return send_file(io.BytesIO(output.getvalue().encode()),
                     mimetype='text/csv',
                     as_attachment=True,
                     download_name='syllabified_output.csv')


if __name__ == "__main__":
    app.run(debug=True)
