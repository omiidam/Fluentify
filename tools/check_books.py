#!/usr/bin/env python3
"""The library: are the books sound, and is the panel wired to them?

books.json is content, so the first thing this suite does is read it the way a
learner would. A word book has lessons, a lesson has words, and a word has a
Persian meaning, an English definition and sentences that use it - a word with
no example is a word the page can only show half of. The grammar book teaches
structures instead: a rule, a pattern, examples, exercises and a short exam,
and it is judged on whether a learner could practice from it. Both kinds of gap
are invisible in a diff and obvious on the screen.

The second half is the wiring, because the panel is built from four separate
anchors - the tile in the header, the entry in Panels.TILES, the rule that
shows it, and the loader that fetches the catalog - and any one of them going
missing leaves a button that does nothing or a panel that opens blank. That has
happened once here already, to the Review panel.

The third is the offline build. The APK has no server, so the panel reads
data/books.json out of its own assets; if the file is not copied into the
bundle the panel works on the web and fails on the phone.

    python3 tools/check_books.py
"""

from __future__ import annotations

import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
BOOKS = ROOT / "books.json"
PAGE = ROOT / "webapp.py"
BUILD = ROOT / "build_apk_ui.py"
BUILT = ROOT / "android/app/src/main/assets/www/index.html"
APK_DATA = ROOT / "android/app/src/main/assets/www/data/books.json"

# Persian letters, without the digits and punctuation that share the block: a
# meaning made of "۳" alone would not be a translation.
FA_LETTER = re.compile(r"[\u0621-\u064A\u066E-\u06D3\u06FA-\u06FF]")
LATIN = re.compile(r"[A-Za-z]")
WORD_SHAPE = re.compile(r"^[a-z][a-z'’\- ]*[a-z]$")

# The lessons this panel was built for, in the book's own order. A mistyped or
# missing headword passes every shape check and only a reader would notice, so
# the roster is pinned here and compared word by word.
PINNED_LESSONS = {
    1: [
        "abandon", "keen", "jealous", "tact", "oath", "vacant",
        "hardship", "gallant", "data", "unaccustomed", "bachelor", "qualify",
    ],
    2: [
        "dismal", "wager", "peril", "recline", "shriek", "sinister",
        "conceal", "inhabit", "frigid", "numb", "corpse", "tempt",
    ],
    3: [
        "annual", "blend", "minimum", "talent", "persuade", "visible",
        "typical", "devise", "essential", "wholesale", "scarce", "expensive",
    ],
    4: [
        "humid", "vanish", "dense", "predict", "villain", "vapor",
        "enormous", "theory", "utilize", "descend", "eliminate", "circulate",
    ],
    5: [
        "rural", "campus", "evade", "majority", "assemble", "tradition",
        "burden", "explore", "reform", "topic", "probe", "debate",
    ],
    6: [
        "thorough", "undoubtedly", "approach", "popular", "neglect",
        "employee", "defect", "deceive", "defraud", "detect", "client",
        "comprehensive",
    ],
    7: [
        "preserve", "gloomy", "consent", "unique", "resent", "denounce",
        "molest", "unforeseen", "torrent", "postpone", "capsule", "massive",
    ],
    8: [
        "weird", "valid", "obvious", "mediocre", "reluctant", "exaggerate",
        "security", "bulky", "amateur", "variety", "prominent", "survive",
    ],
    9: [
        "vicinity", "document", "century", "conclude", "undeniable", "resist",
        "lack", "ignore", "challenge", "miniature", "source", "rage",
    ],
    10: [
        "excel", "feminine", "mount", "compete", "dread", "masculine",
        "menace", "tendency", "underestimate", "victorious", "numerous",
        "flexible",
    ],
    11: [
        "evidence", "solitary", "vision", "frequent", "glimpse", "recent",
        "decade", "hesitate", "absurd", "conflict", "minority", "fiction",
    ],
    12: [
        "frank", "audible", "urgent", "urban", "ignite", "prohibit",
        "pollute", "decrease", "abolish", "population", "reveal", "adequate",
    ],
    13: [
        "commence", "migrate", "gleam", "famine", "vessel", "identify",
        "observant", "editor", "revive", "persist", "hazy", "journalist",
    ],
    14: [
        "unruly", "rival", "violent", "brutal", "opponent", "brawl",
        "duplicate", "vicious", "whirling", "underdog", "thrust",
        "bewildered",
    ],
    15: [
        "expand", "alter", "mature", "sacred", "revise", "pledge",
        "casual", "pursue", "unanimous", "fortunate", "pioneer",
        "innovative",
    ],
    16: [
        "grateful", "doubt", "slender", "cautious", "accurate", "penetrate",
        "pierce", "vast", "surpass", "capacity", "confident", "microscope",
    ],
    17: [
        "avoid", "aware", "quantity", "appeal", "wretched", "harsh",
        "misfortune", "opt", "wary", "keg", "nourish", "addict",
    ],
    18: [
        "reckless", "ingenious", "economical", "rave", "glance", "budget",
        "manipulate", "lubricate", "tragedy", "horrid", "pedestrian",
        "nimble",
    ],
    19: [
        "ban", "quota", "abundant", "absorbed", "appropriate", "estimate",
        "uneasy", "panic", "harvest", "calculated", "morsel", "threat",
    ],
    20: [
        "perish", "jagged", "captive", "crafty", "linger", "defiant",
        "ambush", "prosper", "emerge", "devour", "vigor", "fragile",
    ],
    21: [
        "transmit", "confirm", "verify", "detour", "weary", "merit",
        "plea", "collide", "relieve", "dilemma", "baffle", "anticipate",
    ],
    22: [
        "delinquent", "penalize", "vocation", "homicide", "acknowledge",
        "reject", "warden", "spouse", "unstable", "deprived", "justice",
        "beneficiary",
    ],
    23: [
        "embrace", "forbid", "proceed", "reptile", "partial", "logical",
        "rarely", "exhibit", "prior", "precaution", "valiant", "extract",
    ],
    24: [
        "authority", "encourage", "symbol", "vermin", "neutral", "consider",
        "fierce", "wail", "trifle", "detest", "scowl", "sneer",
    ],
    25: [
        "baggage", "calamity", "pauper", "collapse", "architect",
        "prosecute", "squander", "fugitive", "bigamy", "abroad", "envy",
        "matrimony",
    ],
    26: [
        "quench", "guide", "respond", "beckon", "venture", "compel",
        "awesome", "betray", "possible", "pacify", "utter", "awkward",
    ],
    27: [
        "feeble", "cease", "rash", "exhausted", "monarch", "disrupt",
        "thrifty", "rapidly", "severity", "unite", "despite", "miserly",
    ],
    28: [
        "undernourished", "disclose", "disaster", "outlaw", "excessive",
        "culprit", "promote", "illustrate", "insist", "censor", "juvenile",
        "bait",
    ],
    29: [
        "exempt", "repetition", "blunder", "comprehend", "toil", "maim",
        "commend", "final", "mourning", "vain", "subside", "daze",
    ],
    30: [
        "appoint", "mortal", "occupant", "depict", "site", "verse",
        "quarter", "quote", "novel", "attract", "morality", "roam",
    ],
    31: [
        "idle", "dispute", "commuter", "valor", "vein", "uneventful",
        "lunatic", "jest", "confine", "patriotic", "fertile", "idol",
    ],
    32: [
        "distress", "maximum", "flee", "torment", "loyalty", "apologize",
        "colleague", "signify", "refer", "diminish", "mythology",
        "vulnerable",
    ],
    33: [
        "mumble", "wad", "retain", "volunteer", "jolly", "prejudice",
        "hinder", "mute", "abuse", "shrill", "lecture", "witty",
    ],
    34: [
        "adolescent", "candidate", "radical", "spontaneous", "vaccinate",
        "utensil", "sensitive", "temperate", "untidy", "coeducational",
        "precede", "skim",
    ],
    35: [
        "lottery", "obtain", "movie theater", "event", "soar", "stationary",
        "subsequent", "discard", "relate", "vague", "finance", "elevate",
    ],
    36: [
        "prompt", "soothe", "redeem", "refrain", "harmony", "hasty",
        "tempest", "scorch", "sympathetic", "resume", "illegal", "narcotic",
    ],
    37: [
        "dwindle", "heir", "deliberate", "surplus", "heed", "unify",
        "vandal", "abide", "drought", "summit", "traitor", "majestic",
    ],
    38: [
        "tumult", "swarm", "verdict", "biography", "recede", "charity",
        "kneel", "dejected", "tyrant", "drench", "wobble", "obedient",
    ],
    39: [
        "depart", "cancel", "placard", "contagious", "unearth", "customary",
        "scald", "transparent", "legible", "clergy", "debtor", "coincide",
    ],
    40: [
        "obesity", "epidemic", "chiropractor", "ventilated", "oral",
        "magnifying", "obstacle", "pension", "jeopardize", "negative",
        "municipal", "vital",
    ],
    41: [
        "wasp", "parole", "rehabilitate", "multitude", "potential",
        "upholstery", "indifference", "preoccupied", "vertical", "nominate",
        "morgue", "complacent",
    ],
    42: [
        "snub", "wrath", "ponder", "maintain", "endure", "expose", "legend",
        "ballot", "wharf", "resign", "amend", "drastic",
    ],
}

