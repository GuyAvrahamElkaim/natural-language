import csv
import xml.etree.ElementTree as ET
from collections import defaultdict

# Paths to XML files
book_files = {
    "Genesis": "../data/raw/menukad/Genesis.xml",
    "Exodus": "../data/raw/menukad/Exodus.xml",
    "Leviticus": "../data/raw/menukad/Leviticus.xml",
    "Numbers": "../data/raw/menukad/Numbers.xml",
    "Deuteronomy": "../data/raw/menukad/Deuteronomy.xml",
}

# Path to the source mapping CSV (DH ranges)
source_csv_path = "../../torah_full_sources_updated.csv"

# Output CSV path
output_path = "token_length_distribution_by_book_and_source_from_xml.csv"

# Tokens to exclude
exclude_tokens = {":", "-", "׃", "־", "׀"}

# --- Range Parsing Utilities ---
def parse_range(range_str):
    def parse_point(s):
        if ':' in s:
            chapter, rest = s.split(':')
            if '.' in rest:
                verse, subverse = rest.split('.')
                return int(chapter), int(verse), int(subverse)
            return int(chapter), int(rest), 0
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

def get_source(book, chap, verse, subverse, source_ranges):
    for r in source_ranges:
        if r['book'] == book and verse_in_range(chap, verse, subverse, r['start'], r['end']):
            return r['source']
    return None

# --- Main Token Length Count ---
def count_token_lengths(book_files, source_ranges):
    length_counts = defaultdict(lambda: defaultdict(int))

    for book, path in book_files.items():
        try:
            tree = ET.parse(path)
            root = tree.getroot()
        except Exception as e:
            print(f"⚠️ Failed to process {book}: {e}")
            continue

        for c in root.findall(".//c"):
            chapter = int(c.attrib['n'])
            for v in c.findall('v'):
                verse = int(v.attrib['n'])
                subverse = 0  # XML doesn't seem to include subverses

                source = get_source(book, chapter, verse, subverse, source_ranges)

                # Count valid tokens
                token_count = 0
                for w in v.findall('w'):
                    text = (w.text or "").strip()
                    if text and text not in exclude_tokens:
                        token_count += 1

                if token_count > 0:
                    length_counts[token_count][book] += 1
                    if source:
                        length_counts[token_count][source] += 1

    return length_counts

# --- Write CSV ---
def write_length_distribution(length_counts, output_path):
    columns = ["length", "J", "E", "P", "R", "Genesis", "Exodus", "Leviticus", "Numbers", "Deuteronomy"]
    with open(output_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(columns)

        for length in sorted(length_counts.keys()):
            row = [length]
            for col in columns[1:]:
                row.append(length_counts[length].get(col, 0))
            writer.writerow(row)

    print(f"✅ CSV saved to: {output_path}")

# --- Run All Steps ---
if __name__ == "__main__":
    source_ranges = load_source_ranges(source_csv_path)
    length_counts = count_token_lengths(book_files, source_ranges)
    write_length_distribution(length_counts, output_path)
