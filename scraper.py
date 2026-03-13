import requests
import feedparser
from datetime import datetime, timezone
from concurrent.futures import ThreadPoolExecutor, as_completed
import re

# ─── SOURCES ─────────────────────────────────────────────────────────────────
SOURCES = [
    {"name": "CyberScoop",            "url": "https://cyberscoop.com/feed/",                                                                                   "type_hint": "News"},
    {"name": "SecurityWeek",          "url": "https://feeds.feedburner.com/securityweek",                                                                      "type_hint": "News"},
    {"name": "Infosecurity Magazine", "url": "https://www.infosecurity-magazine.com/rss/news/",                                                                "type_hint": "News"},
    {"name": "The Record",            "url": "https://therecord.media/feed/",                                                                                  "type_hint": "News"},
    {"name": "Dark Reading",          "url": "https://www.darkreading.com/rss.xml",                                                                            "type_hint": "News"},
    {"name": "The Hacker News",       "url": "https://feeds.feedburner.com/TheHackersNews",                                                                    "type_hint": "News"},
    {"name": "Cybersecurity Dive",    "url": "https://www.cybersecuritydive.com/feeds/news/",                                                                  "type_hint": "News"},
    {"name": "Wired Security",        "url": "https://www.wired.com/feed/category/security/latest/rss",                                                        "type_hint": "News"},
    {"name": "Federal News Network",  "url": "https://federalnewsnetwork.com/category/cybersecurity/feed/",                                                    "type_hint": "Policy"},
    {"name": "Meritalk",              "url": "https://www.meritalk.com/feed/",                                                                                 "type_hint": "Policy"},
    {"name": "Computer Weekly",       "url": "https://www.computerweekly.com/rss/IT-security.xml",                                                             "type_hint": "News"},
    {"name": "Nextgov",               "url": "https://www.nextgov.com/rss/all/",                                                                               "type_hint": "Policy"},
    {"name": "Lawfare",               "url": "https://www.lawfaremedia.org/feed",                                                                              "type_hint": "Policy"},
    {"name": "Tech Policy Press",     "url": "https://techpolicy.press/feed/",                                                                                 "type_hint": "Policy"},
    {"name": "Brookings",             "url": "https://www.brookings.edu/topic/cybersecurity/feed/",                                                            "type_hint": "Academic"},
    {"name": "CSIS",                  "url": "https://www.csis.org/rss.xml",                                                                                   "type_hint": "Academic"},
    {"name": "Atlantic Council",      "url": "https://www.atlanticcouncil.org/feed/",                                                                          "type_hint": "Academic"},
    {"name": "CFR",                   "url": "https://www.cfr.org/rss/all",                                                                                    "type_hint": "Academic"},
    {"name": "Chatham House",         "url": "https://www.chathamhouse.org/rss.xml",                                                                           "type_hint": "Academic"},
    {"name": "RAND",                  "url": "https://www.rand.org/pubs/rss/all.xml",                                                                          "type_hint": "Academic"},
    {"name": "National Law Review",   "url": "https://www.natlawreview.com/topic/cybersecurity/feed",                                                          "type_hint": "Regulatory"},
    {"name": "BakerHostetler",        "url": "https://www.bakerdatacounsel.com/feed/",                                                                         "type_hint": "Regulatory"},
    {"name": "Wiley Rein",            "url": "https://www.wileyconnect.com/feed/",                                                                             "type_hint": "Regulatory"},
    {"name": "Foley Insights",        "url": "https://www.foley.com/insights/rss/",                                                                            "type_hint": "Regulatory"},
    {"name": "Politico Cyber",        "url": "https://news.google.com/rss/search?q=politico+cybersecurity+policy&hl=en-US&gl=US&ceid=US:en",                   "type_hint": "Policy"},
    {"name": "Axios Codebook",        "url": "https://news.google.com/rss/search?q=axios+codebook+cybersecurity&hl=en-US&gl=US&ceid=US:en",                    "type_hint": "Policy"},
    {"name": "NYDFS",                 "url": "https://news.google.com/rss/search?q=NYDFS+cybersecurity+regulation&hl=en-US&gl=US&ceid=US:en",                  "type_hint": "Regulatory"},
    {"name": "SEC Cyber Rules",       "url": "https://news.google.com/rss/search?q=SEC+cybersecurity+disclosure+rule&hl=en-US&gl=US&ceid=US:en",               "type_hint": "Regulatory"},
    {"name": "CISA Directives",       "url": "https://news.google.com/rss/search?q=CISA+cybersecurity+directive+binding+operational&hl=en-US&gl=US&ceid=US:en","type_hint": "Regulatory"},
    {"name": "NIS2 Directive",        "url": "https://news.google.com/rss/search?q=NIS2+directive+EU+cybersecurity+compliance&hl=en-US&gl=US&ceid=US:en",      "type_hint": "Legislative"},
    {"name": "DORA Regulation",       "url": "https://news.google.com/rss/search?q=DORA+digital+operational+resilience+act+financial&hl=en-US&gl=US&ceid=US:en","type_hint": "Legislative"},
    {"name": "EU AI Act Cyber",       "url": "https://news.google.com/rss/search?q=EU+AI+Act+cybersecurity+compliance+regulation&hl=en-US&gl=US&ceid=US:en",   "type_hint": "Legislative"},
    {"name": "ENISA",                 "url": "https://news.google.com/rss/search?q=ENISA+cybersecurity+regulation+EU&hl=en-US&gl=US&ceid=US:en",               "type_hint": "Regulatory"},
    {"name": "UK NCSC / ICO",         "url": "https://news.google.com/rss/search?q=NCSC+ICO+UK+cybersecurity+regulation+guidance&hl=en-US&gl=US&ceid=US:en",   "type_hint": "Policy"},
    {"name": "Risky Biz",             "url": "https://news.google.com/rss/search?q=risky.biz+cybersecurity+regulation+policy&hl=en-US&gl=US&ceid=US:en",       "type_hint": "News"},
    {"name": "APAC Cyber Reg",        "url": "https://news.google.com/rss/search?q=cybersecurity+regulation+law+australia+singapore+japan+india&hl=en-US&gl=US&ceid=US:en","type_hint": "Regulatory"},
    {"name": "Canada Cyber Policy",   "url": "https://news.google.com/rss/search?q=canada+cybersecurity+regulation+bill+C-26&hl=en-US&gl=US&ceid=US:en",       "type_hint": "Legislative"},
]