# The second book is organized by week; each week is four days of five words.
PINNED_1100 = {
    1: ["voracious", "indiscriminate", "eminent", "steeped", "replete",
        "abound", "technology", "prognosticate", "automaton", "matron",
        "paradox", "realm", "annals", "compound", "tinge",
        "badger", "implore", "drudgery", "interminable", "perceive"],
    2: ["laconic", "throng", "intrepid", "accost", "reticent",
        "furtive", "felon", "plethora", "hapless", "irate",
        "pretext", "fabricate", "adroit", "gesticulate", "vigilant",
        "avid", "cajole", "rudimentary", "enhance", "nuance"],
    3: ["loathe", "reprimand", "lackluster", "caustic", "wrest",
        "infamous", "jostle", "dupe", "incipient", "inadvertent",
        "ominous", "tremulous", "repudiate", "cessation", "bristle",
        "euphemism", "mundane", "incongruous", "condolence", "stipulate"],
    4: ["alacrity", "disdain", "belligerent", "intimidate", "feint",
        "pugnacious", "promulgate", "brash", "scoff", "belittle",
        "tangible", "laceration", "castigate", "sordid", "octogenarian",
        "solace", "aspirant", "dregs", "frenzy", "scurrilous"],
    5: ["rampant", "inane", "ethics", "concur", "clandestine",
        "flagrant", "admonish", "duress", "culprit", "inexorable",
        "egregious", "distraught", "duplicity", "acrimonious", "paucity",
        "elicit", "pernicious", "tolerate", "construe", "impunity"],
    6: ["affluent", "feasible", "discern", "sally", "consternation",
        "precocious", "perfunctory", "chagrin", "perverse", "deride",
        "disparage", "laudable", "fiasco", "masticate", "eschew",
        "quell", "voluble", "confidant", "obsolescence", "dubious"],
    7: ["implacable", "paroxysm", "reprehensible", "jurisdiction",
        "skirmish", "harass", "monolithic", "indigent", "arbitrary", "fray",
        "stymie", "effigy", "flout", "cognizant", "turbulent",
        "terminate", "forthwith", "exacerbate", "revert", "oust"],
    8: ["emaciated", "surge", "tranquil", "sanctuary", "ascend",
        "malnutrition", "afflict", "besiege", "privation", "sinister",
        "ubiquitous", "remote", "thwart", "harbinger", "malignant",
        "excruciating", "respite", "reverberating", "fretful", "succumb"],
    9: ["impresario", "extortion", "adverse", "asset", "bigot",
        "blatant", "entourage", "virulent", "venom", "spew",
        "loath", "solicit", "astute", "ineffectual", "advocate",
        "scrutinize", "nefarious", "amicable", "vexatious", "malady"],
    10: ["inclement", "peruse", "premonition", "desist", "recoil",
         "pertinent", "mastiff", "obsess", "doleful", "wan",
         "histrionics", "elusive", "frustrate", "symptomatic", "interject",
         "inert", "salient", "imminent", "squeamish", "engrossed"],
    11: ["inundate", "fruitless", "poignant", "garbled", "sanguine",
         "phlegmatic", "corroborate", "comprehensive", "zealous", "coerce",
         "elapse", "meticulous", "domicile", "lax", "sporadic",
         "conjecture", "obviate", "lurid", "quip", "rash"],
    12: ["diatribe", "inhibition", "fortuitous", "incoherent", "ilk",
         "prestigious", "placard", "integral", "remuneration", "nominal",
         "expunge", "flamboyant", "anathema", "schism", "utopia",
         "timorous", "truncated", "jaunty", "fractious", "ostentatious"],
    13: ["importune", "incontrovertible", "surreptitious", "haven",
         "subjugate", "ultimate", "eventuate", "emit", "subterranean",
         "viable", "premise", "jeopardize", "incredulous", "permeate",
         "propitious", "surmise", "curtail", "repress", "cryptic",
         "inchoate"],
    14: ["aspire", "inveigh", "nettle", "overt", "relegate",
         "supine", "mammoth", "repulse", "havoc", "raze",
         "lethal", "scurry", "incisive", "precipitate", "stereotype",
         "stentorian", "singular", "valor", "bias", "sinecure"],
    15: ["complicity", "liquidation", "accomplice", "recant", "culpable",
         "abrogate", "alleged", "access", "invalidate", "preclude",
         "persevere", "landmark", "extrinsic", "declaim", "fetter",
         "paragon", "nomadic", "asperity", "epithet", "controversial"],
    16: ["indigenous", "gregarious", "habitat", "cursory", "interloper",
         "prolific", "bulwark", "sedentary", "frugal", "antithesis",
         "altruistic", "embellish", "cache", "coterie", "cupidity",
         "virtuosity", "temerity", "amorous", "progeny", "saturate"],
    17: ["perpetrate", "consummate", "subterfuge", "concoct", "fallacious",
         "manifold", "assiduous", "impeccable", "fraught", "resourceful",
         "murky", "component", "hoax", "labyrinth", "evaluate",
         "exult", "attest", "gullible", "deploy", "enigma"],
    18: ["abortive", "modify", "accommodate", "spontaneous", "innate",
         "veneer", "myriad", "urbane", "crave", "irrelevant",
         "deem", "inherent", "buff", "romp", "latent",
         "tortuous", "itinerant", "peregrination", "conjugal", "barometer"],
    19: ["megalomania", "profligate", "strife", "legion", "coup",
         "amnesty", "expatriate", "exonerate", "fiat", "mendacious",
         "parsimonious", "pecuniary", "dismantle", "sumptuous", "underwrite",
         "restrictive", "blunt", "nostalgia", "rife", "balk"],
    20: ["revile", "derogatory", "indict", "nebulous", "pesky",
         "redolent", "omnivorous", "disparate", "abstemious", "repose",
         "extant", "vicissitudes", "edifice", "sultry", "trenchant",
         "puissant", "unabated", "maudlin", "levity", "lugubrious"],
    21: ["scion", "indoctrinate", "opulence", "obsequious", "fulsome",
         "lush", "destitution", "ponder", "supplication", "decadence",
         "penance", "ascetic", "desultory", "disciple", "metamorphosis",
         "bona fide", "salvation", "materialism", "nurture", "nirvana"],
    # The book repeats two words from earlier weeks - fabricate (week 2) and
    # bigot (week 17). The library holds one entry per word, so those two are
    # not listed a second time and weeks 22 and 24 carry nineteen.
    22: ["juxtapose", "plight", "covert", "cope", "incompatibility",
         "incapacitated", "connubial", "demur", "appellation",
         "escalation", "indifference", "potential", "cumulative", "recondite",
         "palliate", "delude", "prelude", "chimerical", "acknowledge"],
    23: ["heterogeneous", "gamut", "perspicacious", "analogous", "maladjusted",
         "phenomenon", "mortality", "decade", "susceptible", "neurotic",
         "pedagogue", "enunciate", "inordinate", "irascible", "introspective",
         "perpetuate", "mandate", "compensatory", "neutralize", "catastrophic"],
    24: ["anthropologist", "bizarre", "inanimate", "fetish", "artifact",
         "taboo", "imprudent", "prohibition", "imperative", "taint",
         "universal", "contemptuous", "absurd", "abhor",
         "vulnerable", "entreaty", "tradition", "originate", "inviolable"],
    25: ["awesome", "eruption", "puny", "debris", "dispersed",
         "obliterate", "deplorable", "initiate", "conflagration", "rue",
         "congenial", "hoard", "sage", "aegis", "detriment",
         "longevity", "imbibe", "virile", "senile", "doddering"],
    26: ["lethargic", "prevalent", "paramount", "remiss", "hostile",
         "rebuke", "aversion", "evince", "vogue", "superficial",
         "jettison", "inevitable", "lucrative", "tussle", "intrinsic",
         "acute", "gist", "transient", "terse", "cogent"],
    27: ["pinnacle", "array", "obscure", "ardent", "culminate",
         "constrict", "prodigy", "bereft", "falter", "exultation",
         "vitriolic", "invective", "besmirch", "voluminous", "retrospect",
         "egotist", "humility", "pungent", "inveterate", "adamant"],
    28: ["bedlam", "cacophony", "exploit", "propinquity",
         "disgruntled", "infallible", "panacea", "eradicate", "impede",
         "sedate", "equanimity", "compatible", "serenity", "revere",
         "irrational", "avarice", "insatiable", "nadir", "moribund"],
    29: ["lithe", "obese", "adherent", "bliss", "pathetic",
         "exhort", "apathy", "fracas", "inebriated", "adversary",
         "indolent", "gusto", "garrulous", "banal", "platitude",
         "pique", "dilettante", "atypical", "nondescript", "wane"],
    30: ["extinct", "idyllic", "galvanize", "encumbrance", "gaudy",
         "condescend", "candor", "mortify", "jocose", "malign",
         "omnipotent", "zenith", "fledgling", "peremptory", "precedent",
         "wheedle", "rustic", "jubilant", "decorum", "charlatan"],
    31: ["heresy", "prudent", "ostensible", "fervid", "spurious",
         "propagate", "anomaly", "innocuous", "surfeit", "milieu",
         "strident", "concomitant", "lassitude", "deleterious", "efficacy",
         "dissent", "ferment", "attenuated", "arbiter", "incumbent"],
    # vulnerable (week 24) and bizarre (week 24) recur in weeks 28 and 32.
    32: ["profound", "alleviate", "prodigious", "expedite", "celerity",
         "usurp", "paltry", "condone", "trivial",
         "menial", "venerable", "extraneous", "ambiguous", "succinct",
         "archaic", "emulate", "facetious", "rabid", "salubrious"],
    33: ["complacent", "somber", "debilitate", "impetuous", "occult",
         "discreet", "foment", "glean", "quarry", "slovenly",
         "abjure", "reproach", "penitent", "evanescent", "tantamount",
         "propensity", "wary", "allay", "deter", "connoisseur"],
    34: ["site", "vigil", "cumbersome", "interrogate", "divulge",
         "fluctuate", "unmitigated", "commodious", "antiquated", "disheveled",
         "tenacious", "facade", "asinine", "grimace", "calumny",
         "pittance", "au courant", "fastidious", "noisome", "unkempt"],
    # Four more repeats: equanimity (week 28) in 35, reticent (week 2) in 38,
    # lassitude (week 31) in 40, and intrinsic (week 26) in 41.
    35: ["parable", "whimsical", "lampoon", "countenance", "sanctimonious",
         "effrontery", "nonentity", "flabbergasted", "debacle",
         "vivacious", "gaunt", "mien", "hirsute", "refute",
         "pensive", "whet", "stupor", "wince", "cliche"],
    36: ["genre", "candid", "unsavory", "degrade", "venial",
         "epitome", "dexterity", "grotesque", "compassion", "repugnant",
         "acme", "copious", "vehemently", "depict", "naive",
         "perfidious", "covet", "ingratiate", "penury", "ignominious"],
    37: ["confront", "antipathy", "servile", "volition", "sojourn",
         "austere", "felicitous", "halcyon", "tenable", "superfluous",
         "motivate", "rationalize", "therapy", "nascent", "iconoclast",
         "erudite", "phobia", "germane", "vertigo", "conducive"],
    38: ["glib", "homogeneous", "malleable", "legerdemain", "trend",
         "stagnant", "fatal", "passe", "procrastinate", "facet",
         "foist", "stigmatize", "capitulate", "audacity", "tantalize",
         "retort", "tacit", "chicanery", "docile"],
    39: ["saga", "belated", "decrepit", "imperturbable", "vacillate",
         "staunch", "opprobrium", "machiavellian", "unconscionable", "pandemonium",
         "flay", "demeanor", "delineation", "vindicate", "heinous",
         "turpitude", "infraction", "callous", "redress", "vituperation"],
    40: ["rhetoric", "clique", "extol", "mentor", "facile",
         "cant", "umbrage", "magnanimous", "vilify", "elucidate",
         "vapid", "unwieldy", "proximity", "vitiate",
         "augment", "fatuous", "contort", "repertoire", "imperceptible"],
    41: ["curry", "pall", "succulent", "satiety",
         "potpourri", "sanction", "denote", "allude", "insidious",
         "propriety", "advent", "impious", "proffer", "spate",
         "shibboleth", "bogus", "substantiate", "nutritive", "raucous"],
    # callous (week 39) recurs in week 42 and technology (week 1) in week 44,
    # so both of those weeks carry nineteen words.
    42: ["quandary", "expedient", "negligible", "blase",
         "ennui", "comely", "frenetic", "artifice", "diversity",
         "qualm", "expurgate", "begrudge", "artless", "gratuity",
         "manifest", "delve", "capricious", "requisite", "replenish"],
    43: ["roster", "stunted", "atrophy", "maim", "ameliorate",
         "cynic", "unctuous", "benevolent", "subservient", "iniquity",
         "largess", "criterion", "repent", "mollify", "mercenary",
         "pariah", "aloof", "pragmatic", "vestige", "guise"],
    44: ["nullify", "deluge", "futility", "carnage",
         "libel", "defamatory", "plaintiff", "canard", "deprecate",
         "reputed", "frail", "potent", "excoriate", "devout",
         "diminutive", "profuse", "dulcet", "impromptu", "malevolent"],
    45: ["wistful", "raiment", "brigand", "corpulent", "rail",
         "raconteur", "sullen", "rift", "emissary", "ruminate",
         "taut", "livid", "martinet", "yen", "bagatelle",
         "callow", "appalled", "penchant", "decapitate", "termagant"],
    46: ["ascertain", "dormant", "burgeon", "potentate", "disseminate",
         "derive", "prerogative", "nepotism", "dearth", "internecine",
         "tyro", "sophistry", "factitious", "encomium", "obloquy",
         "hyperbole", "munificent", "prevarication", "charisma", "genocide"],
}
# The grammar book carries no headwords to pin, so its syllabus is pinned
# instead: every structure the book teaches, in the book's own chapter order. A
# lesson dropped or renamed still passes every shape check, and only a reader
# would notice.
PINNED_GRAMMAR = [
    "Simple present and present progressive",
    "Present simple and progressive: affirmative, negative and question forms",
    "Stative verbs: verbs not used in the progressive",
    "Simple past tense",
    "Simple past and past progressive",
    "Was going to: intentions that did not happen",
    "Regular and irregular verbs",
    "The irregular verb list: learning the three forms together",
    "Present perfect with since and for",
    "Present perfect: unspecified time and repeated events",
    "Have and has in spoken English",
    "Present perfect or simple past: which one?",
    "Present perfect progressive: how long an action has lasted",
    "Past perfect",
    "Had in spoken English",
    "Past perfect progressive: how long before another past action",
    "Expressing future time: be going to and will",
    "Forms with be going to",
    "Forms with will",
    "Certainty about the future: definitely, probably, maybe",
    "Be going to or will: which one?",
    "Expressing the future in time clauses",
    "The present progressive and simple present for future time",
    "Future progressive",
    "Future perfect",
    "Summary of verb tenses: the twelve tenses at a glance",
    "Simple tenses: present, past and future",
    "Progressive tenses: an action in progress",
    "Perfect tenses: looking back from a point in time",
    "Perfect progressive: how long an action has lasted",
    "Choosing the tense: a review",
    "Basic agreement: one subject, one verb",
    "Final -s and -es: nouns and verbs",
    "Subjects joined by and, or and nor",
    "Prepositional phrases after the subject",
    "There is and there are; amounts, titles and times",
    "Indefinite pronouns, collective nouns and quantities",
    "Plural forms of nouns: regular and irregular",
    "Possessive nouns: 's, s' and of",
    "Count and noncount nouns: the difference",
    "Noncount nouns: the categories and the surprises",
    "Units of measure with noncount nouns",
    "A few and a little",
    "Many and much",
    "A lot of, lots of and plenty of",
    "Nouns that look plural and are not",
    "Nouns always plural, and nouns with two meanings",
    "The three choices: a, an, the or nothing",
    "A and an: one of many, not known yet",
    "The: known to both people",
    "The: unique things, and the second mention",
    "No article: plural and noncount general statements",
    "A and an with jobs, amounts and rates",
    "No article with names, languages, meals and most places",
    "The with geography, superlatives and ordinals",
    "Common article mistakes: a decision procedure",
    "Personal pronouns: subject and object",
    "Possessive adjectives and possessive pronouns",
    "Reflexive pronouns: myself, yourself, themselves",
    "Pronouns in agreement: everyone, one and they",
    "Indefinite pronouns: someone, anyone, no one, everyone",
    "One and ones: replacing a noun",
    "There and it as empty subjects",
    "Question pronouns: who, whom, whose, which and what",
    "Common pronoun mistakes: between you and me, its and it's",
    "Modals of necessity and advice: must, have to, should",
    "Ability and possibility: can, could, may, might",
    "Requests and suggestions: could you, would you mind, let's",
    "Degrees of certainty: must be, may be, can't be",
    "The passive",
    "The passive with modals, get and stative verbs",
    "Noun clauses and reported speech",
    "The subjunctive in noun clauses: insist that he be",
    "Adjective clauses",
    "Reducing adjective clauses to phrases",
    "Gerunds and infinitives",
    "Causative verbs: make, have, get, let and help",
    "Paired conjunctions and parallel structure",
    "Adverb clauses: time, cause, contrast and condition",
    "Reducing adverb clauses to modifying phrases",
    "Connectives: because of, therefore, so that, otherwise",
    "Conditionals and wishes",
]

