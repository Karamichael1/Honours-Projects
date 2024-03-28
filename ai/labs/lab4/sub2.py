import re
import os
from collections import Counter

def clean_words(text):
    cleaned_words = re.sub(r'[^a-zA-Z\s]', '', text.lower()).split()
    return cleaned_words

def get_top_words(filename):
    try:
        script_dir = os.path.dirname(os.path.abspath(__file__))
        file_path = os.path.join(script_dir, filename)
        with open(file_path, 'r', encoding='utf-8') as file:
            text = file.read()
        word_counts = Counter(clean_words(text))
        sorted_words = sorted(word_counts.items(), key=lambda x: (-x[1], x[0]))
        top_words = sorted_words[:3]
        return ' '.join([word for word, _ in top_words])
    except FileNotFoundError:
        return "File not found."

if __name__ == "__main__":
    filename = input().strip()
    print(get_top_words(filename))
