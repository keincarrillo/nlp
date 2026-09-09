"""Parser de archivos RIS"""

import re

# Linea RIS con etiqueta como "ETIQUETA  - valor"
RIS_TAG_PATTERN = re.compile(r'(\w+)\s*-\s*(.*)')

# La etiqueta ER separa una entrada de la siguiente
RIS_ENTRY_END_PATTERN = re.compile(r'ER\s*-')


def parse_ris(content):
    """Extrae las entradas RIS del texto"""
    entries = []

    # Cada entrada es un bloque de lineas "ETIQUETA  - valor"
    # que termina con la etiqueta ER (end of record)
    for block in RIS_ENTRY_END_PATTERN.split(content):
        entry = _parse_ris_block(block)
        if entry:
            entries.append(entry)

    return entries


def _parse_ris_block(block):
    """Convierte el texto de una entrada RIS en un diccionario"""
    entry = {}
    current_tag = None
    current_lines = []

    def save_value():
        """Guarda el valor acumulado de la etiqueta en curso"""
        if current_tag is None:
            return
        value = '\n'.join(current_lines).strip()
        # Etiquetas repetidas como AU o KW se agrupan en una lista
        if current_tag in entry:
            if isinstance(entry[current_tag], list):
                entry[current_tag].append(value)
            else:
                entry[current_tag] = [entry[current_tag], value]
        else:
            entry[current_tag] = value

    for line in block.splitlines():
        match = RIS_TAG_PATTERN.match(line)

        # Linea sin etiqueta es texto que continua el valor anterior
        if match is None:
            current_lines.append(line)
            continue

        # Nueva etiqueta guarda el valor anterior y empieza otro
        save_value()
        current_tag = match.group(1).strip()
        current_lines = [match.group(2).strip()]

    # Guarda la ultima etiqueta del bloque
    save_value()

    return entry