import os
import xml.etree.ElementTree as ET
import json
from collections import defaultdict

def get_text_of_w(w_elem):
    """
    Extract text from a <w> element. If there's any nested <m> elements,
    you might want to combine those as well.
    """
    return w_elem.text.strip() if w_elem.text else ""

def build_phrases_for_clause(clause_elem, words_dict, ns):
    """
    Build a list of phrase dictionaries for each <phrase> inside the <clause>.
    """
    phrases_data = []
    # <phrase> is also in the TEI namespace
    for ph in clause_elem.findall("tei:phrase", ns):
        ph_id = ph.get("id")
        ph_func = ph.get("function")
        ph_type = ph.get("type")

        # Look up words that match this phrase ID
        words_list = words_dict.get(ph_id, [])

        phrase_info = {
            "phrase_id": ph_id,
            "function": ph_func,
            "phrase_type": ph_type,
            "words": words_list
        }
        phrases_data.append(phrase_info)
    return phrases_data

def build_clauses_for_sentence(sentence_elem, words_dict, ns):
    """
    Build a list of clauses from each <clause> in the <sentence>.
    """
    clauses_data = []
    for cl in sentence_elem.findall("tei:clause", ns):
        cl_id = cl.get("id")
        cl_type = cl.get("type")

        phrases = build_phrases_for_clause(cl, words_dict, ns)

        clause_info = {
            "clause_id": cl_id,
            "type": cl_type,
            "phrases": phrases
        }
        clauses_data.append(clause_info)
    return clauses_data

def build_sentences_for_verse(verse_elem, words_dict, ns):
    """
    Gather all <sentence> elements from <syntacticInfo> and build them out.
    """
    sentences_data = []
    # note the namespace in the .find(...) call
    syntactic_info_elem = verse_elem.find("tei:syntacticInfo", ns)
    if syntactic_info_elem is not None:
        for sent in syntactic_info_elem.findall("tei:sentence", ns):
            sent_id = sent.get("id")
            clauses = build_clauses_for_sentence(sent, words_dict, ns)

            sentence_info = {
                "sentence_id": sent_id,
                "clauses": clauses
            }
            sentences_data.append(sentence_info)
    return sentences_data

def build_verse_representation(verse_elem, ns):
    """
    Construct a dict representing a single verse <s type="pasuk">.
    """
    # Because xml:id is in a special namespace: {http://www.w3.org/XML/1998/namespace}id
    verse_id = verse_elem.get("{http://www.w3.org/XML/1998/namespace}id", "unknown_id")

    # Collect words by phraseId
    words_by_phrase = defaultdict(list)

    # Now find <w> in TEI namespace
    for w in verse_elem.findall("tei:w", ns):
        w_phrase_id = w.get("phraseId")
        w_text = get_text_of_w(w)

        if w_phrase_id:
            words_by_phrase[w_phrase_id].append(w_text)
        else:
            # If no phraseId on <w>, try any <m> child
            for m in w.findall("tei:m", ns):
                m_phrase_id = m.get("phraseId")
                if m_phrase_id:
                    m_text = m.text.strip() if m.text else w_text
                    words_by_phrase[m_phrase_id].append(m_text)

    # Build sentences from <syntacticInfo>
    sentences = build_sentences_for_verse(verse_elem, words_by_phrase, ns)

    return {
        "verse_id": verse_id,
        "sentences": sentences
    }

def process_shebanq_file(xml_path):
    """
    Parse the TEI-based XML for all <s type="pasuk"> elements
    and build a data structure for each verse.
    """
    tree = ET.parse(xml_path)
    root = tree.getroot()

    # TEI namespace dictionary
    ns = {"tei": "http://www.tei-c.org/ns/1.0"}

    # Now we find <s> with type="pasuk" in the TEI namespace
    verses_data = []
    for verse_elem in root.findall(".//tei:s[@type='pasuk']", ns):
        verse_dict = build_verse_representation(verse_elem, ns)
        verses_data.append(verse_dict)

    return verses_data

if __name__ == "__main__":
    import sys

    if len(sys.argv) > 2:
        directory = sys.argv[1]
        file_name = sys.argv[2]
        xml_path = os.path.join(directory, file_name)
    else:
        # Provide defaults or exit with usage instructions
        directory = "."
        file_name = "../Deuteronomy.xml"
        xml_path = os.path.join(directory, file_name)

    verses_data = process_shebanq_file(xml_path)
output_file = os.path.join(directory, "Deuteronomy.json")
with open(output_file, "w", encoding="utf-8") as f:
    json.dump(verses_data, f, ensure_ascii=False, indent=2)