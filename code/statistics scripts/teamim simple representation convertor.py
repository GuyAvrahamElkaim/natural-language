#!/usr/bin/env python3
# ---------------------------------------------------------------
#  Taʿam canonical signatures  +  DH source labels
#  (handles short IDs like 'gn1:1')
# ---------------------------------------------------------------

import json, pandas as pd
from pathlib import Path
from collections import defaultdict

# -----------------------------------------------------------------
# 1  FILE LOCATIONS
# -----------------------------------------------------------------
DATA_DIR        = Path("../../data/parsed/teamim")
TEAMIM_JSON     = DATA_DIR / "torah_teamim_verses_trees_ranked.json"
DH_SOURCES_CSV  = "../../torah_full_sources_updated.csv"
OUTPUT_CSV      = "verse_teamim_signatures_with_sources.csv"

# -----------------------------------------------------------------
# 2  SHORT‑ID → LONG‑ID CONVERSION
# -----------------------------------------------------------------
BOOK_CODE = {
    "gn": "Genesis",
    "ex": "Exodus",
    "lv": "Leviticus",
    "nu": "Numbers",
    "dt": "Deuteronomy",
}

def short_to_long_id(short_id: str) -> str:
    """
    Convert 'gn1:1' or 'gn1:1.2' → 'Tanakh.Torah.Genesis.1.1' (.2)
    """
    # split sub‑verse if exists
    if '.' in short_id:
        verse_part, sub = short_id.split('.')
    else:
        verse_part, sub = short_id, None

    # extract book code + chapter:verse
    code, chap_verse = verse_part[:2], verse_part[2:]
    book = BOOK_CODE[code.lower()]
    chap, verse = chap_verse.split(':')
    long_id = f"Tanakh.Torah.{book}.{int(chap)}.{int(verse)}"
    if sub is not None:
        long_id += f".{int(sub)}"
    return long_id

# -----------------------------------------------------------------
# 3  BUILD VERSE→SOURCE MAP  (same logic as before)
# -----------------------------------------------------------------
def parse_single(vstr):
    if '.' in vstr: cv, s = vstr.split('.'); c,v = map(int,cv.split(':')); return c,v,int(s)
    c,v = map(int, vstr.split(':')); return c,v,None

def make_vid(book,c,v,s=None):
    base=f"Tanakh.Torah.{book}.{c}.{v}"
    return f"{base}.{s}" if s else base

def expand_range(book, rng):
    if '-' not in rng:
        c,v,s=parse_single(rng); return [make_vid(book,c,v,s)]
    start,end=rng.split('-')
    s_c,s_v,s_s=parse_single(start)
    if ':' not in end: end=f"{s_c}:{end}"
    e_c,e_v,e_s=parse_single(end)
    vids=[]
    for chap in range(s_c,e_c+1):
        v_from=s_v if chap==s_c else 1
        v_to  =e_v if chap==e_c else 200
        for verse in range(v_from,v_to+1):
            if s_s is not None or e_s is not None:
                sub_from=s_s if (chap==s_c and verse==s_v) else 1
                sub_to  =e_s if (chap==e_c and verse==e_v) else 99
                for sub in range(sub_from,sub_to+1):
                    vids.append(make_vid(book,chap,verse,sub))
            else:
                vids.append(make_vid(book,chap,verse))
    return vids

verse2src = defaultdict(set)
for _,row in pd.read_csv(DH_SOURCES_CSV).iterrows():
    for vid in expand_range(row["Book"], row["Range"]):
        verse2src[vid].add(row["Source"])

# -----------------------------------------------------------------
# 4  TAʿAM SIGNATURE HELPERS
# -----------------------------------------------------------------
RANK = {"emperor":"E","king":"K","second":"S","third":"T"}
def sig_node(n):
    head=f"{RANK.get(n['type'],'X')}{n['index']}({n['accent']})"
    kids=n.get("children",[])
    return f"{head}[{','.join(sig_node(k) for k in kids)}]" if kids else head

def signature(obj):
    root=obj.get("tree",obj)
    return "|".join(sig_node(e) for e in root["children"])

# -----------------------------------------------------------------
# 5  PROCESS VERSES
# -----------------------------------------------------------------
records=[]
with open(TEAMIM_JSON, encoding="utf-8") as fh:
    verses=json.load(fh)          # dict: {short_id: treeObj}

for short_id, tree in verses.items():
    long_id = short_to_long_id(short_id)
    sig     = signature(tree)
    srcs    = verse2src.get(long_id, {"none"})
    records.append({
        "verse_id":         long_id,
        "teamim_signature": sig,
        "source":           ",".join(sorted(srcs)),
    })

# -----------------------------------------------------------------
# 6  SAVE CSV
# -----------------------------------------------------------------
pd.DataFrame(records).to_csv(OUTPUT_CSV, index=False, encoding="utf-8")
print(f"✅  Saved {OUTPUT_CSV}  ({len(records)} rows)")
print(pd.DataFrame(records).head())
