# utils.py — handles CSV, Excel, and Google Sheets processing
import pandas as pd
import gspread
from oauth2client.service_account import ServiceAccountCredentials
from .processor import process_text

def transcribe_dataframe(df, column_name, word_by_word=False):
    results = []
    for val in df[column_name].dropna():
        output = process_text(str(val), word_by_word)
        if word_by_word:
            breakdown = "; ".join([f"{k} = {v[0]}" for k, v in output.items()])
            ipa = "; ".join([f"{k} = {v[1]}" for k, v in output.items()])
        else:
            breakdown = output['sentence'][0]
            ipa = output['sentence'][1]
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
