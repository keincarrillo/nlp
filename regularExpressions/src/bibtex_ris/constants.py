"""constantes del conversor con los mapeos de tipos y campos"""

# tipos de entrada bibtex a ris
TYPES_TO_RIS = {
    'article': 'JOUR',
    'inproceedings': 'CONF',
    'book': 'BOOK',
    'chapter': 'CHAP',
    'thesis': 'THES',
}

# tipos de entrada ris a bibtex
TYPES_TO_BIBTEX = {ris: bib for bib, ris in TYPES_TO_RIS.items()}

# campos bibtex a etiquetas ris
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

# campos ris a etiquetas bibtex
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

# nombres de mes a numero
MONTHS = {
    'jan': '01', 'feb': '02', 'mar': '03', 'apr': '04',
    'may': '05', 'jun': '06', 'jul': '07', 'aug': '08',
    'sep': '09', 'oct': '10', 'nov': '11', 'dec': '12',
}

# numero de mes a nombre
MONTHS_REVERSE = {num: name.title() for name, num in MONTHS.items()}

# orden de campos al escribir ris
FIELD_ORDER = [
    'title', 'journal', 'booktitle', 'pages', 'volume', 'number',
    'publisher', 'address', 'edition', 'abstract', 'keywords',
    'issn', 'isbn', 'url', 'doi',
]

# orden de etiquetas al escribir bibtex
RIS_FIELD_ORDER = [
    'AU', 'ED', 'PY', 'DA', 'TI', 'JO', 'T2', 'BT', 'SP',
    'VL', 'IS', 'PB', 'CY', 'ET', 'AB', 'KW', 'SN', 'UR', 'DO',
]