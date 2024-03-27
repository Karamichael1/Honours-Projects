import re

def clean_words(text):
    cleaned_words = re.sub(r'[^a-zA-Z ]', '', text.lower()).split()
    return ' '.join(cleaned_words)

if __name__ == "__main__":
    user_input = input()
    print(clean_words(user_input))