import re

import pandas as pd
import re
import os
import io
import gspread
from oauth2client.service_account import ServiceAccountCredentials

# Include previous syllabify, to_ipa, and process_text functions here

def transcribe_dataframe(df, column_name, word_by_word=False):
    results = []

    for val in df[column_name].dropna():
        out = process_text(str(val), word_by_word)
        if word_by_word:
            breakdown = "; ".join([f"{k} = {v[0]}" for k, v in out.items()])
            ipa = "; ".join([f"{k} = {v[1]}" for k, v in out.items()])
        else:
            breakdown = out['sentence'][0]
            ipa = out['sentence'][1]
        results.append((val, breakdown, ipa))

    df['Syllabified'] = [r[1] for r in results]
    df['IPA'] = [r[2] for r in results]
    return df

def handle_uploaded_file(file, ext, column_name="Text", word_by_word=False):
    if ext == ".csv":
        df = pd.read_csv(file)
    elif ext in [".xls", ".xlsx"]:
        df = pd.read_excel(file)
    else:
        raise ValueError("Unsupported file type.")
    
    return transcribe_dataframe(df, column_name, word_by_word)

def handle_google_sheet(sheet_url, creds_json_path, column_name="Text", word_by_word=False):
    scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
    creds = ServiceAccountCredentials.from_json_keyfile_name(creds_json_path, scope)
    client = gspread.authorize(creds)

    sheet_id = sheet_url.split("/d/")[1].split("/")[0]
    sheet = client.open_by_key(sheet_id).sheet1
    data = sheet.get_all_records()
    df = pd.DataFrame(data)

    return transcribe_dataframe(df, column_name, word_by_word)

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

def process_text(text, word_by_word=False):
    # Example implementation, adjust with your actual logic
    words = text.split()
    result = {}

    if word_by_word:
        for word in words:
            syllables = syllabify(word)
            ipa = to_ipa(syllables)
            result[word] = (syllables, ipa)
        return result
    else:
        all_syllables = []
        all_ipa = []
        for word in words:
            all_syllables.append(syllabify(word))
            all_ipa.append(to_ipa(all_syllables[-1]))
        return {'sentence': (" ".join(all_syllables), " ".join(all_ipa))}
