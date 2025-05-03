#!/usr/bin/env python3
# ---------------------------------------------------------------
#  Build verse‑level Teamim signature + DH source
#  from ONE combined JSON file that contains *all* Torah verses
# ---------------------------------------------------------------

import json, re, unicodedata, pandas as pd
from pathlib import Path
from collections import defaultdict

# -----------------------------------------------------------------
# 1.  ---- FILES ---------------------------------------------------
# -----------------------------------------------------------------
DATA_DIR   = Path("/../data/parsed/teamim")               # adjust if needed
TEAMIM_FILE = DATA_DIR / "verse_trees_ranked.json"  # <‑‑ your single file here
SOURCES_CSV = "../torah_full_sources_updated.csv"

# -----------------------------------------------------------------
# 2.  ---- TEAMIM → 3‑letter slug ---------------------------------
# -----------------------------------------------------------------
CANT_RE    = re.compile('[\u0591-\u05AF]')
slug_cache = {}

def slug(sign: str) -> str:
    if sign in slug_cache:
        return slug_cache[sign]
    base = unicodedata.name(sign).split()[-1]   # e.g. ... TIPHCHA
    slug_cache[sign] = base.lower()[:3]         # 'tip'
    return slug_cache[sign]

def teamim_signature(tokens) -> str:
    parts = []
    for tok in tokens:
        m = CANT_RE.search(tok["token"])
        if not m:
            continue
        sign = m.group()
        if sign == "֡":          # skip sof‑pasuq / siluk
            continue
        parts.append(slug(sign))
    return '-'.join(parts)

# -----------------------------------------------------------------
# 3.  ---- EXPAND DH SOURCE RANGES --------------------------------
#      (same helper set as in earlier scripts)
# -----------------------------------------------------------------
def parse_single(vstr):
    if '.' in vstr:
        cv, sub = vstr.split('.')
        chap, verse = map(int, cv.split(':'))
        return chap, verse, int(sub)
    chap, verse = map(int, vstr.split(':'))
    return chap, verse, None

def make_vid(book, chap, verse, sub=None):
    base = f"Tanakh.Torah.{book}.{chap}.{verse}"
    return f"{base}.{sub}" if sub is not None else base

def expand_range(book, rng):
    if '-' not in rng:
        c, v, s = parse_single(rng)
        return [make_vid(book, c, v, s)]

    start, end   = rng.split('-')
    s_c, s_v, s_sub = parse_single(start)
    if ':' not in end:                       # e.g. "4:1-16"
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
# 4.  ---- Build verse → source map --------------------------------
# -----------------------------------------------------------------
verse2src = defaultdict(set)
dh_df = pd.read_csv(SOURCES_CSV)

for _, row in dh_df.iterrows():
    for vid in expand_range(row["Book"], row["Range"]):
        verse2src[vid].add(row["Source"])

# -----------------------------------------------------------------
# 5.  ---- Read ONE teamim file & collect signatures ---------------
# -----------------------------------------------------------------
records = []
with open(TEAMIM_FILE, encoding='utf‑8') as fh:
    all_verses = json.load(fh)

for v in all_verses:
    vid  = v["verse_id"]
    sig  = teamim_signature(v["prediction"][0]["tokens"])
    srcs = verse2src.get(vid, {"none"})
    records.append({
        "verse_id"         : vid,
        "teamim_signature" : sig,
        "source"           : ','.join(sorted(srcs))
    })

df = pd.DataFrame.from_records(records)

# -----------------------------------------------------------------
# 6.  ---- SAVE ----------------------------------------------------
# -----------------------------------------------------------------
OUT = "verse_teamim_signatures_with_sources.csv"
df.to_csv(OUT, index=False, encoding='utf‑8')
print(f"✅  Saved {OUT}  ({len(df)} rows)")
print(df.head())
