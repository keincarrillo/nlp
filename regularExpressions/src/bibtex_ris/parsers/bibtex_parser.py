"""Parser de archivos BibTeX"""

import re

from ..latex import unescape_latex
from ..utils import split_authors

# ------------------------------------------------------------------
# Expresiones regulares
# ------------------------------------------------------------------

# Inicio de una entrada BibTeX: "@tipo{clave,".
# re.IGNORECASE permite escribir "@Article" o "@article".
ENTRY_PATTERN = re.compile(r'@(\w+)\s*\{\s*([^,]+),', re.IGNORECASE)

# Inicio de un campo dentro de una entrada: "nombre =".
FIELD_START_PATTERN = re.compile(r'(\w+)\s*=')


def parse_bibtex(content):
    """Extrae entradas BibTeX"""
    entries = []

    # 1) Localizar cada entrada con una regex sencilla.
    for match in ENTRY_PATTERN.finditer(content):
        entry_type = match.group(1).lower()
        entry_id = match.group(2).strip()

        # 2) Buscar la llave que cierra la entrada contando llaves.
        end = _find_entry_end(content, match.end())
        fields_text = content[match.end():end]

        # 3) Leer los pares nombre = valor de dentro de la entrada.
        entries.append({
            'type': entry_type,
            'id': entry_id,
            'fields': _parse_fields(fields_text),
        })

    return entries


def _find_entry_end(text, start):
    """Devuelve la posicion de la llave '}' que cierra una entrada"""
    depth = 0
    for i in range(start, len(text)):
        char = text[i]
        if char == '{':
            depth += 1
        elif char == '}':
            depth -= 1
            if depth < 0:
                return i
    return len(text)


def _parse_fields(fields_text):
    """Convierte el bloque 'nombre = valor, ...' en un diccionario"""
    fields = {}
    position = 0

    # Paso 1: buscar el siguiente campo, que siempre empieza con "nombre =".
    while True:
        match = FIELD_START_PATTERN.search(fields_text, position)
        if match is None:
            break

        name = match.group(1).lower()

        # Paso 2: leer el valor que sigue al signo '='.
        # La posicion avanza hasta justo despues del valor leido.
        value, position = _read_field_value(fields_text, match.end())
        if value is None:
            # Valor no valido: pasar al siguiente posible campo.
            position = match.end()
            continue

        # Paso 3: limpiar el valor y guardarlo.
        value = unescape_latex(value.strip())
        if name in ('author', 'editor'):
            fields[name] = split_authors(value)
        else:
            fields[name] = value

    return fields


def _read_field_value(text, start):
    """Lee un valor BibTeX a partir de la posicion 'start'.

    BibTeX permite dos estilos de valor:
      - entre comillas dobles:  "texto"
      - entre llaves:           {texto}

    Un valor entre llaves puede contener llaves anidadas, por
    ejemplo comandos LaTeX como {\\v{R}} o {\\&}. Por eso se
    cuentan las llaves hasta encontrar la que cierra.

    Devuelve la tupla (valor, posicion_final) o (None, start)
    cuando no hay un valor valido.
    """
    if start >= len(text):
        return None, start

    # Ignorar los espacios que hay entre el '=' y el valor.
    while start < len(text) and text[start] in ' \t\n':
        start += 1
    if start >= len(text):
        return None, start

    # Valor entre comillas: termina en la siguiente comilla doble.
    if text[start] == '"':
        end = text.find('"', start + 1)
        if end == -1:
            return None, start
        return text[start + 1:end], end + 1

    # Valor entre llaves: se cuentan las llaves anidadas.
    if text[start] == '{':
        depth = 0
        for i in range(start, len(text)):
            if text[i] == '{':
                depth += 1
            elif text[i] == '}':
                depth -= 1
                if depth == 0:
                    return text[start + 1:i], i + 1
        # No se encontro la llave de cierre.
        return None, start

    # No empieza con comilla ni con llave: no hay valor que leer.
    return None, start