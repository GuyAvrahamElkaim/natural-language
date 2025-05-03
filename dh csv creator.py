import xml.etree.ElementTree as ET
import pandas as pd
import re

# === Configuration ===
input_xml_file = "genesis_DH.xml"  # change this to your file name
output_csv_file = "torah_sources.csv"
book_name = "Genesis"  # change to "Exodus" etc. as needed

# === Helper to extract the chapter number ===
def extract_chapter(verse_range):
    match = re.match(r"(\d+):", verse_range.strip())
    return match.group(1) if match else None

# === Parse XML ===
tree = ET.parse(input_xml_file)
root = tree.getroot()

# === Extract Data ===
rows = []
for excerpt in root.findall("excerpt"):
    verse_range = excerpt.findtext("range", "").strip()
    source = excerpt.findtext("source", "").strip()
    note = excerpt.findtext("note", "").strip()
    chapter = extract_chapter(verse_range)
    rows.append({
        "book": book_name,
        "chapter": chapter,
        "source": source,
        "note": note
    })

# === Write to CSV ===
df = pd.DataFrame(rows)
df.to_csv(output_csv_file, index=False)
print(f"CSV saved to {output_csv_file}")
