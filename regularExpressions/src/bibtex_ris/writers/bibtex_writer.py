"""Genera texto BibTeX a partir de una entrada RIS parseada"""

from ..constants import RIS_FIELD_ORDER, RIS_TO_BIBTEX, TYPES_TO_BIBTEX
from ..utils import da_to_month_day


def ris_entry_to_bibtex(entry):
    """Convierte una entrada RIS a BibTeX"""
    ris_type = entry.get('TY', 'JOUR')
    if isinstance(ris_type, list):
        ris_type = ris_type[0]
    bibtex_type = TYPES_TO_BIBTEX.get(ris_type, 'article')

    entry_id = entry.get('ID', 'unknown')
    if isinstance(entry_id, list):
        entry_id = entry_id[0]

    lines = ['@{}{{{},'.format(bibtex_type, entry_id)]
    handled = set()

    def add_field(name, value):
        lines.append('  {} = {{{}}},'.format(name, value))

    for tag in RIS_FIELD_ORDER:
        if tag not in entry:
            continue
        handled.add(tag)
        value = entry[tag]

        if tag == 'PY':
            add_field('year', value)
            month, day = da_to_month_day(entry.get('DA'))
            handled.add('DA')
            if month:
                add_field('month', month)
                if day:
                    add_field('day', day)
            continue

        if tag in ('DA', 'EP'):
            # Se procesan junto a PY y SP
            continue

        if tag == 'SP':
            pages = str(value)
            if 'EP' in entry:
                pages += '--' + str(entry['EP'])
                handled.add('EP')
            add_field('pages', pages)
            continue

        if tag in ('JO', 'T2', 'BT'):
            name = {'JO': 'journal', 'T2': 'booktitle', 'BT': 'booktitle'}[tag]
            add_field(name, value)
            continue

        if tag == 'KW':
            join = ', '.join(value) if isinstance(value, list) else str(value)
            add_field('keywords', join)
            continue

        if tag == 'SN':
            # SN no distingue ISSN de ISBN: ISSN para revistas, ISBN para el resto
            name = 'issn' if ris_type == 'JOUR' else 'isbn'
            add_field(name, value)
            continue

        if tag in ('AU', 'ED'):
            name = 'author' if tag == 'AU' else 'editor'
            join = ' and '.join(value) if isinstance(value, list) else str(value)
            add_field(name, join)
            continue

        bibtex_field = RIS_TO_BIBTEX.get(tag)
        if bibtex_field:
            add_field(bibtex_field, value if not isinstance(value, list) else value[0])

    # Etiquetas que no estan en el orden canonico
    processed_tags = handled | {
        'TY', 'ID', 'ER', 'PY', 'DA', 'SP', 'EP', 'AU', 'ED',
        'KW', 'SN', 'JO', 'T2', 'BT',
    }
    for tag, value in entry.items():
        if tag in processed_tags:
            continue
        bibtex_field = RIS_TO_BIBTEX.get(tag)
        if not bibtex_field:
            continue
        if isinstance(value, list):
            value = value[0]
        add_field(bibtex_field, value)

    if lines[-1].endswith(','):
        lines[-1] = lines[-1].rstrip(',')
    lines.append('}')
    return '\n'.join(lines)