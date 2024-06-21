import string
import pymupdf
import matplotlib.pyplot as plt

# Define function to extract text from PDF
def extract_text_from_pdf(file_path):
    doc = pymupdf.open(file_path)
    text = ""
    for page_num in range(doc.page_count):
        page = doc.load_page(page_num)
        text += page.get_text()
    return text

# Define function to process text
def process_text(text, ignored_characters, min_word_length=3, top_n=100, remove_stop_words=False):
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

        # Remove ignored characters
        for char in ignored_characters:
            formatted_text = formatted_text.replace(char, '')

        # Split into words and sentences
        all_words = formatted_text.split()
        words_count += len(all_words)
        total_word_length += sum(len(word) for word in all_words)
        sentence_count += formatted_text.count('.') + formatted_text.count('!') + formatted_text.count('?')

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

    # Print statistics
    print(f'Total words: {words_count}')
    print(f'Unique words: {unique_words_count}')
    print(f'Average word length: {average_word_length:.2f}')
    print(f'Sentence count: {sentence_count}')
    print(f'Average sentence length: {average_sentence_length:.2f} words')
    print(f'Top {top_n} words:')
    for word, freq in top_words:
        print(f'{word}: {freq}')

    # Plot top N words
    plot_top_words(top_words)

# Define function to plot top words
def plot_top_words(top_words):
    words, frequencies = zip(*top_words)
    plt.figure(figsize=(12, 8))
    plt.bar(words, frequencies, color='blue')
    plt.xlabel('Words')
    plt.ylabel('Frequencies')
    plt.title('Top N Frequent Words')
    plt.xticks(rotation=45, ha='right')
    plt.tight_layout()
    plt.show()

# Main function to handle both text and PDF files
def analyze_file(file_path, ignored_characters, min_word_length, top_n=100, remove_stop_words=False):
    if file_path.lower().endswith('.pdf'):
        text = extract_text_from_pdf(file_path)
    else:
        with open(file_path, 'rt', encoding='utf8') as file:
            text = file.read()
    process_text(text, ignored_characters, min_word_length, top_n=top_n, remove_stop_words=remove_stop_words)

# Define ignored characters and call the function
IGNORED_CHARACTERS = string.punctuation
file_path = 'You Dont Know JS - 1st Edition.pdf'  # Replace with your file path
analyze_file(file_path, IGNORED_CHARACTERS, min_word_length=6, top_n=20, remove_stop_words=False)
