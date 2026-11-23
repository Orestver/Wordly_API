import random
from models import Word

def get_options(words: list[Word], current_word: Word, is_reversed: bool, quantity: int = 3):

    translations = [word.translation for word in words if word != current_word]
    original_words = [word.original_word for word in words if word != current_word]
    random.shuffle(translations)
    random.shuffle(original_words)
    if is_reversed:
        options = original_words[0:quantity]
        options.append(current_word.original_word)
        random.shuffle(options)
        return options
    else:
        options = translations[0:quantity]
        options.append(current_word.translation)
        random.shuffle(options)
        return options

