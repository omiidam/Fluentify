#!/usr/bin/env python3
"""Audits Fluentify's content sources for British English.

Two lists, because the two cases need different handling:

  SPELLING  orthographic only (colour, organise, centre, travelling). These can
            be converted mechanically; no American reading of the word is lost.

  VOCAB     lexical choices that are correct English but not the American
            default (petrol, queue, flat for apartment). Several of these have
            a legitimate American meaning of their own - "flat" is an adjective,
            "lift" is a verb, "mark" is a verb - so they are printed with
            context and judged by hand, never replaced blindly.

Proper nouns and institutions (British, BBC, London, pound) are reported
separately: they are facts about the world, not spelling choices, and stay.

Read-only. Exit 0 always so it can sit in a check run; the real gate is
check_american.py once the content is converted.
"""

import re
import sys
from collections import Counter, defaultdict
from pathlib import Path

ROOT = Path(__file__).parent.parent

SPELLING = {
    "colour": "color", "colours": "colors", "coloured": "colored",
    "colourful": "colorful", "colouring": "coloring", "colourless": "colorless",
    "favourite": "favorite", "favourites": "favorites",
    "favour": "favor", "favours": "favors", "favoured": "favored",
    "favourable": "favorable", "favourably": "favorably",
    "behaviour": "behavior", "behaviours": "behaviors",
    "harbour": "harbor", "harbours": "harbors",
    "neighbour": "neighbor", "neighbours": "neighbors",
    "neighbourhood": "neighborhood", "neighbourhoods": "neighborhoods",
    "neighbouring": "neighboring",
    "labour": "labor", "labours": "labors", "laboured": "labored",
    "honour": "honor", "honours": "honors", "honoured": "honored",
    "honourable": "honorable",
    "humour": "humor",
    "rumour": "rumor", "rumours": "rumors",
    "armour": "armor", "armoured": "armored",
    "odour": "odor", "odours": "odors",
    "vapour": "vapor", "vapours": "vapors",
    "flavour": "flavor", "flavours": "flavors", "flavoured": "flavored",
    "savour": "savor", "savoury": "savory",
    "endeavour": "endeavor", "endeavours": "endeavors",
    "rigour": "rigor", "rigours": "rigors",
    "splendour": "splendor",
    "tumour": "tumor", "tumours": "tumors",
    "valour": "valor",
    "vigour": "vigor",
    "clamour": "clamor",
    "parlour": "parlor", "parlours": "parlors",
    "centre": "center", "centres": "centers", "centred": "centered",
    "centrepiece": "centerpiece",
    "theatre": "theater", "theatres": "theaters",
    "metre": "meter", "metres": "meters",
    "litre": "liter", "litres": "liters",
    "fibre": "fiber", "fibres": "fibers",
    "calibre": "caliber",
    "sombre": "somber",
    "lustre": "luster",
    "spectre": "specter",
    "manoeuvre": "maneuver", "manoeuvres": "maneuvers",
    "manoeuvring": "maneuvering",
    "organise": "organize", "organises": "organizes",
    "organised": "organized", "organising": "organizing",
    "organisation": "organization", "organisations": "organizations",
    "realise": "realize", "realises": "realizes",
    "realised": "realized", "realising": "realizing",
    "realisation": "realization", "realisations": "realizations",
    "recognise": "recognize", "recognises": "recognizes",
    "recognised": "recognized", "recognising": "recognizing",
    "apologise": "apologize", "apologises": "apologizes",
    "apologised": "apologized", "apologising": "apologizing",
    "criticise": "criticize", "criticises": "criticizes",
    "criticised": "criticized", "criticising": "criticizing",
    "emphasise": "emphasize", "emphasises": "emphasizes",
    "emphasised": "emphasized", "emphasising": "emphasizing",
    "summarise": "summarize", "summarises": "summarizes",
    "summarised": "summarized", "summarising": "summarizing",
    "analyse": "analyze", "analyses": "analyzes",
    "analysed": "analyzed", "analysing": "analyzing",
    "specialise": "specialize", "specialises": "specializes",
    "specialised": "specialized", "specialising": "specializing",
    "specialisation": "specialization",
    "memorise": "memorize", "memorises": "memorizes",
    "memorised": "memorized", "memorising": "memorizing",
    "prioritise": "prioritize", "prioritises": "prioritizes",
    "prioritised": "prioritized", "prioritising": "prioritizing",
    "minimise": "minimize", "minimises": "minimizes",
    "minimised": "minimized", "minimising": "minimizing",
    "maximise": "maximize", "maximises": "maximizes",
    "maximised": "maximized", "maximising": "maximizing",
    "optimise": "optimize", "optimises": "optimizes",
    "optimised": "optimized", "optimising": "optimizing",
    "modernise": "modernize", "modernised": "modernized",
    "standardise": "standardize", "standardised": "standardized",
    "standardisation": "standardization",
    "globalise": "globalize", "globalisation": "globalization",
    "localise": "localize", "localised": "localized",
    "legalise": "legalize", "legalised": "legalized",
    "normalise": "normalize", "normalised": "normalized",
    "stabilise": "stabilize", "stabilised": "stabilized",
    "mobilise": "mobilize", "mobilised": "mobilized",
    "civilise": "civilize", "civilised": "civilized",
    "practise": "practice", "practises": "practices",
    "practised": "practiced", "practising": "practicing",
    "licence": "license", "licences": "licenses",
    "defence": "defense", "defences": "defenses",
    "offence": "offense", "offences": "offenses",
    "pretence": "pretense",
    "programme": "program", "programmes": "programs",
    "catalogue": "catalog", "catalogues": "catalogs",
    "analogue": "analog",
    "travelling": "traveling", "travelled": "traveled",
    "traveller": "traveler", "travellers": "travelers",
    "cancelled": "canceled", "cancelling": "canceling",
    "labelled": "labeled", "labelling": "labeling",
    "modelled": "modeled", "modelling": "modeling",
    "signalled": "signaled", "signalling": "signaling",
    "fuelled": "fueled", "fuelling": "fueling",
    "levelled": "leveled", "levelling": "leveling",
    "tunnelled": "tunneled", "tunnelling": "tunneling",
    "counsellor": "counselor", "counsellors": "counselors",
    "jewellery": "jewelry",
    "storey": "story", "storeys": "stories",
    "tyre": "tire", "tyres": "tires",
    "kerb": "curb", "kerbs": "curbs",
    "plough": "plow", "ploughs": "plows",
    "draught": "draft", "draughts": "drafts",
    "cheque": "check", "cheques": "checks",
    "grey": "gray", "greys": "grays", "greyish": "grayish",
    "mould": "mold", "moulds": "molds", "moulded": "molded",
    "mouldy": "moldy",
    "smoulder": "smolder", "smouldering": "smoldering",
    "aluminium": "aluminum",
    "sceptical": "skeptical", "sceptic": "skeptic",
    "scepticism": "skepticism",
    "encyclopaedia": "encyclopedia", "encyclopaedias": "encyclopedias",
    "cosy": "cozy", "cosier": "cozier", "cosiest": "coziest",
    "doughnut": "donut", "doughnuts": "donuts",
    "pyjamas": "pajamas",
    "moustache": "mustache",
    "aeroplane": "airplane", "aeroplanes": "airplanes",
    "maths": "math",
    "towards": "toward",
    "whilst": "while",
    "amongst": "among",
    "learnt": "learned",
    "spelt": "spelled",
    "dreamt": "dreamed",
    "burnt": "burned",
    "leapt": "leaped",
    "spoilt": "spoiled",
    "enrol": "enroll", "enrolment": "enrollment", "enrolments": "enrollments",
    "fulfil": "fulfill", "fulfils": "fulfills",
    "fulfilment": "fulfillment",
    "instalment": "installment", "instalments": "installments",
    "skilful": "skillful", "skilfully": "skillfully",
    "wilful": "willful",
    "appal": "appall",
    "distil": "distill",
    "per cent": "percent",
    "postcode": "zip code", "postcodes": "zip codes",
    "nought": "zero",
}