POS = {"noun", "verb", "adjective", "adverb", "preposition", "conjunction",
       "pronoun", "determiner", "interjection", "phrase", "expression"}

problems: list[str] = []


def fail(what: str) -> None:
    problems.append(what)


def check(ok: bool, what: str) -> bool:
    if not ok:
        fail(what)
    return ok


def load() -> dict:
    try:
        return json.loads(BOOKS.read_text(encoding="utf-8"))
    except FileNotFoundError:
        fail("books.json is missing from the repository root")
    except json.JSONDecodeError as exc:
        fail(f"books.json does not parse: {exc}")
    return {}


def check_catalog(data: dict) -> dict:
    """Every book, lesson and word, field by field."""
    books = data.get("books")
    if not check(isinstance(books, list) and books, "books.json has no books"):
        return {"books": 0, "lessons": 0, "words": 0,
                "structures": 0, "examples": 0, "exercises": 0, "exam": 0}

    ids: set[str] = set()
    stats = {"books": 0, "lessons": 0, "words": 0,
             "structures": 0, "examples": 0, "exercises": 0, "exam": 0}

    for book in books:
        bid = book.get("id") or "<no id>"
        stats["books"] += 1
        check(isinstance(book.get("id"), str)
              and re.fullmatch(r"[a-z0-9]+(-[a-z0-9]+)*", book["id"] or "") is not None,
              f"{bid}: the id is not a lowercase slug")
        check(bid not in ids, f"{bid}: the id is used twice")
        ids.add(bid)
        check(bool((book.get("title") or "").strip()),
              f"{bid}: no English title")
        check(bool(FA_LETTER.search(book.get("title_fa") or "")),
              f"{bid}: the Persian title has no Persian letters")
        check(bool(book.get("author")), f"{bid}: no author")
        check(bool(FA_LETTER.search(book.get("about_fa") or "")),
              f"{bid}: the Persian blurb has no Persian letters")

        kind = book.get("kind")
        check(kind in (None, "grammar"),
              f"{bid}: kind is {kind!r}, and the panel only knows word books "
              f"and 'grammar'")

        lessons = book.get("lessons")
        if not check(isinstance(lessons, list) and lessons,
                     f"{bid}: has no lessons"):
            continue

        numbers = [l.get("n") for l in lessons]
        check(numbers == list(range(1, len(lessons) + 1)),
              f"{bid}: lessons are not numbered 1..{len(lessons)} in order "
              f"(got {numbers})")

        if kind == "grammar":
            stats["structures"] += len(lessons)
            check_structures(book, lessons, stats)
            continue

        seen_words: dict[str, int] = {}
        for lesson in lessons:
            stats["lessons"] += 1
            where = f"{bid} lesson {lesson.get('n')}"
            check(bool((lesson.get("title") or "").strip()),
                  f"{where}: no title")
            check(bool(FA_LETTER.search(lesson.get("title_fa") or "")),
                  f"{where}: the Persian title has no Persian letters")

            words = lesson.get("words")
            if not check(isinstance(words, list) and words,
                         f"{where}: has no words"):
                continue

            for w in words:
                stats["words"] += 1
                headword = (w.get("word") or "")
                label = f"{where}: {headword or '<no word>'}"
                check(isinstance(headword, str)
                      and WORD_SHAPE.fullmatch(headword or "") is not None
                      and headword == headword.lower(),
                      f"{label}: the headword is not a plain lowercase English word")
                low = headword.lower()
                check(low not in seen_words,
                      f"{label}: the word appears twice in the book "
                      f"(also lesson {seen_words.get(low)})")
                seen_words[low] = lesson.get("n")

                check(bool(FA_LETTER.search(w.get("fa") or "")),
                      f"{label}: no Persian meaning")
                check(bool(LATIN.search(w.get("def_en") or ""))
                      and len((w.get("def_en") or "").split()) >= 3,
                      f"{label}: the English definition is missing or too short")
                check(w.get("pos") in POS,
                      f"{label}: part of speech is {w.get('pos')!r}, "
                      f"not one of {sorted(POS)}")
                ipa = w.get("ipa") or ""
                check(not ipa or ipa.startswith("/") and ipa.endswith("/"),
                      f"{label}: the IPA {ipa!r} is not wrapped in slashes")

                examples = w.get("examples")
                if not check(isinstance(examples, list) and len(examples) >= 2,
                             f"{label}: fewer than two example sentences"):
                    continue
                stem = low[:4]
                for sentence in examples:
                    check(isinstance(sentence, str) and len(sentence.split()) >= 4,
                          f"{label}: an example is too short ({sentence!r})")
                    check(str(sentence).rstrip()[-1:] in ".?!",
                          f"{label}: an example does not end in punctuation "
                          f"({sentence!r})")
                    # the sentence has to actually use the word, or it is an
                    # example of something else
                    check(stem in str(sentence).lower(),
                          f"{label}: the example does not contain the word "
                          f"({sentence!r})")
    return stats


