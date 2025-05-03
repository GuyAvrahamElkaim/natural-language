import json
import csv
from collections import defaultdict
import re

# --- Utilities to handle ranges ---
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

# --- Load source ranges from CSV ---
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

# --- Get matching source for a verse ---
def get_source(book, chap, verse, subverse, source_ranges):
    for r in source_ranges:
        if r['book'] == book and verse_in_range(chap, verse, subverse, r['start'], r['end']):
            return r['source'], r['book']
    return None, book

# --- Process multiple books ---
def count_phrase_types(json_files_by_book, source_csv_path, output_csv_path):
    source_ranges = load_source_ranges(source_csv_path)
    phrase_map = defaultdict(lambda: defaultdict(int))

    for book_name, json_path in json_files_by_book.items():
        with open(json_path, encoding="utf-8") as f:
            data = json.load(f)

        for verse in data:
            verse_id = verse.get("verse_id")
            parsed = verse_id_to_key(verse_id)
            if not parsed:
                continue
            book, chap, verse_num, subverse = parsed
            source, _ = get_source(book, chap, verse_num, subverse, source_ranges)

            for sentence in verse.get("sentences", []):
                for clause in sentence.get("clauses", []):
                    for phrase in clause.get("phrases", []):
                        phrase_type = phrase.get("phrase_type")
                        if phrase_type:
                            phrase_map[phrase_type][book] += 1
                            if source:
                                phrase_map[phrase_type][source] += 1

    # Prepare columns
    all_phrase_types = sorted(phrase_map.keys())
    columns = ["phrase_type", "J", "E", "P", "R", "Genesis", "Exodus", "Leviticus", "Numbers", "Deuteronomy"]
    rows = []

    for phrase_type in all_phrase_types:
        row = [phrase_type]
        for col in columns[1:]:
            row.append(phrase_map[phrase_type].get(col, 0))
        rows.append(row)

    # Write CSV
    with open(output_csv_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(columns)
        writer.writerows(rows)

    print(f"✅ CSV saved to: {output_csv_path}")

# --- Run the script ---
if __name__ == "__main__":
    json_files = {
        "Genesis": "../data/parsed/constituency_parsing/Genesis.json",
        "Exodus": "../data/parsed/constituency_parsing/Exodus.json",
        "Leviticus": "../data/parsed/constituency_parsing/Leviticus.json",
        "Numbers": "../data/parsed/constituency_parsing/Numbers.json",
        "Deuteronomy": "../data/parsed/constituency_parsing/Deuteronomy.json",
    }

    count_phrase_types(
        json_files_by_book=json_files,
        source_csv_path="../../torah_full_sources_updated.csv",
        output_csv_path="../../data/statistics/phrase_type_frequencies_by_book_and_source.csv"
    )
