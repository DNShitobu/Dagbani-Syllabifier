from flask import Flask, request, render_template
from syllabifier import syllabify, to_ipa

app = Flask(__name__)

@app.route('/', methods=['GET', 'POST'])
def index():
    result = {}
    input_text = ""
    if request.method == 'POST':
        input_text = request.form['text']
        words = input_text.strip().split()
        result = {word: (syllabify(word), to_ipa(syllabify(word))) for word in words}
    return render_template('index.html', result=result, text=input_text)

if __name__ == '__main__':
    app.run(debug=True)
