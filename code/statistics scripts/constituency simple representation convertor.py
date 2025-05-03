#!/usr/bin/env python3
# ---------------------------------------------------------------
#  Canonical constituency signature  +  DH source per verse
# ---------------------------------------------------------------

import json
import pandas as pd
from pathlib import Path
from collections import defaultdict

# -----------------------------------------------------------------
# 1.  ---- FILE LOCATIONS ------------------------------------------
# -----------------------------------------------------------------
DATA_DIR = Path("../../data/parsed/constituency_parsing")        # edit if paths differ
CONST_JSON = {
    "Genesis"     : DATA_DIR / "Genesis.json",
    "Exodus"      : DATA_DIR / "Exodus.json",
    "Leviticus"   : DATA_DIR / "Leviticus.json",
    "Numbers"     : DATA_DIR / "Numbers.json",
    "Deuteronomy" : DATA_DIR / "Deuteronomy.json",
}
SOURCES_CSV = "../torah_full_sources_updated.csv"

# -----------------------------------------------------------------
# 2.  ---- DH helper copied from previous script -------------------
# -----------------------------------------------------------------
def parse_single(vstr):
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
    if '-' not in rng:                          # single verse
        c, v, s = parse_single(rng)
        return [make_vid(book, c, v, s)]

    start, end = rng.split('-')
    s_c, s_v, s_sub = parse_single(start)
    if ':' not in end:                          # 4:1‑16 style
        end = f"{s_c}:{end}"
    e_c, e_v, e_sub = parse_single(end)

    vids = []
    for chap in range(s_c, e_c + 1):
        v_from = s_v if chap == s_c else 1
        v_to   = e_v if chap == e_c else 200
        for verse in range(v_from, v_to + 1):
            if s_sub is not None or e_sub is not None:
                sub_from = s_sub if (chap==s_c and verse==s_v) else 1
                sub_to   = e_sub if (chap==e_c and verse==e_v) else 99
                for sub in range(sub_from, sub_to + 1):
                    vids.append(make_vid(book, chap, verse, sub))
            else:
                vids.append(make_vid(book, chap, verse))
    return vids

# -----------------------------------------------------------------
# 3.  ---- Build verse → source map --------------------------------
# -----------------------------------------------------------------
verse2src = defaultdict(set)
dh_df = pd.read_csv(SOURCES_CSV)

for _, row in dh_df.iterrows():
    for vid in expand_range(row["Book"], row["Range"]):
        verse2src[vid].add(row["Source"])

# -----------------------------------------------------------------
# 4.  ---- Canonical constituency signature ------------------------
# -----------------------------------------------------------------
def const_signature(verse_json):
    """
    Produce a stable string based on:
        • each sentence (in order)
        • each clause type inside that sentence (in order)
        • the ordered list of phrase FUNCTIONS inside the clause
    Example part:  "s0:NmCl(Subj+PreC)|xQtX(Rela+Pred+Subj+Objc+Loca)"
    """
    pieces = []
    for s_idx, sent in enumerate(verse_json["sentences"]):
        for clause in sent["clauses"]:
            c_type = clause["type"]
            p_funcs = '+'.join(ph["function"] for ph in clause["phrases"])
            pieces.append(f"s{s_idx}:{c_type}({p_funcs})")
    return '|'.join(pieces)

def signatures_from_file(path):
    with open(path, encoding='utf‑8') as fh:
        verses = json.load(fh)
    for v in verses:
        yield v["verse_id"], const_signature(v)

# -----------------------------------------------------------------
# 5.  ---- Collect all records ------------------------------------
# -----------------------------------------------------------------
records = []
for book, jpath in CONST_JSON.items():
    for vid, sig in signatures_from_file(jpath):
        records.append({
            "verse_id"                : vid,
            "constituency_signature"  : sig,
            "source"                  : ','.join(sorted(verse2src.get(vid, {"none"})))
        })

df = pd.DataFrame.from_records(records)

# -----------------------------------------------------------------
# 6.  ---- Save & preview -----------------------------------------
# -----------------------------------------------------------------
OUT = "verse_constituency_signatures_with_sources.csv"
df.to_csv(OUT, index=False, encoding='utf‑8')
print(f"✅  Saved {OUT}  ({len(df)} rows)")
print(df.head())
