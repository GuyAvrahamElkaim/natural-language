import csv
import json
import re
from collections import defaultdict

def parse_point(s, default_chapter=None):
    """
    Parses formats like:
    - C:V.W => (C, V, W)
    - C:V => (C, V, 0)
    - V => (default_chapter, V, 0)
    """
    if ":" in s:
        chapter_str, verse_str = s.split(":")
        chapter = int(chapter_str)
    else:
        if default_chapter is None:
            raise ValueError(f"Missing chapter in: {s}")
        chapter = default_chapter
        verse_str = s

    if "." in verse_str:
        verse_parts = verse_str.split(".")
        verse = int(verse_parts[0])
        subverse = int(verse_parts[1])
    else:
        verse = int(verse_str)
        subverse = 0

    return (chapter, verse, subverse)

def parse_range(range_str):
    """
    Parses ranges like:
    - '2:4.6 - 2:25.99'
    - '2:4 - 25'
    - '2:4'
    """
    if '-' in range_str:
        start_str, end_str = [s.strip() for s in range_str.split('-')]
        start = parse_point(start_str)
        end = parse_point(end_str, default_chapter=start[0])
    else:
        start = parse_point(range_str.strip())
        end = start
    return start, end

def verse_in_range(verse_key, start, end):
    return start <= verse_key <= end

def load_sources(csv_path, book):
    sources = []
    with open(csv_path, newline='', encoding='utf-8-sig') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            range_str = row.get('Range') or row.get('range')
            if not range_str:
                continue
            try:
                start, end = parse_range(range_str)
                sources.append({
                    'start': start,
                    'end': end,
                    'source': row.get('Source', '').strip(),
                    'book': book,
                    'note': row.get('Note', '').strip()
                })
            except ValueError as e:
                print(f"Skipping invalid range '{range_str}': {e}")
    return sources

def get_source_for_verse(verse_id, sources_by_book):
    """
    Extracts source (J/E/P/R) and book from verse_id like 'Tanakh.Torah.Genesis.1.1'
    """
    match = re.match(r"Tanakh\.Torah\.([^.]+)\.(\d+)\.(\d+)", verse_id)
    if not match:
        return None, None

    book, chap, verse = match.groups()
    chap = int(chap)
    verse = int(verse)
    key = (chap, verse, 0)

    for source in sources_by_book.get(book, []):
        if verse_in_range(key, source['start'], source['end']):
            return source['source'], book

    return None, book

def main(json_path, csv_path, book_name, output_csv):
    sources_by_book = {book_name: load_sources(csv_path, book_name)}

    with open(json_path, encoding='utf-8') as f:
        data = json.load(f)

    word_map = defaultdict(lambda: defaultdict(int))

    for verse in data:
        verse_id = verse['verse_id']
        words = verse['tokens']
        source, book = get_source_for_verse(verse_id, sources_by_book)
        if not book:
            continue

        for word in words:
            word_map[word][book] += 1
            if source:
                word_map[word][source] += 1

    with open(output_csv, 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        header = ['word', 'J', 'E', 'P', 'R', 'Genesis', 'Exodus', 'Leviticus', 'Numbers', 'Deuteronomy']
        writer.writerow(header)

        for word, counts in sorted(word_map.items()):
            row = [word]
            for col in header[1:]:
                row.append(counts.get(col, 0))
            writer.writerow(row)

if __name__ == '__main__':
    # Change paths as needed:
    main(
        json_path='words.json',
        csv_path='genesis_sources.csv',
        book_name='Genesis',
        output_csv='word_counts.csv'
    )