# ─── REGULATORY SIGNAL FILTER ────────────────────────────────────────────────
REGULATORY_SIGNALS = [
    "legislat", "bill ", " act ", "statute", "directive", "enacted", "signed into law",
    "proposed rule", "final rule", "rulemaking", "rule-making", "proposed regulation",
    "parliament", "congress", "senate", "house of representatives", "amendment",
    "regulat", "compliance", "enforcement", "enforcement action", "penalty", "fine ",
    "consent order", "supervisory", "regulator", "authority order", "sanction",
    "gdpr", "nis2", "dora ", "hipaa", "sec rule", "nydfs", "cisa order", "ftc order",
    "iso 27001", "soc 2", "pci dss", "fedramp", "cmmc ",
    "policy", "guidance", "framework", "executive order", "memorandum", "advisory",
    "national strategy", "best practice", "standard", "nist ", "oversight", "governance",
    "enisa", "ncsc", "ico ", "bsi ", "anssi", "acsc ", "csa singapore",
    "cyber resilience act", "eu cyber", "ai act", "data act", "data governance act",
    "cfpb", "ferc ", "tsa directive", "fcc rule",
    "think tank", "white paper", "policy paper", "congressional report",
    "government report", "regulatory landscape", "risk assessment framework",
]

CYBER_KEYWORDS = [
    "cyber", "security", "privacy", "data protect", "breach", "hack", "encrypt",
    "ransomware", "vulnerability", "threat", "phishing", "malware", "critical infrastructure",
    "zero trust", "incident response", "data law", "data act", "information security",
]


# ─── US STATES ───────────────────────────────────────────────────────────────
# Each entry: (display_label, [(keyword, weight), ...])
# Minimum score of 3 required to resolve to a specific state label.
# State keywords must be regulatory/legal in nature to avoid false positives
# (e.g., "california" alone won't trigger; "california law" or "cpra" will).

