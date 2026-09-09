"""utilidades de formato compartidas por los writers y el converter"""

import re

from .constants import MONTHS, MONTHS_REVERSE


def format_line(tag, value):
    """compone una linea ris con el formato 'etiqueta  - valor'"""
    return '{}  - {}'.format(tag, value)


def split_authors(value):
    """divide un campo de autores bibtex separado por la palabra and"""
    return [name.strip() for name in re.split(r'\s+and\s+', value, flags=re.IGNORECASE)]


def split_pages(value):
    """divide un rango de paginas como 'inicio--fin' en [inicio, fin]"""
    parts = [p.strip() for p in re.split(r'--|–|-', value.strip())]
    return [p for p in parts if p] or [value.strip()]


def split_keywords(value):
    """divide una lista de keywords separada por comas"""
    return [k.strip() for k in value.split(',') if k.strip()]


def build_date(year, month=None, day=None):
    """compone una fecha en formato yyyy/mm/dd"""
    parts = [str(year), '', '']
    if month:
        key = str(month).strip().lower()
        num = MONTHS.get(key[:3])
        if num is None and key.isdigit():
            num = '{:02d}'.format(int(key))
            if not 1 <= int(key) <= 12:
                num = ''
        parts[1] = num or ''
    if day:
        parts[2] = str(day).strip()
    return '/'.join(parts)


def da_to_month_day(value):
    """convierte una fecha da del formato yyyy/mm/dd en mes y dia"""
    if not value:
        return None, None
    parts = str(value).split('/')
    month = None
    day = None
    if len(parts) >= 2 and parts[1]:
        month = MONTHS_REVERSE.get(parts[1])
    if len(parts) >= 3 and parts[2]:
        day = parts[2]
    return month, day