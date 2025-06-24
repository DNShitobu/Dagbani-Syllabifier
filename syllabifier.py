import re

# IPA Mappings for Dagbani phonemes
ipa_map = {
    "ny": "ɲ", "ŋ": "ŋ", "ch": "ʧ", "sh": "ʃ", "dz": "ʣ", "kp": "k͡p", "gb": "g͡b",
    "aa": "aː", "ee": "eː", "ii": "iː", "oo": "oː", "uu": "uː",
    "ɛɛ": "ɛː", "ɔɔ": "ɔː",
    "a": "a", "e": "e", "i": "i", "o": "o", "u": "u", "ɛ": "ɛ", "ɔ": "ɔ",
    "b": "b", "d": "d", "f": "f", "g": "g", "h": "h", "j": "ʤ",
    "k": "k", "l": "l", "m": "m", "n": "n", "p": "p", "r": "r",
    "s": "s", "t": "t", "v": "v", "w": "w", "y": "j", "z": "z"
}

# Core syllabification function
def syllabify(word):
    vowels = ['a', 'e', 'i', 'o', 'u', 'ɛ', 'ɔ']
    long_vowels = ['aa', 'ee', 'ii', 'oo', 'uu', 'ɛɛ', 'ɔɔ']
    digraphs = ['ny', 'ŋ', 'ch', 'sh', 'dz', 'kp', 'gb']

    i = 0
    units = []
    while i < len(word):
        # Handle long vowels
        matched = False
        for lv in sorted(long_vowels, key=len, reverse=True):
            if word[i:i+len(lv)] == lv:
                units.append(lv)
                i += len(lv)
                matched = True
                break
        if matched:
            continue

        # Handle digraphs
        for dg in sorted(digraphs, key=len, reverse=True):
            if word[i:i+len(dg)] == dg:
                units.append(dg)
                i += len(dg)
                matched = True
                break
        if matched:
            continue

        # Handle single characters
        units.append(word[i])
        i += 1

    # Syllable grouping: simplistic V or CV pattern
    syllables = []
    temp = ''
    for u in units:
        temp += u
        if any(v in u for v in vowels):
            syllables.append(temp)
            temp = ''
    if temp:
        syllables.append(temp)
    return '.'.join(syllables)

# IPA transcription function
def to_ipa(syll_string):
    result = []
    for syll in syll_string.split('.'):
        ipa = ''
        i = 0
        while i < len(syll):
            found = False
            for length in [3, 2, 1]:
                part = syll[i:i+length]
                if part in ipa_map:
                    ipa += ipa_map[part]
                    i += length
                    found = True
                    break
            if not found:
                ipa += syll[i]
                i += 1
        result.append(ipa)
    return '.'.join(result)