US_STATES = [
    ("🇺🇸 US · Alabama",        [("alabama law", 4), ("alabama regulat", 4), ("alabama legislat", 4), ("alabama data", 3), ("alabama ", 1)]),
    ("🇺🇸 US · Alaska",         [("alaska law", 4), ("alaska regulat", 4), ("alaska legislat", 4), ("alaska data", 3), ("alaska ", 1)]),
    ("🇺🇸 US · Arizona",        [("arizona law", 4), ("arizona regulat", 4), ("arizona legislat", 4), ("arizona data", 3), ("arizona ", 1)]),
    ("🇺🇸 US · Arkansas",       [("arkansas law", 4), ("arkansas regulat", 4), ("arkansas legislat", 4), ("arkansas data", 3), ("arkansas ", 1)]),
    ("🇺🇸 US · California",     [
        ("cpra", 5), ("ccpa", 5), ("california consumer privacy", 5), ("california privacy rights act", 5),
        ("california data", 4), ("california law", 4), ("california regulat", 4), ("california legislat", 4),
        ("california attorney general", 4), ("cppa ", 4), ("ab 375", 4), ("sb 1386", 4),
        ("california ", 1),
    ]),
    ("🇺🇸 US · Colorado",       [("colorado privacy act", 5), ("cpa colorado", 5), ("colorado law", 4), ("colorado regulat", 4), ("colorado legislat", 4), ("colorado data", 3), ("colorado ", 1)]),
    ("🇺🇸 US · Connecticut",    [("connecticut data privacy", 5), ("ctdpa", 5), ("connecticut law", 4), ("connecticut regulat", 4), ("connecticut legislat", 4), ("connecticut ", 1)]),
    ("🇺🇸 US · Delaware",       [("delaware law", 4), ("delaware regulat", 4), ("delaware legislat", 4), ("delaware data", 3), ("delaware ", 1)]),
    ("🇺🇸 US · Florida",        [("florida digital bill of rights", 5), ("fdbr", 5), ("florida law", 4), ("florida regulat", 4), ("florida legislat", 4), ("florida data", 3), ("florida ", 1)]),
    ("🇺🇸 US · Georgia",        [("georgia law", 4), ("georgia regulat", 4), ("georgia legislat", 4), ("georgia data", 3), ("georgia ", 1)]),
    ("🇺🇸 US · Hawaii",         [("hawaii law", 4), ("hawaii regulat", 4), ("hawaii legislat", 4), ("hawaii data", 3), ("hawaii ", 1)]),
    ("🇺🇸 US · Idaho",          [("idaho law", 4), ("idaho regulat", 4), ("idaho legislat", 4), ("idaho data", 3), ("idaho ", 1)]),
    ("🇺🇸 US · Illinois",       [("illinois biometric", 5), ("bipa", 5), ("illinois privacy", 4), ("illinois law", 4), ("illinois regulat", 4), ("illinois legislat", 4), ("illinois data", 3), ("illinois ", 1)]),
    ("🇺🇸 US · Indiana",        [("indiana consumer data", 5), ("indiana law", 4), ("indiana regulat", 4), ("indiana legislat", 4), ("indiana data", 3), ("indiana ", 1)]),
    ("🇺🇸 US · Iowa",           [("iowa data act", 5), ("iowa law", 4), ("iowa regulat", 4), ("iowa legislat", 4), ("iowa data", 3), ("iowa ", 1)]),
    ("🇺🇸 US · Kansas",         [("kansas law", 4), ("kansas regulat", 4), ("kansas legislat", 4), ("kansas data", 3), ("kansas ", 1)]),
    ("🇺🇸 US · Kentucky",       [("kentucky law", 4), ("kentucky regulat", 4), ("kentucky legislat", 4), ("kentucky data", 3), ("kentucky ", 1)]),
    ("🇺🇸 US · Louisiana",      [("louisiana law", 4), ("louisiana regulat", 4), ("louisiana legislat", 4), ("louisiana data", 3), ("louisiana ", 1)]),
    ("🇺🇸 US · Maine",          [("maine law", 4), ("maine regulat", 4), ("maine legislat", 4), ("maine data", 3), ("maine ", 1)]),
    ("🇺🇸 US · Maryland",       [("maryland online data privacy", 5), ("modpa", 5), ("maryland law", 4), ("maryland regulat", 4), ("maryland legislat", 4), ("maryland data", 3), ("maryland ", 1)]),
    ("🇺🇸 US · Massachusetts",  [("massachusetts data law", 5), ("201 cmr", 5), ("massachusetts law", 4), ("massachusetts regulat", 4), ("massachusetts legislat", 4), ("massachusetts data", 3), ("massachusetts ", 1)]),
    ("🇺🇸 US · Michigan",       [("michigan law", 4), ("michigan regulat", 4), ("michigan legislat", 4), ("michigan data", 3), ("michigan ", 1)]),
    ("🇺🇸 US · Minnesota",      [("minnesota law", 4), ("minnesota regulat", 4), ("minnesota legislat", 4), ("minnesota data", 3), ("minnesota ", 1)]),
    ("🇺🇸 US · Mississippi",    [("mississippi law", 4), ("mississippi regulat", 4), ("mississippi legislat", 4), ("mississippi data", 3), ("mississippi ", 1)]),
    ("🇺🇸 US · Missouri",       [("missouri law", 4), ("missouri regulat", 4), ("missouri legislat", 4), ("missouri data", 3), ("missouri ", 1)]),
    ("🇺🇸 US · Montana",        [("montana consumer data privacy", 5), ("montana law", 4), ("montana regulat", 4), ("montana legislat", 4), ("montana data", 3), ("montana ", 1)]),
    ("🇺🇸 US · Nebraska",       [("nebraska data privacy", 5), ("nebraska law", 4), ("nebraska regulat", 4), ("nebraska legislat", 4), ("nebraska ", 1)]),
    ("🇺🇸 US · Nevada",         [("nevada privacy law", 5), ("nevada law", 4), ("nevada regulat", 4), ("nevada legislat", 4), ("nevada data", 3), ("nevada ", 1)]),
    ("🇺🇸 US · New Hampshire",  [("new hampshire law", 4), ("new hampshire regulat", 4), ("new hampshire legislat", 4), ("new hampshire data", 3), ("new hampshire", 1)]),
    ("🇺🇸 US · New Jersey",     [("new jersey law", 4), ("new jersey regulat", 4), ("new jersey legislat", 4), ("new jersey data", 3), ("new jersey", 1)]),
    ("🇺🇸 US · New Mexico",     [("new mexico law", 4), ("new mexico regulat", 4), ("new mexico legislat", 4), ("new mexico data", 3), ("new mexico", 1)]),
    ("🇺🇸 US · New York",       [
        ("nydfs", 5), ("new york shield act", 5), ("ny shield", 5), ("new york privacy act", 5),
        ("nypa ", 5), ("new york department of financial services", 5),
        ("new york law", 4), ("new york regulat", 4), ("new york legislat", 4), ("new york data", 3),
        ("new york attorney general", 4), ("new york ", 4),
    ]),
    ("🇺🇸 US · North Carolina", [("north carolina law", 4), ("north carolina regulat", 4), ("north carolina legislat", 4), ("north carolina data", 3), ("north carolina", 1)]),
    ("🇺🇸 US · North Dakota",   [("north dakota law", 4), ("north dakota regulat", 4), ("north dakota legislat", 4), ("north dakota", 1)]),
    ("🇺🇸 US · Ohio",           [("ohio law", 4), ("ohio regulat", 4), ("ohio legislat", 4), ("ohio data", 3), ("ohio ", 1)]),
    ("🇺🇸 US · Oklahoma",       [("oklahoma law", 4), ("oklahoma regulat", 4), ("oklahoma legislat", 4), ("oklahoma data", 3), ("oklahoma ", 1)]),
    ("🇺🇸 US · Oregon",         [("oregon consumer privacy act", 5), ("ocpa", 5), ("oregon law", 4), ("oregon regulat", 4), ("oregon legislat", 4), ("oregon data", 3), ("oregon ", 1)]),
    ("🇺🇸 US · Pennsylvania",   [("pennsylvania law", 4), ("pennsylvania regulat", 4), ("pennsylvania legislat", 4), ("pennsylvania data", 3), ("pennsylvania ", 1)]),
    ("🇺🇸 US · Rhode Island",   [("rhode island law", 4), ("rhode island regulat", 4), ("rhode island legislat", 4), ("rhode island data", 3), ("rhode island", 1)]),
    ("🇺🇸 US · South Carolina", [("south carolina law", 4), ("south carolina regulat", 4), ("south carolina legislat", 4), ("south carolina", 1)]),
    ("🇺🇸 US · South Dakota",   [("south dakota law", 4), ("south dakota regulat", 4), ("south dakota legislat", 4), ("south dakota", 1)]),
    ("🇺🇸 US · Tennessee",      [("tennessee information protection", 5), ("tipa", 5), ("tennessee law", 4), ("tennessee regulat", 4), ("tennessee legislat", 4), ("tennessee data", 3), ("tennessee ", 1)]),
    ("🇺🇸 US · Texas",          [("texas data privacy", 5), ("tdpsa", 5), ("texas law", 4), ("texas regulat", 4), ("texas legislat", 4), ("texas data", 3), ("texas attorney general", 4), ("texas ", 1)]),
    ("🇺🇸 US · Utah",           [("utah consumer privacy", 5), ("ucpa", 5), ("utah law", 4), ("utah regulat", 4), ("utah legislat", 4), ("utah data", 3), ("utah ", 1)]),
    ("🇺🇸 US · Vermont",        [("vermont law", 4), ("vermont regulat", 4), ("vermont legislat", 4), ("vermont data", 3), ("vermont ", 1)]),
    ("🇺🇸 US · Virginia",       [("virginia consumer data protection", 5), ("vcdpa", 5), ("virginia law", 4), ("virginia regulat", 4), ("virginia legislat", 4), ("virginia data", 3), ("virginia ", 1)]),
    ("🇺🇸 US · Washington",     [("washington my health my data", 5), ("washington privacy act", 5), ("washington law", 4), ("washington regulat", 4), ("washington legislat", 4), ("washington state data", 3), ("washington state", 2)]),
    ("🇺🇸 US · Washington D.C.", [("district of columbia law", 4), ("d.c. law", 4), ("d.c. council", 4), ("washington dc regulat", 3)]),
    ("🇺🇸 US · West Virginia",  [("west virginia law", 4), ("west virginia regulat", 4), ("west virginia legislat", 4), ("west virginia", 1)]),
    ("🇺🇸 US · Wisconsin",      [("wisconsin law", 4), ("wisconsin regulat", 4), ("wisconsin legislat", 4), ("wisconsin data", 3), ("wisconsin ", 1)]),
    ("🇺🇸 US · Wyoming",        [("wyoming law", 4), ("wyoming regulat", 4), ("wyoming legislat", 4), ("wyoming data", 3), ("wyoming ", 1)]),
]

