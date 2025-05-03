import json
from pathlib import Path

def extract_verse_statistics(verse_id):
    """Placeholder for statistics extraction - will be implemented later"""
    return {
        "word_count": 0,
        "unique_words": 0,
        "dependency_depth": 0,
        "teamim_depth": 0,
        "constituency_clauses": 0,
        "teamim_clauses": 0
    }

def generate_verse_entry(verse_id):
    """Generate a basic verse entry without DH sources"""
    parts = verse_id.split('.')
    book = parts[2]
    chapter = int(parts[3])
    verse = int(parts[4])
    stats = extract_verse_statistics(verse_id)

    return {
        "verse_id": verse_id,
        "book": book,
        "chapter": chapter,
        "verse": verse,
        "statistics": stats
    }

def create_books_statistics():
    # Torah books list
    TORAH_BOOKS = ['genesis', 'exodus', 'leviticus', 'numbers', 'deuteronomy']

    # Create verses_stats directory if it doesn't exist
    Path('data/verses_stats').mkdir(exist_ok=True)

    # Process each Torah book
    for book in TORAH_BOOKS:
        try:
            # Read verse IDs from dependency file
            with open(f'data/dependency/{book}_dep.json', 'r') as f:
                verse_ids = json.load(f).keys()

            # Generate entries for each verse
            verses_data = []
            for verse_id in verse_ids:
                verse_entry = generate_verse_entry(verse_id)
                verses_data.append(verse_entry)

            # Save to output file
            output_path = f'data/verses_stats/{book}_verses_stats.json'
            with open(output_path, 'w', encoding='utf-8') as f:
                json.dump(verses_data, f, ensure_ascii=False, indent=2)

            print(f"Generated statistics for {book}: {len(verses_data)} verses")

        except FileNotFoundError as e:
            print(f"Warning: Could not process {book}, file not found: {e}")

if __name__ == "__main__":
    create_books_statistics()