def check_structures(book: dict, lessons: list, stats: dict) -> None:
    """A grammar book is judged differently from a word book.

    There are no headwords here to pin; what makes this book useful is that
    every structure can be practiced from the page. That means a rule that is
    more than a label, examples of the rule in both languages, and exercises
    and an exam whose key exists - an exercise with no answer, or a question
    whose key is not among its options, looks complete in the JSON and teaches
    nothing on the screen.
    """
    bid = book.get("id")
    check(bool(LATIN.search(book.get("about_en") or "")),
          f"{bid}: no English blurb")
    check(bool((book.get("edition") or "").strip()),
          f"{bid}: does not say which edition or publisher it follows")

    # The book has twenty chapters. A syllabus that skips one leaves the learner
    # with a gap they cannot see, because the rest of the book still reads well.
    chapters: set[int] = set()
    for lesson in lessons:
        for number in re.findall(r"\d+", lesson.get("chapter") or ""):
            chapters.add(int(number))
    missing = sorted(set(range(1, 21)) - chapters)
    check(not missing,
          f"{bid}: no structure from chapter(s) {missing}" if missing
          else f"all 20 chapters, {len(lessons)} structures")

    # Every structure points at the chart it follows, so a learner can find the
    # page again. The numbers must be unique and in reading order.
    sections = [str(l.get("section") or "") for l in lessons]
    bad_section = [f"{l.get('n')}:{l.get('section')!r}"
                   for l in lessons
                   if not re.fullmatch(r"\d+(?:-\d+)?", str(l.get("section") or ""))]
    check(not bad_section,
          f"{bid}: a structure has no chart number ({', '.join(bad_section[:6])})"
          if bad_section else f"{len(sections)} chart references")
    check(len(sections) == len(set(sections)),
          f"{bid}: two structures claim the same chart")

    # Chapter one is the chapter the book opens with, and its six charts are
    # what a learner meets first: all of them, in the book's own order.
    first = [str(l.get("section")) for l in lessons
             if l.get("chapter") == "Chapter 1"]
    check(first == ["1-1", "1-2", "1-3", "1-4", "1-5", "1-6"],
          f"{bid}: chapter one is not its six charts in order (got {first})")

    # Chapter two is complete as well: the book's ten perfect-tense charts, in
    # the book's order. A missing chart here is a gap nobody sees, because the
    # rest of the chapter still reads like a finished chapter.
    second = [str(l.get("section")) for l in lessons if l.get("chapter") == "Chapter 2"]
    check(second == [f"2-{i}" for i in range(1, 11)],
          f"{bid}: chapter two is not its ten charts in order (got {second})")

    # Chapter three is complete the same way: the book's ten future-time
    # charts, in the book's order, each one a full structure rather than a
    # heading with a single example under it.
    third = [l for l in lessons if l.get("chapter") == "Chapter 3"]
    check([str(l.get("section")) for l in third] == [f"3-{i}" for i in range(1, 11)],
          f"{bid}: chapter three is not its ten charts in order "
          f"(got {[str(l.get('section')) for l in third]})")
    thin = [str(l.get("section")) for l in third
            if len(l.get("examples") or []) < 3
            or len(l.get("exercises") or []) < 3
            or len(l.get("exam") or []) < 3]
    check(not thin,
          f"{bid}: chapter three chart(s) {thin} are thinner than the rest of the book")

    # Chapter four is the review of verb tenses: one chart per tense family,
    # then the chart that tells a learner how to choose between them.
    fourth = [l for l in lessons if l.get("chapter") == "Chapter 4"]
    check([str(l.get("section")) for l in fourth] == [f"4-{i}" for i in range(1, 6)],
          f"{bid}: chapter four is not its five charts in order "
          f"(got {[str(l.get('section')) for l in fourth]})")
    thin4 = [str(l.get("section")) for l in fourth
             if len(l.get("examples") or []) < 3
             or len(l.get("exercises") or []) < 3
             or len(l.get("exam") or []) < 3]
    check(not thin4,
          f"{bid}: chapter four chart(s) {thin4} are thinner than the rest of the book")

    # Chapter five is agreement: the basic rule, the -s/-es ending, compound
    # subjects, phrases after the subject, there is/are, and the pronouns and
    # collective nouns that look plural and are not.
    fifth = [l for l in lessons if l.get("chapter") == "Chapter 5"]
    check([str(l.get("section")) for l in fifth] == [f"5-{i}" for i in range(1, 7)],
          f"{bid}: chapter five is not its six charts in order "
          f"(got {[str(l.get('section')) for l in fifth]})")
    thin5 = [str(l.get("section")) for l in fifth
             if len(l.get("examples") or []) < 3
             or len(l.get("exercises") or []) < 3
             or len(l.get("exam") or []) < 3]
    check(not thin5,
          f"{bid}: chapter five chart(s) {thin5} are thinner than the rest of the book")

    # Chapter six is nouns: the plural, the possessive, count against noncount,
    # the units a noncount noun is counted in, the quantifiers, and the nouns
    # whose -s lies about their number.
    sixth = [l for l in lessons if l.get("chapter") == "Chapter 6"]
    check([str(l.get("section")) for l in sixth] == [f"6-{i}" for i in range(1, 11)],
          f"{bid}: chapter six is not its ten charts in order "
          f"(got {[str(l.get('section')) for l in sixth]})")
    thin6 = [str(l.get("section")) for l in sixth
             if len(l.get("examples") or []) < 3
             or len(l.get("exercises") or []) < 3
             or len(l.get("exam") or []) < 3]
    check(not thin6,
          f"{bid}: chapter six chart(s) {thin6} are thinner than the rest of the book")

    # Chapter seven is the article: the four choices, the indefinite, the two
    # ways the becomes identifiable, the three places English uses nothing,
    # the fixed patterns, and the procedure that settles a whole paragraph.
    seventh = [l for l in lessons if l.get("chapter") == "Chapter 7"]
    check([str(l.get("section")) for l in seventh] == [f"7-{i}" for i in range(1, 10)],
          f"{bid}: chapter seven is not its nine charts in order "
          f"(got {[str(l.get('section')) for l in seventh]})")
    thin7 = [str(l.get("section")) for l in seventh
             if len(l.get("examples") or []) < 3
             or len(l.get("exercises") or []) < 3
             or len(l.get("exam") or []) < 3]
    check(not thin7,
          f"{bid}: chapter seven chart(s) {thin7} are thinner than the rest of the book")

    # Chapter eight is the pronoun: personal, possessive, reflexive, the
    # agreement question, the indefinite set, one/ones, the empty subjects,
    # the question words, and the mistakes that survive spellcheck.
    eighth = [l for l in lessons if l.get("chapter") == "Chapter 8"]
    check([str(l.get("section")) for l in eighth] == [f"8-{i}" for i in range(1, 10)],
          f"{bid}: chapter eight is not its nine charts in order "
          f"(got {[str(l.get('section')) for l in eighth]})")
    thin8 = [str(l.get("section")) for l in eighth
             if len(l.get("examples") or []) < 3
             or len(l.get("exercises") or []) < 3
             or len(l.get("exam") or []) < 3]
    check(not thin8,
          f"{bid}: chapter eight chart(s) {thin8} are thinner than the rest of the book")

    # The panel shelves a grammar book by chapter, so the book has to name its
    # chapters: a number alone would leave every section headed "Chapter 9"
    # with no sign of what chapter nine is about.
    listed = book.get("chapters") or []
    numbers = [c.get("n") for c in listed]
    check(numbers == list(range(1, 21)),
          f"{bid}: the chapter list is not twenty chapters in order (got {numbers})")
    taught = sorted({int(n) for l in lessons
                     for n in re.findall(r"\d+", l.get("chapter") or "")})
    check(sorted(numbers) == taught,
          f"{bid}: a chapter is taught but not named ({sorted(set(taught) - set(numbers))})"
          if set(taught) - set(numbers)
          else f"{bid}: the chapter list names a chapter nothing is taught from")
    unnamed = [c.get("n") for c in listed
               if not (c.get("title") or "").strip()
               or not FA_LETTER.search(c.get("title_fa") or "")]
    check(not unnamed,
          f"{bid}: chapter(s) {unnamed} have no name in both languages")

    titles: list[str] = []
    for lesson in lessons:
        where = f"{bid} structure {lesson.get('n')}"
        title = (lesson.get("title") or "").strip()
        titles.append(title.lower())
        check(bool(title), f"{where}: no title")
        check(bool(FA_LETTER.search(lesson.get("title_fa") or "")),
              f"{where}: the Persian title has no Persian letters")
        check(bool((lesson.get("chapter") or "").strip()),
              f"{where}: does not say which chapter of the book it follows")

        use_en = (lesson.get("use_en") or "").strip()
        check(LATIN.search(use_en) is not None and len(use_en.split()) >= 10,
              f"{where}: the rule is thinner than a sentence ({use_en!r})")
        check(bool(FA_LETTER.search(lesson.get("use_fa") or "")),
              f"{where}: the Persian rule has no Persian letters")
        form = (lesson.get("form_en") or "").strip()
        check(LATIN.search(form) is not None and len(form.split()) >= 3,
              f"{where}: no pattern line ({form!r})")

        # English first, then Persian: every block is read from the top down, so
        # the order of the fields is the order a learner sees, and a Persian
        # line that slipped above its English is a block read backwards.
        keys = list(lesson)
        check(keys.index("title") < keys.index("title_fa")
              and keys.index("use_en") < keys.index("use_fa")
              and keys.index("form_en") < keys.index("examples"),
              f"{where}: the English fields do not come before the Persian")

        examples = lesson.get("examples") or []
        stats["examples"] += len(examples)
        if check(isinstance(examples, list) and len(examples) >= 3,
                 f"{where}: fewer than three examples"):
            for ex in examples:
                en = (ex.get("en") or "").strip()
                check(len(en.split()) >= 4 and en[-1:] in ".?!",
                      f"{where}: an example is not a sentence ({en!r})")
                check(bool(FA_LETTER.search(ex.get("fa") or "")),
                      f"{where}: an example has no Persian ({en!r})")
                check(list(ex)[:2] == ["en", "fa"],
                      f"{where}: an example is not English then Persian ({en!r})")

        exercises = lesson.get("exercises") or []
        stats["exercises"] += len(exercises)
        if check(isinstance(exercises, list) and len(exercises) >= 3,
                 f"{where}: fewer than three exercises"):
            for ex in exercises:
                prompt = (ex.get("prompt") or "").strip()
                check(len(prompt.split()) >= 3,
                      f"{where}: an exercise prompt is too short ({prompt!r})")
                answer = (ex.get("answer") or "").strip()
                check(bool(answer) and len(answer.split()) <= 8,
                      f"{where}: an exercise has no usable answer ({prompt!r})")
                check(bool((ex.get("why_en") or "").strip()),
                      f"{where}: an exercise answer is not explained ({prompt!r})")
                check(bool(FA_LETTER.search(ex.get("why_fa") or "")),
                      f"{where}: an exercise explanation has no Persian")
                check(list(ex).index("why_en") < list(ex).index("why_fa"),
                      f"{where}: an exercise explains in Persian before English")

        exam = lesson.get("exam") or []
        stats["exam"] += len(exam)
        if check(isinstance(exam, list) and len(exam) >= 3,
                 f"{where}: fewer than three exam questions"):
            for q in exam:
                text = (q.get("q") or "").strip()
                check(len(text.split()) >= 4 and text[-1:] in "?.",
                      f"{where}: an exam question is not a question ({text!r})")
                options = q.get("options") or []
                check(isinstance(options, list) and len(options) == 3,
                      f"{where}: not three options ({text!r})")
                answer = (q.get("answer") or "").strip()
                check(answer in [str(o).strip() for o in options],
                      f"{where}: the key {answer!r} is not one of {options}")
                check(bool((q.get("why_en") or "").strip())
                      and bool(FA_LETTER.search(q.get("why_fa") or "")),
                      f"{where}: an exam answer is not explained in both "
                      f"languages ({text!r})")
                check(list(q).index("why_en") < list(q).index("why_fa"),
                      f"{where}: an exam answer explains in Persian before "
                      f"English ({text!r})")

    check(len(titles) == len(set(titles)),
          f"{bid}: a structure is taught twice")

    # Every chapter-one structure stands on its own: the rule, the pattern,
    # three examples, three exercises and three exam questions.
    thin = [f"{l.get('section')}: {len(l.get('examples') or [])}/"
            f"{len(l.get('exercises') or [])}/{len(l.get('exam') or [])}"
            for l in lessons
            if min(len(l.get("examples") or []), len(l.get("exercises") or []),
                   len(l.get("exam") or [])) < 3]
    check(not thin, f"{bid}: a structure is missing practice ({', '.join(thin[:6])})")