# ─── COUNTRY GEO RULES ───────────────────────────────────────────────────────
# Format: (display_label, min_score_to_win, [(keyword, weight), ...])
#
# IMPORTANT – EU design philosophy:
#   Generic words like "european" or "europe" do NOT score EU points.
#   Only actual EU institutional signals (Commission, Parliament, Council,
#   specific EU laws & agencies) score points.  This prevents a story about
#   "a European hacker" or "European companies" from being tagged EU.
#   The EU also requires a higher minimum score (6) to win over any other
#   region. If EU score is below 6, the article falls through to its next-
#   highest scorer (often a specific member state).

GEO_COUNTRIES = [
    # ── European Union (high threshold — must be genuinely about EU governance) ──
    ("🇪🇺 EU", 6, [
        ("european commission",          6), ("european parliament",           6),
        ("european council",             6), ("council of the european union",6), ("eu regulation",                 5),
        ("eu charter",                   5), ("eu treaty",                     5),
        ("eu directive",                 5), ("eu law",                        5),
        ("enisa",                        5), ("gdpr",                          4),
        ("nis2 directive",               5), ("dora regulation",               5),
        ("eu ai act",                    5), ("cyber resilience act",          5),
        ("eu data act",                  5), ("eu data governance act",        5),
        ("eu cybersecurity act",         5), ("eidas",                         5),
        ("eu member state",              4), ("single market regulat",         4),
        ("brussels regulat",             4), ("europarl",                      4),
        ("eu policy",                    3), ("eu standard",                   3),
        ("eu framework",                 3), ("eu compliance",                 3),
        ("eu supervisory",               3), ("eu enforcement",                3),
    ]),

    # ── United Kingdom ──
    ("🇬🇧 UK", 3, [
        ("ncsc ",                    5), ("ico ",                       5),
        ("uk government",            5), ("uk parliament",              5),
        ("united kingdom law",       5), ("united kingdom regulat",     5),
        ("uk data protection",       5), ("uk gdpr",                    5),
        ("online safety act",        5), ("product security act",       5),
        ("ofcom",                    4), ("fca uk",                     4),
        ("uk cyber",                 4), ("uk regulat",                 4),
        ("uk law",                   4), ("uk policy",                  4),
        ("british government",       4), ("uk attorney general",        3),
        ("england law",              3), ("scotland law",               3),
        (" uk ",                     2), ("britain",                    2),
        ("united kingdom",           2),
    ]),

    # ── EU Member States (individual, scored separately from EU) ──
    ("🇩🇪 Germany", 3, [
        ("bsi ",                     5), ("bundestag",                  5),
        ("german government",        5), ("bundesrat",                  5),
        ("it-sicherheitsgesetz",     5), ("german federal",             5),
        ("german data",              4), ("german law",                 4),
        ("german regulat",           4), ("german cyber",               4),
        ("german parliament",        4), ("germany's law",              4),
        ("berlin government",        3), ("germany ",                   2),
        ("german ",                  1),
    ]),
    ("🇫🇷 France", 3, [
        ("anssi",                    5), ("cnil",                       5),
        ("french government",        5), ("assemblée nationale",        5),
        ("french data",              4), ("french law",                 4),
        ("french regulat",           4), ("french cyber",               4),
        ("france's law",             4), ("paris government",           3),
        ("france ",                  2), ("french ",                    1),
    ]),
    ("🇳🇱 Netherlands", 3, [
        ("dutch authority for",      5), ("ap netherlands",             5),
        ("dutch government",         5), ("dutch data",                 4),
        ("dutch law",                4), ("dutch regulat",              4),
        ("dutch cyber",              4), ("netherlands law",            4),
        ("netherlands regulat",      4), ("hague government",           3),
        ("netherlands ",             2), ("dutch ",                     1),
    ]),
    ("🇮🇪 Ireland", 3, [
        ("dpc ireland",              5), ("irish data protection",      5),
        ("irish government",         5), ("irish law",                  4),
        ("irish regulat",            4), ("ireland cyber",              4),
        ("ireland's law",            4), ("dublin government",          3),
        ("ireland ",                 2), ("irish ",                     1),
    ]),
    ("🇮🇹 Italy", 3, [
        ("garante",                  5), ("italian data",               5),
        ("italian government",       5), ("italian law",                4),
        ("italian regulat",          4), ("italian cyber",              4),
        ("acn italy",                4), ("italy's law",                4),
        ("rome government",          3), ("italy ",                     2),
        ("italian ",                 1),
    ]),
    ("🇪🇸 Spain", 3, [
        ("aepd",                     5), ("spanish data",               5),
        ("spanish government",       5), ("spanish law",                4),
        ("spanish regulat",          4), ("spanish cyber",              4),
        ("spain's law",              4), ("madrid government",          3),
        ("spain ",                   2), ("spanish ",                   1),
    ]),
    ("🇵🇱 Poland", 3, [
        ("polish government",        5), ("polish law",                 4),
        ("polish regulat",           4), ("polish cyber",               4),
        ("poland's law",             4), ("warsaw government",          3),
        ("poland ",                  2), ("polish ",                    1),
    ]),
    ("🇧🇪 Belgium", 3, [
        ("belgian government",       5), ("belgian data",               5),
        ("belgian law",              4), ("belgian regulat",            4),
        ("belgium cyber",            4), ("belgium's law",              4),
        ("brussels government",      3), ("belgium ",                   2),
        ("belgian ",                 1),
    ]),
    ("🇸🇪 Sweden", 3, [
        ("swedish government",       5), ("swedish law",                4),
        ("swedish regulat",          4), ("swedish cyber",              4),
        ("sweden's law",             4), ("stockholm government",       3),
        ("sweden ",                  2), ("swedish ",                   1),
    ]),
    ("🇩🇰 Denmark", 3, [
        ("danish government",        5), ("danish law",                 4),
        ("danish regulat",           4), ("danish cyber",               4),
        ("denmark's law",            4), ("denmark ",                   2),
        ("danish ",                  1),
    ]),
    ("🇫🇮 Finland", 3, [
        ("finnish government",       5), ("finnish law",                4),
        ("finnish regulat",          4), ("finnish cyber",              4),
        ("finland's law",            4), ("finland ",                   2),
        ("finnish ",                 1),
    ]),
    ("🇵🇹 Portugal", 3, [
        ("portuguese government",    5), ("portuguese law",             4),
        ("portuguese regulat",       4), ("portugal cyber",             4),
        ("portugal's law",           4), ("lisbon government",          3),
        ("portugal ",                2), ("portuguese ",                1),
    ]),
    ("🇦🇹 Austria", 3, [
        ("austrian government",      5), ("austrian law",               4),
        ("austrian regulat",         4), ("austria cyber",              4),
        ("austria's law",            4), ("vienna government",          3),
        ("austria ",                 2), ("austrian ",                  1),
    ]),
    ("🇨🇿 Czech Republic", 3, [
        ("czech government",         5), ("czech law",                  4),
        ("czech regulat",            4), ("czech cyber",                4),
        ("czech republic law",       4), ("prague government",          3),
        ("czech republic",           2), ("czech ",                     1),
    ]),
    ("🇷🇴 Romania", 3, [
        ("romanian government",      5), ("romanian law",               4),
        ("romanian regulat",         4), ("romania cyber",              4),
        ("romania's law",            4), ("bucharest government",       3),
        ("romania ",                 2), ("romanian ",                  1),
    ]),
    ("🇭🇺 Hungary", 3, [
        ("hungarian government",     5), ("hungarian law",              4),
        ("hungarian regulat",        4), ("hungary cyber",              4),
        ("hungary's law",            4), ("budapest government",        3),
        ("hungary ",                 2), ("hungarian ",                 1),
    ]),
    ("🇬🇷 Greece", 3, [
        ("greek government",         5), ("greek law",                  4),
        ("greek regulat",            4), ("greece cyber",               4),
        ("greece's law",             4), ("athens government",          3),
        ("greece ",                  2), ("greek ",                     1),
    ]),

    # ── Other major non-EU countries ──
    ("🇺🇸 US", 3, [
        ("congress",                 5), ("senate",                     5),
        ("house of representatives", 5), ("white house",                5),
        ("federal register",         5), ("nist ",                      5),
        ("cisa ",                    5), ("nydfs",                      5),
        ("sec rule",                 5), ("ftc ",                       4),
        ("ferc ",                    4), ("fbi ",                       4),
        ("department of homeland",   5), ("u.s. department",            5),
        ("u.s. government",          5), ("u.s. law",                   5),
        ("u.s. regulat",             5), ("u.s. policy",                4),
        ("federal agency",           4), ("washington d.c.",            4),
        ("cmmc ",                    4), ("fedramp",                    4),
        ("cfpb",                     4), ("tsa directive",              5),
        ("fcc rule",                 4), ("doj ",                       4),
        ("pentagon",                 4), ("u.s. congress",              5),
        ("american law",             4), ("united states law",          4),
        ("united states regulat",    4), ("united states",              3),
        (" u.s. ",                   3), ("american ",                  1),
    ]),
    ("🇨🇳 China", 3, [
        ("cyberspace administration of china", 6), ("cac china",        6),
        ("prc law",                  5), ("china's cybersecurity law",  5),
        ("pipl",                     5), ("mlps ",                      5),
        ("china's data",             5), ("chinese government",         5),
        ("chinese law",              4), ("chinese regulat",            4),
        ("china law",                4), ("china regulat",              4),
        ("china cyber",              4), ("china's law",                4),
        ("national security law china", 5), ("beijing government",      4),
        ("china ",                   2), ("chinese ",                   1),
    ]),
    ("🇷🇺 Russia", 3, [
        ("roskomnadzor",             6), ("russian government",         5),
        ("russian law",              5), ("russian regulat",            5),
        ("russia's cyber",           5), ("russia's data",              5),
        ("fsb ",                     4), ("svr ",                       4),
        ("kremlin",                  4), ("state duma",                 5),
        ("russia's law",             4), ("moscow government",          4),
        ("russia ",                  2), ("russian ",                   1),
    ]),
    ("🇦🇺 Australia", 3, [
        ("acsc ",                    5), ("asd australia",              5),
        ("australian government",    5), ("home affairs australia",     5),
        ("australian cyber",         4), ("australian law",             4),
        ("australian regulat",       4), ("australia's cyber",          4),
        ("australia's law",          4), ("canberra government",        4),
        ("privacy act australia",    5), ("critical infrastructure act", 5),
        ("australia ",               2), ("australian ",                1),
    ]),
    ("🇨🇦 Canada", 3, [
        ("cse canada",               5), ("bill c-26",                  5),
        ("cppa canada",              5), ("pipeda",                     5),
        ("canadian government",      5), ("canadian law",               4),
        ("canadian regulat",         4), ("canada's cyber",             4),
        ("canada's law",             4), ("privacy commissioner canada", 5),
        ("ottawa government",        4), ("canada ",                    2),
        ("canadian ",                1),
    ]),
    ("🇸🇬 Singapore", 3, [
        ("csa singapore",            6), ("pdpa",                       5),
        ("mas singapore",            5), ("singapore government",       5),
        ("singapore cyber",          4), ("singapore law",              4),
        ("singapore regulat",        4), ("singapore's law",            4),
        ("singapore ",               2),
    ]),
    ("🇯🇵 Japan", 3, [
        ("nisc japan",               5), ("meti japan",                 5),
        ("japanese government",      5), ("japanese law",               4),
        ("japanese regulat",         4), ("japan cyber",                4),
        ("japan's law",              4), ("appi japan",                 5),
        ("tokyo government",         4), ("japan ",                     2),
        ("japanese ",                1),
    ]),
    ("🇰🇷 South Korea", 3, [
        ("kisa ",                    5), ("korean government",          5),
        ("korean law",               4), ("korean regulat",             4),
        ("south korea cyber",        4), ("south korea's law",          4),
        ("pipa korea",               5), ("seoul government",           4),
        ("south korea ",             2), ("korean ",                    1),
    ]),
    ("🇮🇳 India", 3, [
        ("cert-in",                  5), ("meity",                      5),
        ("dpdp act",                 5), ("it act india",               5),
        ("indian government",        5), ("indian law",                 4),
        ("indian regulat",           4), ("india's cyber",              4),
        ("india's law",              4), ("new delhi government",       4),
        ("india ",                   2), ("indian ",                    1),
    ]),
    ("🇧🇷 Brazil", 3, [
        ("lgpd",                     5), ("anpd brazil",                5),
        ("brazilian government",     5), ("brazilian law",              4),
        ("brazilian regulat",        4), ("brazil cyber",               4),
        ("brazil's law",             4), ("brasilia government",        4),
        ("brazil ",                  2), ("brazilian ",                 1),
    ]),
    ("🇮🇱 Israel", 3, [
        ("incd israel",              5), ("israeli government",         5),
        ("israeli law",              4), ("israeli regulat",            4),
        ("israel cyber",             4), ("israel's law",               4),
        ("privacy protection authority israel", 5), ("israel ",         2),
        ("israeli ",                 1),
    ]),
    ("🇸🇦 Saudi Arabia", 3, [
        ("nca saudi",                5), ("saudi government",           5),
        ("saudi law",                4), ("saudi regulat",              4),
        ("saudi cyber",              4), ("saudi arabia's law",         4),
        ("pdpl saudi",               5), ("riyadh government",          4),
        ("saudi arabia ",            2), ("saudi ",                     1),
    ]),
    ("🇦🇪 UAE", 3, [
        ("uae government",           5), ("uae law",                    4),
        ("uae regulat",              4), ("uae cyber",                  4),
        ("uae data",                 4), ("dubai government",           4),
        ("abu dhabi law",            4), ("federal decree uae",         5),
        ("uae ",                     2),
    ]),
    ("🇿🇦 South Africa", 3, [
        ("popia",                    5), ("south african government",   5),
        ("south african law",        4), ("south african regulat",      4),
        ("south africa cyber",       4), ("south africa's law",         4),
        ("pretoria government",      4), ("south africa ",              2),
        ("south african ",           1),
    ]),
    ("🇲🇽 Mexico", 3, [
        ("mexican government",       5), ("mexican law",                4),
        ("mexican regulat",          4), ("mexico cyber",               4),
        ("mexico's law",             4), ("lfpdppp",                    5),
        ("inai mexico",              5), ("mexico ",                    2),
        ("mexican ",                 1),
    ]),
    ("🇳🇿 New Zealand", 3, [
        ("nzism",                    5), ("new zealand government",     5),
        ("new zealand law",          4), ("new zealand regulat",        4),
        ("new zealand cyber",        4), ("new zealand's law",          4),
        ("privacy act new zealand",  5), ("wellington government",      4),
        ("new zealand ",             2),
    ]),
    ("🇨🇭 Switzerland", 3, [
        ("revfadp",                  5), ("swiss government",           5),
        ("swiss law",                4), ("swiss regulat",              4),
        ("swiss cyber",              4), ("switzerland law",            4),
        ("bern government",          4), ("switzerland ",               2),
        ("swiss ",                   1),
    ]),
    ("🇳🇴 Norway", 3, [
        ("norwegian government",     5), ("norwegian law",              4),
        ("norwegian regulat",        4), ("norway cyber",               4),
        ("norway's law",             4), ("oslo government",            3),
        ("norway ",                  2), ("norwegian ",                 1),
    ]),
    ("🇹🇷 Turkey", 3, [
        ("turkish government",       5), ("turkish law",                4),
        ("turkish regulat",          4), ("turkey cyber",               4),
        ("kvkk",                     5), ("turkey's law",               4),
        ("ankara government",        4), ("turkey ",                    2),
        ("turkish ",                 1),
    ]),
    ("🇺🇦 Ukraine", 3, [
        ("ukrainian government",     5), ("ukrainian law",              4),
        ("ukrainian regulat",        4), ("ukraine cyber",              4),
        ("ukraine's law",            4), ("kyiv government",            4),
        ("ukraine ",                 2), ("ukrainian ",                 1),
    ]),
    ("🇹🇭 Thailand", 3, [
        ("pdpa thailand",            5), ("thai government",            5),
        ("thai law",                 4), ("thai regulat",               4),
        ("thailand cyber",           4), ("thailand's law",             4),
        ("thailand ",                2), ("thai ",                      1),
    ]),
    ("🇮🇩 Indonesia", 3, [
        ("pdp law indonesia",        5), ("kominfo",                    5),
        ("indonesian government",    5), ("indonesian law",             4),
        ("indonesian regulat",       4), ("indonesia cyber",            4),
        ("jakarta government",       4), ("indonesia ",                 2),
        ("indonesian ",              1),
    ]),
    ("🇲🇾 Malaysia", 3, [
        ("pdpa malaysia",            5), ("nacsa malaysia",             5),
        ("malaysian government",     5), ("malaysian law",              4),
        ("malaysian regulat",        4), ("malaysia cyber",             4),
        ("kuala lumpur government",  4), ("malaysia ",                  2),
        ("malaysian ",               1),
    ]),
    ("🇵🇭 Philippines", 3, [
        ("npc philippines",          5), ("data privacy act philippines", 5),
        ("philippine government",    5), ("philippine law",             4),
        ("philippine regulat",       4), ("philippines cyber",          4),
        ("manila government",        4), ("philippines ",               2),
        ("philippine ",              1),
    ]),
    ("🇻🇳 Vietnam", 3, [
        ("pdpd vietnam",             5), ("vietnamese government",      5),
        ("vietnamese law",           4), ("vietnamese regulat",         4),
        ("vietnam cyber",            4), ("vietnam's law",              4),
        ("hanoi government",         4), ("vietnam ",                   2),
        ("vietnamese ",              1),
    ]),
    ("🇦🇷 Argentina", 3, [
        ("pdp argentina",            5), ("aaip argentina",             5),
        ("argentine government",     5), ("argentine law",              4),
        ("argentine regulat",        4), ("argentina cyber",            4),
        ("buenos aires government",  4), ("argentina ",                 2),
        ("argentine ",               1),
    ]),
    ("🇨🇴 Colombia", 3, [
        ("habeas data colombia",     5), ("sic colombia",               5),
        ("colombian government",     5), ("colombian law",              4),
        ("colombian regulat",        4), ("colombia cyber",             4),
        ("bogota government",        4), ("colombia ",                  2),
        ("colombian ",               1),
    ]),
    ("🇳🇬 Nigeria", 3, [
        ("ndpc nigeria",             5), ("nigerian government",        5),
        ("nigerian law",             4), ("nigerian regulat",           4),
        ("nigeria cyber",            4), ("nigeria's law",              4),
        ("abuja government",         4), ("nigeria ",                   2),
        ("nigerian ",                1),
    ]),
    ("🇰🇪 Kenya", 3, [
        ("odpc kenya",               5), ("kenyan government",          5),
        ("kenyan law",               4), ("kenyan regulat",             4),
        ("kenya cyber",              4), ("kenya's law",                4),
        ("nairobi government",       4), ("kenya ",                     2),
        ("kenyan ",                  1),
    ]),
    ("🇮🇱 Israel", 3, [
        ("incd israel",              5), ("ppa israel",                 5),
        ("israeli government",       5), ("israeli law",                4),
        ("israeli regulat",          4), ("israel cyber",               4),
        ("israel's law",             4), ("israel ",                    2),
        ("israeli ",                 1),
    ]),
    ("🇵🇰 Pakistan", 3, [
        ("peca pakistan",            5), ("pakistani government",       5),
        ("pakistani law",            4), ("pakistani regulat",          4),
        ("pakistan cyber",           4), ("pakistan's law",             4),
        ("islamabad government",     4), ("pakistan ",                  2),
        ("pakistani ",               1),
    ]),

    # ── Global / Multi-jurisdictional (low threshold — many signals needed) ──
    ("🌐 Global", 4, [
        ("g7 ",                      4), ("g20 ",                      4),
        ("nato",                     3), ("five eyes",                  4),
        ("transatlantic",            3), ("cross-border regulat",       5),
        ("multinational regulat",    5), ("international standard",     4),
        ("global cyber",             3), ("global regulat",             4),
        ("multiple countries",       4), ("several nations",            4),
        ("worldwide regulat",        4), ("un cyber",                   4),
        ("international cyber",      3),
    ]),
]