VOCAB = [
    "petrol", "lorry", "lorries", "queue", "queues", "queuing", "queueing",
    "biscuit", "biscuits", "crisps", "chips", "jumper", "trainers", "trousers",
    "mobile phone", "mobile phones", "flat", "flats", "lift", "lifts",
    "holiday", "holidays", "rubbish", "pavement", "autumn", "fortnight",
    "chemist", "pharmacy", "nappy", "pram", "torch", "car park", "motorway",
    "timetable", "revise", "revision", "mark", "marks", "term", "terms",
    "post", "posted", "postman", "parcel", "shop", "shops", "film", "films",
    "cinema", "takeaway", "serviette", "aubergine", "courgette", "beetroot",
    "prawn", "prawns", "mince", "candy", "sweets", "pudding", "scone",
    "squash", "fizzy", "lemonade", "cooker", "hob", "tap", "taps",
    "dustbin", "bin", "bins", "loo", "toilet", "toilets", "wardrobe",
    "cot", "off-licence", "estate agent", "terraced", "bungalow",
    "ground floor", "flatmate", "flatmates", "garden", "gardens",
    "zebra crossing", "roundabout", "bonnet", "boot", "windscreen",
    "number plate", "indicator", "handbrake", "estate car", "saloon",
    "coach", "railway", "carriage", "underground", "tube", "postcard",
    "rucksack", "plaster", "paracetamol", "GP", "surgery", "A&E",
    "holidaymaker", "self-catering", "en suite", "sun cream", "single",
    "return", "return ticket", "single ticket", "booking", "book a table",
    "primary school", "secondary school", "university", "headmaster",
    "headteacher", "school report", "hall of residence", "fresher",
    "dissertation", "CV", "redundancy", "sacked", "current account",
    "cash machine", "cashpoint", "chequebook", "building society",
    "council tax", "DIY", "letting agent", "holiday pay",
]