def check_panel() -> None:
    """The four anchors that make the tile open a filled panel."""
    src = PAGE.read_text(encoding="utf-8")

    check('id="btoggle"' in src, "there is no Books tile in the header")
    check('id="bpanel"' in src, "there is no #bpanel in the markup")
    check('id="bbooks"' in src, "the panel has no slot to draw the shelf into")

    tiles = re.search(r"const TILES = \{(.*?)\};", src, re.S)
    check(bool(tiles) and "bpanel: 'btoggle'" in (tiles.group(1) if tiles else ""),
          "Panels.TILES does not map bpanel to btoggle, so the tile cannot "
          "open or close the panel")

    check("getElementById('btoggle').onclick" in src,
          "the Books tile has no click handler")
    check(re.search(r"bpanel: \(\) => Books\.load\(\)", src) is not None,
          "opening the panel does not load the catalog")
    check(re.search(r"loadJSON\('books'\)", src) is not None,
          "the panel does not read books.json")

    # hidden until opened, and shown when it is - both halves, because a panel
    # in only one of the two lists is either always on screen or never is
    hidden = re.findall(r"#bpanel\b[^{]*\{\s*display:\s*none", src)
    check(bool(hidden), "no rule hides #bpanel, so it would sit in the flow")
    shown = re.search(r"#bpanel\.open[^{]*\{\s*display:\s*block", src)
    check(bool(shown), "#bpanel is hidden but nothing shows it when it opens")
    check(re.search(r"#bpanel \{\s*display:\s*none", src) is None
          or bool(shown), "#bpanel.open never overrides the hidden state")

    # direction is declared per element in this panel: the whole point of the
    # dictionary bug was that a mixed line is laid out by its first strong
    # character, so a Persian meaning must be its own rtl block
    check("fa.dir = 'rtl'" in src,
          "the Persian meaning is not marked rtl in the library")
    check("def.dir = 'ltr'" in src,
          "the English definition is not marked ltr in the library")

    # the route has to precede the chat fallback or every request becomes a reply
    route = src.find('"/api/books"')
    check(route != -1, "there is no /api/books route")
    if route != -1:
        chat = src.find('elif self.path.startswith("/api/chat")')
        check(chat == -1 or route < chat,
              "the /api/books route sits after the chat fallback")

    # typed navigation: "open books" / "کتاب‌ها را باز کن"
    check(re.search(r"\bbooks: \{\s*panel: 'bpanel'", src) is not None,
          "the library is not reachable by typing its name")

    # ---- the grammar book draws a structure, not a word ------------------
    check("paintStructure(box, book)" in src,
          "the panel never draws a structure, so a grammar lesson opens blank")
    check(re.search(r"book\.kind === 'grammar'", src) is not None,
          "the panel does not tell a grammar book from a word book")
    check("isGrammar(book)" in src,
          "the shelf counts a grammar book's contents as words")
    # each structure carries its rule, its pattern, examples, exercises and an
    # exam; every one of those has to be drawn or the data is wasted
    check("class = 'bform'" in src or "className = 'bform'" in src,
          "the pattern line of a structure is never drawn")
    check("label('Examples', 'مثال‌ها')" in src,
          "the examples of a structure are never drawn")
    check("label('Exercises', 'تمرین‌ها')" in src,
          "the exercises of a structure are never drawn")
    check("label('Exam', 'آزمون')" in src,
          "the exam questions of a structure are never drawn")
    check("this.answer(item.answer" in src,
          "an exercise or exam question has no answer attached")
    # the key is folded away, not merely styled away
    check("ans.setAttribute('hidden', '')" in src,
          "the answer is not hidden until the learner asks for it")
    check("ans.removeAttribute('hidden')" in src,
          "the answer can never be unfolded once hidden")
    check("item.options || []" in src,
          "the three options of an exam question are never drawn")
    # the shelf has to name the book by what it teaches, and its author
    check("' structure' : ' structures'" in src,
          "the shelf still calls a grammar book's structures lessons")
    check("this.examplesOf(book)" in src,
          "the shelf does not say how many examples a grammar book holds")
    # the list and the structure both carry the book's own chart number, so a
    # lesson can be found in the printed chapter it came from
    check("lesson.section" in src,
          "the panel never shows which chart a structure follows")
    check("'Chart ' + lesson.section" in src,
          "a structure does not name its chart")

    # the chapters are sections of the panel, not one long list of charts
    check("paintChapters(box, book)" in src,
          "the panel has no chapter level, so every structure is one flat list")
    check("'Chapter ' + group.n" in src,
          "a chapter section does not say which chapter it is")
    check("this.lessonTile(book, lesson)" in src,
          "the charts are not drawn as tiles inside their chapter")
    check("this.chaptersOf(book)" in src,
          "the shelf does not say how many chapters a grammar book covers")