# ─── SECTOR / TYPE RULES ─────────────────────────────────────────────────────
SECTOR_RULES = [
    (["bank", "financial", "finance", "fintech", "dora", "nydfs", "sec ", "payment", "credit",
      "insurance", "swift", "trading", "investment", "hedge fund", "asset manag",
      "capital market", "cfpb", "fsb "], "💰 Finance"),
    (["health", "medical", "hospital", "pharma", "hipaa", "fda ", "patient", "clinical",
      "biotech", "ehr ", "health record", "healthcare"], "🏥 Healthcare"),
    (["energy", "power grid", "electric", "oil", "gas", "pipeline", "nuclear", "utility",
      "water system", "scada", "ics ", "ot security", "operational technology"], "⚡ Energy & Utilities"),
    (["defense", "military", "pentagon", "dod ", "nato", "intelligence", "cia ", "nsa ",
      "warfare", "espionage", "nation-state", "apt ", "advanced persistent", "cmmc"], "🛡️ Defense & Intelligence"),
    (["transport", "aviation", "airline", "rail", "maritime", "port", "vehicle", "autonomous",
      "connected car", "faa ", "tsa ", "shipping"], "✈️ Transport"),
    (["telecom", "wireless", "5g", "broadband", "internet provider", "isp ", "carrier",
      "fcc ", "spectrum"], "📡 Telecom"),
    (["ai ", "artificial intelligence", "machine learning", "llm ", "generative ai",
      "eu ai act", "deepfake", "foundation model", "algorithm regulat"], "🤖 AI & Emerging Tech"),
    (["cloud", "saas", "software", "tech company", "platform", "data center",
      "supply chain software", "cyber resilience act"], "💻 Technology"),
    (["government", "federal agency", "public sector", "state department", "municipal",
      "election", "voting", "e-government"], "🏛️ Government"),
    (["retail", "ecommerce", "consumer", "pci ", "shopping", "payment card"], "🛒 Retail & Consumer"),
    (["education", "university", "school", "student", "ferpa", "campus"], "🎓 Education"),
]

