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
            heading = file.readline().strip()  
            text = file.read()
        word_counts = Counter(clean_words(text))
        total_words = sum(word_counts.values())
        bow_model = defaultdict(lambda: 0)
        for word, count in word_counts.items():
            bow_model[word] = count / total_words
        return bow_model, heading
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

text_files = {}
script_dir = os.path.dirname(os.path.abspath(__file__))
for file_name in os.listdir(script_dir):
    if file_name.endswith('.txt'):
        text_files[file_name] = file_name

bow_models = {}
for file_name in text_files.values():
    bow_model, heading = get_bow(file_name)
    bow_models[heading] = (bow_model, heading)

sentence = input()
most_likely_play = classify_sentence(sentence, bow_models)
most_likely_play = most_likely_play.title()
print(most_likely_play)    