"""parser de archivos ris"""

import re

# linea ris con etiqueta como "etiqueta  - valor"
RIS_TAG_PATTERN = re.compile(r'(\w+)\s*-\s*(.*)')

# la etiqueta er separa una entrada de la siguiente
RIS_ENTRY_END_PATTERN = re.compile(r'ER\s*-')


def parse_ris(content):
    """extrae las entradas ris del texto"""
    entries = []

    # cada entrada es un bloque de lineas "etiqueta  - valor"
    # que termina con la etiqueta er (end of record)
    for block in RIS_ENTRY_END_PATTERN.split(content):
        entry = _parse_ris_block(block)
        if entry:
            entries.append(entry)

    return entries


def _parse_ris_block(block):
    """convierte el texto de una entrada ris en un diccionario"""
    entry = {}
    current_tag = None
    current_lines = []

    def save_value():
        """guarda el valor acumulado de la etiqueta en curso"""
        if current_tag is None:
            return
        value = '\n'.join(current_lines).strip()
        # etiquetas repetidas como au o kw se agrupan en una lista
        if current_tag in entry:
            if isinstance(entry[current_tag], list):
                entry[current_tag].append(value)
            else:
                entry[current_tag] = [entry[current_tag], value]
        else:
            entry[current_tag] = value

    for line in block.splitlines():
        match = RIS_TAG_PATTERN.match(line)

        # linea sin etiqueta es texto que continua el valor anterior
        if match is None:
            current_lines.append(line)
            continue

        # nueva etiqueta guarda el valor anterior y empieza otro
        save_value()
        current_tag = match.group(1).strip()
        current_lines = [match.group(2).strip()]

    # guarda la ultima etiqueta del bloque
    save_value()

    return entry