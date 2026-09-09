"""genera texto bibtex a partir de una entrada ris parseada"""

from ..constants import RIS_FIELD_ORDER, RIS_TO_BIBTEX, TYPES_TO_BIBTEX
from ..utils import da_to_month_day


def ris_entry_to_bibtex(entry):
    """convierte una entrada ris a texto bibtex"""
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

        # py separa la fecha en year month y day
        if tag == 'PY':
            add_field('year', value)
            month, day = da_to_month_day(entry.get('DA'))
            handled.add('DA')
            if month:
                add_field('month', month)
                if day:
                    add_field('day', day)
            continue

        # da y ep se procesan junto a py y sp
        if tag in ('DA', 'EP'):
            continue

        # sp y ep se juntan en un solo campo pages
        if tag == 'SP':
            pages = str(value)
            if 'EP' in entry:
                pages += '--' + str(entry['EP'])
                handled.add('EP')
            add_field('pages', pages)
            continue

        # jo t2 y bt mapean a journal o booktitle
        if tag in ('JO', 'T2', 'BT'):
            name = {'JO': 'journal', 'T2': 'booktitle', 'BT': 'booktitle'}[tag]
            add_field(name, value)
            continue

        # kw une los valores en una sola lista separada por comas
        if tag == 'KW':
            join = ', '.join(value) if isinstance(value, list) else str(value)
            add_field('keywords', join)
            continue

        # sn usa issn para revistas e isbn para el resto
        if tag == 'SN':
            name = 'issn' if ris_type == 'JOUR' else 'isbn'
            add_field(name, value)
            continue

        # au y ed unen los autores con la palabra and
        if tag in ('AU', 'ED'):
            name = 'author' if tag == 'AU' else 'editor'
            join = ' and '.join(value) if isinstance(value, list) else str(value)
            add_field(name, join)
            continue

        bibtex_field = RIS_TO_BIBTEX.get(tag)
        if bibtex_field:
            add_field(bibtex_field, value if not isinstance(value, list) else value[0])

    # escribe etiquetas que no estan en el orden canonico
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

    # quita la coma del ultimo campo y cierra la entrada
    if lines[-1].endswith(','):
        lines[-1] = lines[-1].rstrip(',')
    lines.append('}')
    return '\n'.join(lines)