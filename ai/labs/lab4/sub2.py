import re
from collections import Counter

def clean_words(text):
    cleaned_words = re.sub(r'[^a-zA-Z ]', '', text.lower()).split()
    return ' '.join(cleaned_words)

def get_top_words(filename):
    try:
        with open(filename, 'r', encoding='utf-8') as file:
            text = file.read()
        word_counts = Counter(clean_words(text).split())
        top_words = sorted(word_counts.items(), key=lambda x: x[1], reverse=True)[:3]
        return ' '.join([word for word, _ in top_words])
    except FileNotFoundError:
        return "File not found."

if __name__ == "__main__":
    filename = input()
    print(get_top_words(filename))