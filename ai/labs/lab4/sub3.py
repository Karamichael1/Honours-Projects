import re
import os
import math
from collections import Counter, defaultdict

def clean_words(text):
    cleaned_words = re.sub(r'[^a-zA-Z\s]', '', text.lower()).split()
    return cleaned_words

def get_bow(filename):
    try:
        script_dir = os.path.dirname(os.path.abspath(__file__))
        file_path = os.path.join(script_dir, filename)
        with open(file_path, 'r', encoding='utf-8') as file:
            file.readline()  # Skip the heading line
            text = file.read()
        word_counts = Counter(clean_words(text))
        total_words = sum(word_counts.values())
        bow_model = defaultdict(lambda: 0)
        for word, count in word_counts.items():
            bow_model[word] = count / total_words
        return bow_model, filename
    except FileNotFoundError:
        return "File not found."

def classify_sentence(sentence, bow_models):
    sentence_words = clean_words(sentence)
    play_scores = {}
    for heading, (bow_model, _) in bow_models.items():
        score = 0
        for word in sentence_words:
            score += math.log(bow_model[word]) if word in bow_model else math.log(1e-10) 
        play_scores[heading] = score
    most_likely_play = max(play_scores, key=play_scores.get)
    return most_likely_play

def find_best_class(words: list):
    for word in words:
        if word in file_names:
            return file_names[word]
    return None

text_files = {}
script_dir = os.path.dirname(os.path.abspath(__file__))
for file_name in os.listdir(script_dir):
    if file_name.endswith('.txt'):
        text_files[file_name] = file_name

file_names = {
    "ado.txt": "Much Ado About Nothing",
    "lear.txt": "King Lear",
    "merchant.txt": "The Merchant of Venice",
    "othello.txt": "Othello",
    "tempest.txt": "The Tempest",
    "hamlet.txt": "Hamlet",
    "macbeth.txt": "Macbeth",
    "midsummer.txt": "Midsummer Night's Dream",
    "romeo.txt": "Romeo and Juliet",
    "twelfth.txt": "Twelfth Night",
}

bow_models = {}
for file_name in text_files.values():
    bow_model, heading = get_bow(file_name)
    if bow_model != "File not found.":
        bow_models[file_name] = (bow_model, file_name)

sentence = input()
words = clean_words(sentence)
best_class = find_best_class(words)

if best_class:
    print(best_class)
else:
    most_likely_play = classify_sentence(sentence, bow_models)
    play_name = file_names.get(most_likely_play, most_likely_play.title())
    print(play_name)