TYPE_RULES = [
    (["bill ", " act ", "legislation", "congress", "senate", "parliament", "directive",
      "regulation passed", "law passed", "enacted", "signed into law", "proposed law",
      "bipartisan", "amendment", "statute", "rulemaking", "proposed rule", "final rule",
      "cyber resilience act", "ai act", "data act"], "⚖️ Legislative"),
    (["regulat", "compliance", "enforcement", "penalty", "fine ",
      "enforcement action", "consent order", "sec charges", "nydfs", "gdpr enforcement",
      "supervisory", "authority order", "sanction", "regulator"], "📋 Regulatory"),
    (["policy", "guidance", "framework", "strategy", "executive order", "memorandum",
      "advisory", "national strategy", "best practice", "standard", "nist ",
      "iso 27001", "oversight", "governance"], "🗂️ Policy"),
    (["research", "report", "study", "analysis", "survey", "think tank", "academic",
      "findings", "white paper", "assessment", "index "], "📚 Research"),
]

TYPE_COLORS = {
    "⚖️ Legislative":    "#7C3AED",
    "📋 Regulatory":     "#2563EB",
    "🗂️ Policy":         "#0891B2",
    "📚 Research":       "#059669",
}


# ─── HELPERS ─────────────────────────────────────────────────────────────────
def _text(entry) -> str:
    return " ".join([
        entry.get("title", ""),
        entry.get("summary", ""),
        entry.get("description", ""),
        " ".join(t.get("term", "") for t in entry.get("tags", [])),
    ]).lower()


