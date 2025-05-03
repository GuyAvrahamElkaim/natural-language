import xml.etree.ElementTree as ET
import json
from transformers import AutoModel, AutoTokenizer

def main():
    # 1. Load the tokenizer/model
    tokenizer = AutoTokenizer.from_pretrained('dicta-il/dictabert-tiny-joint')
    model = AutoModel.from_pretrained('dicta-il/dictabert-tiny-joint', trust_remote_code=True)
    model.eval()

    # 2. Parse the XML file
    tree = ET.parse('../Numbers.xml')  # or 'Deuteronomy.xml', etc.
    root = tree.getroot()

    book_name = 'Numbers'
    results = []

    for chapter in root.findall('.//c'):
        chapter_num = chapter.attrib.get('n')
        for verse in chapter.findall('v'):
            verse_num = verse.attrib.get('n')
            verse_id = f"Tanakh.Torah.{book_name}.{chapter_num}.{verse_num}"

            # Extract text
            verse_text = ' '.join(
                w.text for w in verse.findall('w') if w.text
            ).strip()

            if verse_text:
                prediction = model.predict([verse_text], tokenizer, output_style='json')
                results.append({
                    'verse_id': verse_id,
                    'text': verse_text,
                    'prediction': prediction
                })

    # 3. Write all predictions into a single JSON file
    with open('../NumbersByDicta.json', 'w', encoding='utf-8') as out_file:
        json.dump(results, out_file, ensure_ascii=False, indent=2)

if __name__ == "__main__":
    main()
