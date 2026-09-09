"""genera texto ris a partir de una entrada bibtex parseada"""

from ..constants import BIBTEX_TO_RIS, FIELD_ORDER, TYPES_TO_RIS
from ..utils import build_date, format_line, split_keywords, split_pages


def bibtex_entry_to_ris(entry):
    """convierte una entrada bibtex a texto ris"""
    ris_type = TYPES_TO_RIS.get(entry.get('type', ''), 'JOUR')
    lines = [format_line('TY', ris_type)]

    fields = entry.get('fields', {})

    # autores y editores se escriben como listas
    for name in ('author', 'editor'):
        values = fields.get(name, [])
        if isinstance(values, str):
            values = [values]
        tag = BIBTEX_TO_RIS[name]
        for item in values:
            lines.append(format_line(tag, item))

    # anio y fecha en formato yyyy/mm/dd
    year = fields.get('year')
    if year:
        lines.append(format_line('PY', year))
        date = build_date(year, fields.get('month'), fields.get('day'))
        lines.append(format_line('DA', date))

    # escribe los demas campos en orden
    for name in FIELD_ORDER:
        if name not in fields:
            continue
        value = fields[name]

        # paginas se dividen en sp y ep
        if name == 'pages':
            pages = split_pages(value)
            lines.append(format_line('SP', pages[0]))
            if len(pages) > 1:
                lines.append(format_line('EP', pages[1]))
            continue

        # keywords se escriben una por linea
        if name == 'keywords':
            for kw in split_keywords(value):
                lines.append(format_line('KW', kw))
            continue

        lines.append(format_line(BIBTEX_TO_RIS[name], value))

    lines.append(format_line('ID', entry.get('id', '')))
    lines.append('ER  -')
    return '\n'.join(lines)