import json
import csv
import re
from collections import defaultdict
import pandas as pd

# --- Range Parsing ---
def parse_range(range_str):
    def parse_point(s):
        if ':' in s:
            chapter, rest = s.split(':')
            if '.' in rest:
                verse, subverse = rest.split('.')
                return int(chapter), int(verse), int(subverse)
            return int(chapter), int(rest), 0
        else:
            return None, int(s), 0

    if '-' in range_str:
        start_str, end_str = [x.strip() for x in range_str.split('-')]
        start = parse_point(start_str)
        end = parse_point(end_str)
        if start[0] is None:
            start = (end[0], start[1], start[2])
        elif end[0] is None:
            end = (start[0], end[1], end[2])
    else:
        start = end = parse_point(range_str)

    return start, end

def verse_in_range(chap, verse, subverse, start, end):
    return (chap, verse, subverse) >= start and (chap, verse, subverse) <= end

def verse_id_to_key(verse_id):
    match = re.match(r'Tanakh\.Torah\.([^.]+)\.(\d+)\.(\d+)(?:\.(\d+))?', verse_id)
    if not match:
        return None
    book, chap, verse, subverse = match.groups()
    return book, int(chap), int(verse), int(subverse) if subverse else 0

# --- Load CSV ---
def load_source_ranges(csv_path):
    source_ranges = []
    with open(csv_path, newline='', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            start, end = parse_range(row['Range'])
            source_ranges.append({
                'start': start,
                'end': end,
                'source': row['Source'],
                'book': row['Book']
            })
    return source_ranges

# --- Get Source for a Verse ---
def get_source(book, chap, verse, subverse, source_ranges):
    for r in source_ranges:
        if r['book'] == book and verse_in_range(chap, verse, subverse, r['start'], r['end']):
            return r['source'], r['book']
    return None, book

# --- Process All Books ---
def process_all_books(json_files_by_book, source_csv_path, output_csv_path):
    source_ranges = load_source_ranges(source_csv_path)
    word_map = defaultdict(lambda: defaultdict(int))

    for expected_book, json_path in json_files_by_book.items():
        with open(json_path, encoding='utf-8') as f:
            data = json.load(f)

        for verse in data:
            verse_id = verse['verse_id']
            parsed = verse_id_to_key(verse_id)
            if not parsed:
                continue
            book, chap, verse_num, subverse = parsed
            source, book = get_source(book, chap, verse_num, subverse, source_ranges)

            tokens = verse['prediction'][0]['tokens']
            for token in tokens:
                word = token['token']
                word_map[word][book] += 1
                if source:
                    word_map[word][source] += 1

    # --- Write Output ---
    df = pd.DataFrame.from_dict(word_map, orient='index').fillna(0).astype(int)
    df.index.name = 'word'
    df = df.reset_index()

    columns = ['word', 'J', 'E', 'P', 'R', 'Genesis', 'Exodus', 'Leviticus', 'Numbers', 'Deuteronomy']
    for col in columns:
        if col not in df.columns:
            df[col] = 0
    df = df[columns]

    df.to_csv(output_csv_path, index=False)
    print(f"✅ CSV written to: {output_csv_path}")

# --- Example Usage ---
if __name__ == '__main__':
    json_files = {
        'Genesis': '../data/parsed/dependency_parsing/GenesisByDicta.json',
        'Exodus': '../data/parsed/dependency_parsing/ExodusByDicta.json',
        'Leviticus': '../data/parsed/dependency_parsing/LeviticusByDicta.json',
        'Numbers': '../data/parsed/dependency_parsing/NumbersByDicta.json',
        'Deuteronomy': '../data/parsed/dependency_parsing/DeuteronomyByDicta.json'
    }

    process_all_books(
        json_files_by_book=json_files,
        source_csv_path='../../torah_full_sources_updated.csv',
        output_csv_path='../../data/statistics/word_frequencies_by_book_and_source.csv'
    )