def is_cyber_relevant(text: str) -> bool:
    return any(kw in text for kw in CYBER_KEYWORDS)


def is_regulatory_relevant(text: str) -> bool:
    return any(sig in text for sig in REGULATORY_SIGNALS)


def classify_geo(text: str) -> str:
    """
    Two-phase geo classification:
    1. Check US states first — if a state scores ≥ 3, prefer the state label
       over the generic US label (more specific is better).
    2. Score all country rules simultaneously; winner must meet its min_score.
       If nothing qualifies, return 🌐 Global.
    """
    # Phase 1: US state check
    best_state, best_state_score = None, 0
    for state_label, kw_weights in US_STATES:
        score = sum(w for kw, w in kw_weights if kw in text)
        if score > best_state_score:
            best_state_score = score
            best_state = state_label

    # Phase 2: Country scoring
    country_scores = {}
    for label, min_score, kw_weights in GEO_COUNTRIES:
        score = sum(w for kw, w in kw_weights if kw in text)
        if score >= min_score:
            country_scores[label] = score

    best_country = max(country_scores, key=country_scores.get) if country_scores else None
    best_country_score = country_scores.get(best_country, 0) if best_country else 0

    # If a US state scored ≥ 3 AND beats or ties country-level US, prefer the state
    if best_state_score >= 3 and best_country in ("🇺🇸 US", None):
        if best_state_score >= best_country_score or best_country is None:
            return best_state

    if best_country:
        return best_country

    return "🌐 Global"