def check_offline() -> None:
    """The APK has no server, so the same file has to be in its assets."""
    build = BUILD.read_text(encoding="utf-8")
    check('"books.json"' in build,
          "build_apk_ui.py does not copy books.json into the offline bundle")
    check("LAZY_DATA" in build,
          "the offline build has no place for a lazily-read data file")

    if BUILT.exists():
        built = BUILT.read_text(encoding="utf-8")
        check("loadJSON('books')" in built,
              "the built page does not read books.json from its own assets")
        check('id="bpanel"' in built,
              "the built page has no Books panel")
        check("id=\"btoggle\"" in built,
              "the built page has no Books tile")
    if APK_DATA.exists() and BOOKS.exists():
        check(APK_DATA.read_bytes() == BOOKS.read_bytes(),
              "the APK's copy of books.json is out of date - "
              "run python3 build_apk_ui.py")


def main() -> int:
    data = load()
    blank = {"books": 0, "lessons": 0, "words": 0,
             "structures": 0, "examples": 0, "exercises": 0, "exam": 0}
    stats = check_catalog(data) if data else blank

    other = next((b for b in data.get("books", []) if b.get("id") == "1100-words"),
                 None)
    if check(other is not None, "the 1100 book is not in the library"):
        lessons = {l.get("n"): l for l in other.get("lessons") or []}
        for number, roster in PINNED_1100.items():
            lesson = lessons.get(number)
            if not check(lesson is not None,
                         f"1100 week {number} is missing"):
                continue
            words = [w.get("word") for w in lesson.get("words") or []]
            check(words == roster,
                  f"1100 week {number} is not its words in order: {words}")
            days = {w.get("day") for w in lesson.get("words") or []}
            check(days and None not in days,
                  f"1100 week {number} has words with no day")

    book = next((b for b in data.get("books", []) if b.get("id") == "essential-504"), None)
    if check(book is not None, "the 504 book is not in the library"):
        lessons = {l.get("n"): l for l in book.get("lessons") or []}
        for number, roster in PINNED_LESSONS.items():
            lesson = lessons.get(number)
            if not check(lesson is not None,
                         f"504 lesson {number} is missing from the book"):
                continue
            words = [w.get("word") for w in lesson.get("words") or []]
            check(words == roster,
                  f"504 lesson {number} is not the book's twelve words in "
                  f"order: {words}")

    grammar = next((b for b in data.get("books", []) if b.get("kind") == "grammar"),
                   None)
    if check(grammar is not None, "the grammar book is not in the library"):
        check(grammar.get("author") == "Betty S. Azar & Stacy A. Hagen",
              "the grammar book is not credited to its authors "
              f"(got {grammar.get('author')!r})")
        titles = [l.get("title") for l in grammar.get("lessons") or []]
        check(titles == PINNED_GRAMMAR,
              f"the grammar book is not the pinned syllabus in order: {titles}")

    check_panel()
    check_offline()

    if problems:
        for p in problems[:40]:
            print("FAIL  " + p)
        if len(problems) > 40:
            print(f"      ... and {len(problems) - 40} more")
        print(f"\nFAIL  {len(problems)} problem(s) with the library")
        return 1

    print(f"PASS  {stats['books']} book(s), {stats['lessons']} lesson(s), "
          f"{stats['words']} words with a meaning, a definition and examples; "
          f"{stats['structures']} grammar structure(s) with "
          f"{stats['examples']} examples, {stats['exercises']} exercises and "
          f"{stats['exam']} exam questions; the panel is wired to them on the "
          f"page and in the APK bundle")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
