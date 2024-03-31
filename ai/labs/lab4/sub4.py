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
            file.readline() 
            text = file.read()
        word_counts = Counter(clean_words(text))
        total_words = sum(word_counts.values())
        bow_model = defaultdict(lambda: 0)
        for word, count in word_counts.items():
            bow_model[word] = count / total_words
        return bow_model, filename
    except FileNotFoundError:
        return "File not found."

def calculate_probability(sentence_words, bow_model):
    probability = 1
    for word in sentence_words:
        word_probability = bow_model[word] if word in bow_model else 1e-10  
        probability *= word_probability
    return probability

def classify_sentence(sentence, bow_models):
    sentence_words = clean_words(sentence)
    play_probabilities = {}
    denominator = 0
    for heading, (bow_model, _) in bow_models.items():
        numerator = calculate_probability(sentence_words, bow_model)
        play_probabilities[heading] = numerator
        denominator += numerator

    for heading in play_probabilities:
        play_probabilities[heading] /= denominator

    return play_probabilities

def log_sum_exp(values):
    max_value = max(values)
    return max_value + math.log(sum(math.exp(value - max_value) for value in values))

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
        bow_models[heading] = (bow_model, file_name)

sentence = input()
play_probabilities = classify_sentence(sentence, bow_models)

print("Probabilities:")
sorted_probabilities = sorted(play_probabilities.items(), key=lambda x: x[1], reverse=True)
for play, probability in sorted_probabilities:
    play_name = file_names.get(play, play.title())
    print(f"{play_name}: {round(probability * 100)}%")