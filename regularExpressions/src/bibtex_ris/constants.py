"""Constantes del conversor con los mapeos de tipos y campos"""

# Tipos de entrada BibTeX a RIS
TYPES_TO_RIS = {
    'article': 'JOUR',
    'inproceedings': 'CONF',
    'book': 'BOOK',
    'chapter': 'CHAP',
    'thesis': 'THES',
}

# Tipos de entrada RIS a BibTeX
TYPES_TO_BIBTEX = {ris: bib for bib, ris in TYPES_TO_RIS.items()}

# Campos BibTeX a etiquetas RIS
BIBTEX_TO_RIS = {
    'author': 'AU',
    'editor': 'ED',
    'title': 'TI',
    'journal': 'JO',
    'booktitle': 'BT',
    'year': 'PY',
    'volume': 'VL',
    'number': 'IS',
    'publisher': 'PB',
    'address': 'CY',
    'edition': 'ET',
    'abstract': 'AB',
    'keywords': 'KW',
    'issn': 'SN',
    'isbn': 'SN',
    'doi': 'DO',
    'url': 'UR',
}

# Campos RIS a etiquetas BibTeX
RIS_TO_BIBTEX = {
    'AU': 'author',
    'ED': 'editor',
    'TI': 'title',
    'JO': 'journal',
    'T2': 'booktitle',
    'BT': 'booktitle',
    'PY': 'year',
    'VL': 'volume',
    'IS': 'number',
    'PB': 'publisher',
    'CY': 'address',
    'ET': 'edition',
    'AB': 'abstract',
    'KW': 'keywords',
    'DO': 'doi',
    'UR': 'url',
}

# Nombres de mes a numero
MONTHS = {
    'jan': '01', 'feb': '02', 'mar': '03', 'apr': '04',
    'may': '05', 'jun': '06', 'jul': '07', 'aug': '08',
    'sep': '09', 'oct': '10', 'nov': '11', 'dec': '12',
}

# Numero de mes a nombre
MONTHS_REVERSE = {num: name.title() for name, num in MONTHS.items()}

# Orden de campos al escribir RIS
FIELD_ORDER = [
    'title', 'journal', 'booktitle', 'pages', 'volume', 'number',
    'publisher', 'address', 'edition', 'abstract', 'keywords',
    'issn', 'isbn', 'url', 'doi',
]

# Orden de etiquetas al escribir BibTeX
RIS_FIELD_ORDER = [
    'AU', 'ED', 'PY', 'DA', 'TI', 'JO', 'T2', 'BT', 'SP',
    'VL', 'IS', 'PB', 'CY', 'ET', 'AB', 'KW', 'SN', 'UR', 'DO',
]