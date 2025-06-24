# processor.py — handles sentence/word processing logic
from .core import syllabify, to_ipa

def process_text(text, word_by_word=False):
    words = text.split()
    result = {}

    if word_by_word:
        for word in words:
            syll = syllabify(word)
            ipa = to_ipa(syll)
            result[word] = (syll, ipa)
        return result
    else:
        syll_list = []
        ipa_list = []
        for word in words:
            s = syllabify(word)
            i = to_ipa(s)
            syll_list.append(s)
            ipa_list.append(i)
        return {'sentence': (" ".join(syll_list), " ".join(ipa_list))}

