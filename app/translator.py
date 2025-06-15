from deep_translator import GoogleTranslator

def translate_in_chunks(text, chunk_size=4900):
    translated_text = ""
    for i in range(0, len(text), chunk_size):
        chunk = text[i:i + chunk_size]
        translated_chunk = GoogleTranslator(source='auto', target='en').translate(chunk)
        translated_text += translated_chunk + " "
        return translated_text.strip()