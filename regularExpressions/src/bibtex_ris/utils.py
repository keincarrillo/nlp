"""Utilidades de formato compartidas por los writers y el converter"""

import re

from .constants import MONTHS, MONTHS_REVERSE


def format_line(tag, value):
    """Compone una linea RIS: 'ETIQUETA  - valor'"""
    return '{}  - {}'.format(tag, value)


def split_authors(value):
    """Divide un campo de autores BibTeX separado por 'and'"""
    return [name.strip() for name in re.split(r'\s+and\s+', value, flags=re.IGNORECASE)]


def split_pages(value):
    """Divide un rango de paginas 'inicio--fin' en [inicio, fin]"""
    parts = [p.strip() for p in re.split(r'--|–|-', value.strip())]
    return [p for p in parts if p] or [value.strip()]


def split_keywords(value):
    """Divide una lista de keywords separada por comas"""
    return [k.strip() for k in value.split(',') if k.strip()]


def build_date(year, month=None, day=None):
    """Compone una fecha en formato YYYY/MM/DD"""
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
    """Convierte una fecha DA 'YYYY/MM/DD' en (mes, dia) para BibTeX"""
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