KEEP = [
    "British", "Britain", "BBC", "London", "Manchester", "Bristol",
    "Scotland", "Wales", "NHS", "pound", "pounds", "£",
]

SKIP_DIRS = {".git", ".venv", "node_modules", "__pycache__",
             ".cloud-attachments", "screenshots", "brand", "Fluentify website",
             "android", "fonts", "lexicon", "nlp"}
SKIP_NAMES = {"audit_british.py", "index.html"}


def sources():
    for path in sorted(ROOT.rglob("*")):
        if path.suffix not in (".json", ".py", ".js", ".html"):
            continue
        rel = path.relative_to(ROOT)
        if any(part in SKIP_DIRS for part in rel.parts):
            continue
        if path.name in SKIP_NAMES or path.name.endswith(".min.js"):
            continue
        yield rel, path.read_text(encoding="utf-8", errors="replace")


TOKEN = re.compile(r"[A-Za-z][A-Za-z'’\-]*")


def count(text, words, ignore_case=True):
    """One pass over the text, not one regex per word: the corpus is 15 MB and
    a compiled pattern per form made this take minutes."""
    wanted = {w.lower(): w for w in words} if ignore_case else {w: w for w in words}
    out = Counter()
    for token in TOKEN.findall(text):
        key = token.lower() if ignore_case else token
        if key in wanted:
            out[wanted[key]] += 1
        # a hyphenated form also counts its parts: "off-licence" -> licence
        if "-" in key and ignore_case:
            for part in key.split("-"):
                if part in wanted:
                    out[wanted[part]] += 1
    if ignore_case:
        low = text.lower()
        for form in words:
            if " " in form:
                n = low.count(form)
                if n:
                    out[form] += n
    return out


def snippet(text, form):
    m = re.search(r"(?<![A-Za-z])" + re.escape(form) + r"(?![A-Za-z])",
                  text, re.IGNORECASE)
    if not m:
        return ""
    i = max(0, m.start() - 80)
    return text[i:m.end() + 80].replace("\n", " ")


def main():
    spelling = Counter()
    vocab = Counter()
    keep = Counter()
    per_file = defaultdict(Counter)
    samples = defaultdict(list)
    for rel, text in sources():
        s = count(text, SPELLING)
        v = count(text, VOCAB)
        k = count(text, KEEP, ignore_case=False)
        spelling.update(s)
        vocab.update(v)
        keep.update(k)
        if s or v:
            per_file[str(rel)].update(s)
            per_file[str(rel)].update(v)
        for form in s:
            if len(samples[form]) < 2:
                samples[form].append(f"{rel}: {snippet(text, form)}")

    print(f"SPELLING: {sum(spelling.values())} occurrences of {len(spelling)} forms "
          f"in {len([f for f in per_file if any(x in SPELLING for x in per_file[f])])} files")
    for form, n in spelling.most_common():
        print(f"  {n:5d}  {form} -> {SPELLING[form]}")
        for line in samples[form][:1]:
            print(f"          {line}")
    print(f"\nVOCAB: {sum(vocab.values())} occurrences of {len(vocab)} context-dependent terms")
    for form, n in vocab.most_common(40):
        print(f"  {n:5d}  {form}")
    print("\nKEPT (proper nouns / institutions): " +
          ", ".join(f"{k}:{v}" for k, v in keep.most_common()) or "none")
    print("\nby file")
    for rel, c in sorted(per_file.items(), key=lambda kv: -sum(kv[1].values()))[:40]:
        print(f"  {sum(c.values()):5d}  {rel}  " +
              ", ".join(f"{k}:{v}" for k, v in c.most_common(6)))
    return 0


if __name__ == "__main__":
    sys.exit(main())
