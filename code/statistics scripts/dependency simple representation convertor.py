#!/usr/bin/env python3
# ---------------------------------------------------------------
#  Create a dependency‑syntax signature for every Torah verse
#  and attach DH source(s) from torah_full_sources_updated.csv
# ---------------------------------------------------------------

import json
import pandas as pd
from pathlib import Path
from collections import defaultdict

# -----------------------------------------------------------------
# 1.  ---- CONFIGURE FILE LOCATIONS --------------------------------
# -----------------------------------------------------------------
DATA_DIR = Path("../../data/parsed/dependency_parsing")        # adjust if your files sit elsewhere
JSON_FILES = {
    "Genesis"     : DATA_DIR / "GenesisByDicta.json",
    "Exodus"      : DATA_DIR / "ExodusByDicta.json",
    "Leviticus"   : DATA_DIR / "LeviticusByDicta.json",
    "Numbers"     : DATA_DIR / "NumbersByDicta.json",
    "Deuteronomy" : DATA_DIR / "DeuteronomyByDicta.json",
}
SOURCES_CSV = "../torah_full_sources_updated.csv"

# -----------------------------------------------------------------
# 2.  ---- HELPERS -------------------------------------------------
# -----------------------------------------------------------------
def canonical_signature(tokens):
    """
    Build a canonical, word‑independent string representing only
    the dependency relations: "childIdx:depFunc->headIdx|..."
    """
    triples = []
    for idx, tok in enumerate(tokens):
        syn = tok.get("syntax", {})
        triples.append((idx,
                        syn.get("dep_func"),
                        syn.get("dep_head_idx")))
    triples.sort()
    return '|'.join(f"{i}:{f}->{h}" for i, f, h in triples)

def signatures_from_json(jpath):
    """Yield (verse_id, syntax_signature) for every verse in file."""
    with open(jpath, encoding='utf‑8') as fh:
        verses = json.load(fh)
    for v in verses:
        vid = v["verse_id"]
        sig = canonical_signature(v["prediction"][0]["tokens"])
        yield vid, sig

# --------- Range‑expansion helpers --------------------------------
def parse_single(vstr):
    """
    Accepts '3:16.2'  → (chapter, verse, subverse or None)
            '3:16'    → (chapter, verse, None)
    """
    if '.' in vstr:
        chap_verse, sub = vstr.split('.')
        chap, verse = map(int, chap_verse.split(':'))
        return chap, verse, int(sub)
    chap, verse = map(int, vstr.split(':'))
    return chap, verse, None

def make_vid(book, chap, verse, sub=None):
    base = f"Tanakh.Torah.{book}.{chap}.{verse}"
    return f"{base}.{sub}" if sub is not None else base

def expand_range(book, rng):
    """
    Turn DH range strings into a list of verse_id strings.
    Handles:
        * single verse      '4:12'
        * normal range      '4:12-4:20'  OR  '4:12-20'
        * split‑verse range '2:4.1-2:4.5'
    """
    # — single verse ---------------------------------------------
    if '-' not in rng:
        c, v, s = parse_single(rng)
        return [make_vid(book, c, v, s)]

    # — range -----------------------------------------------------
    start, end = rng.split('-')
    s_c, s_v, s_sub = parse_single(start)

    # if end has no chapter (e.g. '4:1-16') prepend the start chapter
    if ':' not in end:
        end = f"{s_c}:{end}"

    e_c, e_v, e_sub = parse_single(end)

    vids = []
    for chap in range(s_c, e_c + 1):
        v_from = s_v if chap == s_c else 1
        v_to   = e_v if chap == e_c else 200   # generous upper bound
        for verse in range(v_from, v_to + 1):
            if (s_sub is not None) or (e_sub is not None):
                # we are inside a split‑verse context
                sub_from = s_sub if (chap==s_c and verse==s_v) else 1
                sub_to   = e_sub if (chap==e_c and verse==e_v) else 99
                for sub in range(sub_from, sub_to + 1):
                    vids.append(make_vid(book, chap, verse, sub))
            else:
                vids.append(make_vid(book, chap, verse))
    return vids

# -----------------------------------------------------------------
# 3.  ---- BUILD verse‑to‑source MAP -------------------------------
# -----------------------------------------------------------------
verse2src = defaultdict(set)
dh_df = pd.read_csv(SOURCES_CSV)

for _, row in dh_df.iterrows():
    for vid in expand_range(row["Book"], row["Range"]):
        verse2src[vid].add(row["Source"])

# -----------------------------------------------------------------
# 4.  ---- COLLECT EVERYTHING --------------------------------------
# -----------------------------------------------------------------
records = []
for book, path in JSON_FILES.items():
    for vid, sig in signatures_from_json(path):
        srcs = verse2src.get(vid, {"none"})
        records.append({
            "verse_id"         : vid,
            "syntax_signature" : sig,
            "source"           : ','.join(sorted(srcs))
        })

df = pd.DataFrame.from_records(records)

# -----------------------------------------------------------------
# 5.  ---- SAVE & PRINT -------------------------------------------
# -----------------------------------------------------------------
OUTPUT = "verse_dependency_signatures_with_sources.csv"
df.to_csv(OUTPUT, index=False, encoding='utf‑8')
print(f"✅  Saved {OUTPUT} ({len(df)} rows)")

# quick sanity‑check
print(df.head())
