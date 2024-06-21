import os
import string
import pymupdf
import matplotlib.pyplot as plt
from flask import Flask, request, render_template, redirect, url_for
from werkzeug.utils import secure_filename
import io
import base64

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'uploads'
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

# Define function to extract text from PDF
def extract_text_from_pdf(file_path):
    doc = pymupdf.open(file_path)
    text = ""
    for page_num in range(doc.page_count):
        page = doc.load_page(page_num)
        text += page.get_text()
    return text

# Define function to process text
def process_text(text, ignored_characters, min_word_length=3, top_n=20, remove_stop_words=False):
    freq_words = {}
    words_count = 0
    sentence_count = 0
    total_word_length = 0
    stop_words = set()

    # Load stop words if required
    if remove_stop_words:
        with open('stop_words.txt', 'rt', encoding='utf8') as sw_file:
            stop_words = set(sw_file.read().split())

    lines = text.split('\n')
    for line in lines:
        # Ignore empty lines
        formatted_text = line.strip()
        if not formatted_text:
            continue

        sentence_count += formatted_text.count('.') + formatted_text.count('!') + formatted_text.count('?')

        # Remove ignored characters
        for char in ignored_characters:
            formatted_text = formatted_text.replace(char, '')

        # Split into words and sentences
        all_words = formatted_text.split()
        words_count += len(all_words)
        total_word_length += sum(len(word) for word in all_words)

        # Update word frequency dictionary
        for word in all_words:
            word = word.lower()
            if len(word) < min_word_length or word in stop_words:
                continue
            if word in freq_words:
                freq_words[word] += 1
            else:
                freq_words[word] = 1

    # Calculate additional statistics
    unique_words_count = len(freq_words)
    average_word_length = total_word_length / words_count if words_count else 0
    average_sentence_length = words_count / sentence_count if sentence_count else 0

    # Sort word frequencies and get top N words
    sorted_freq_words = dict(sorted(freq_words.items(), key=lambda item: item[1], reverse=True))
    top_words = list(sorted_freq_words.items())[:top_n]

    # Generate results as HTML
    results = f'''
    <p>Total words: {words_count}</p>
    <p>Unique words: {unique_words_count}</p>
    <p>Average word length: {average_word_length:.2f}</p>
    <p>Sentence count: {sentence_count}</p>
    <p>Average sentence length: {average_sentence_length:.2f} words</p>
    <p>Top {top_n} words:</p>
    <ul>
    '''
    for word, freq in top_words:
        results += f'<li>{word}: {freq}</li>'
    results += '</ul>'

    # Plot top N words and save to a bytes object
    img = io.BytesIO()
    plot_top_words(top_words, img)
    img.seek(0)
    chart_url = base64.b64encode(img.getvalue()).decode()

    return results, f"data:image/png;base64,{chart_url}"

# Define function to plot top words
def plot_top_words(top_words, img):
    words, frequencies = zip(*top_words)
    plt.figure(figsize=(12, 8))
    plt.bar(words, frequencies, color='blue')
    plt.xlabel('Words')
    plt.ylabel('Frequencies')
    plt.title('Top N Frequent Words')
    plt.xticks(rotation=45, ha='right')
    plt.tight_layout()
    plt.savefig(img, format='png')
    plt.close()

# Route to handle file upload and analysis
@app.route('/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        return redirect(request.url)
    file = request.files['file']
    if file.filename == '':
        return redirect(request.url)
    
    top_n = int(request.form['top_n'])
    min_word_length = int(request.form['min_word_length'])

    if file and (file.filename.endswith('.txt') or file.filename.endswith('.pdf')):
        filename = secure_filename(file.filename)
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(file_path)

        if filename.endswith('.pdf'):
            text = extract_text_from_pdf(file_path)
        else:
            with open(file_path, 'rt', encoding='utf8') as f:
                text = f.read()

        results, chart_url = process_text(text, string.punctuation, min_word_length, top_n, remove_stop_words=False)
        return render_template('index.html', results=results, chart_url=chart_url)

    return redirect(request.url)

# Route to render the upload form
@app.route('/')
def index():
    return render_template('index.html', results="", chart_url="")

if __name__ == '__main__':
    # app.run(debug=True)
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 5000)))