def classify_sector(text: str) -> str:
    for keywords, label in SECTOR_RULES:
        if any(kw in text for kw in keywords):
            return label
    return "🔒 General Cybersecurity"


def classify_type(text: str, type_hint: str) -> str:
    for keywords, label in TYPE_RULES:
        if any(kw in text for kw in keywords):
            return label
    hint_map = {
        "Legislative": "⚖️ Legislative",
        "Regulatory":  "📋 Regulatory",
        "Policy":      "🗂️ Policy",
        "Academic":    "📚 Research",
    }
    return hint_map.get(type_hint, "🗂️ Policy")


def parse_date(entry) -> datetime:
    for attr in ("published_parsed", "updated_parsed"):
        t = entry.get(attr)
        if t:
            try:
                return datetime(*t[:6], tzinfo=timezone.utc)
            except Exception:
                pass
    return datetime.now(timezone.utc)


def fetch_source(source: dict) -> list:
    try:
        resp = requests.get(
            source["url"],
            headers={"User-Agent": "Mozilla/5.0 (compatible; CyberRegWatch/1.0)"},
            timeout=10,
        )
        feed = feedparser.parse(resp.text)
        articles = []
        for entry in feed.entries[:25]:
            text = _text(entry)
            if not is_cyber_relevant(text):
                continue
            if not is_regulatory_relevant(text):
                continue
            title    = entry.get("title", "No title").strip()
            link     = entry.get("link", "#").strip()
            raw_desc = entry.get("summary", entry.get("description", ""))
            desc     = re.sub(r"<[^>]+>", "", raw_desc).strip()
            desc     = (desc[:260] + "…") if len(desc) > 260 else desc
            articles.append({
                "title":    title,
                "url":      link,
                "summary":  desc,
                "source":   source["name"],
                "date":     parse_date(entry),
                "geo":      classify_geo(text),
                "sector":   classify_sector(text),
                "art_type": classify_type(text, source["type_hint"]),
            })
        return articles
    except Exception:
        return []


def fetch_all(max_workers: int = 14) -> list:
    articles = []
    with ThreadPoolExecutor(max_workers=max_workers) as ex:
        for result in as_completed([ex.submit(fetch_source, s) for s in SOURCES]):
            articles.extend(result.result())

    seen, unique = set(), []
    for a in articles:
        key = re.sub(r"\W+", "", a["title"].lower())[:64]
        if key not in seen:
            seen.add(key)
            unique.append(a)

    unique.sort(key=lambda x: x["date"], reverse=True)
    return unique