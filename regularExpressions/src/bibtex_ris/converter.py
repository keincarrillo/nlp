"""Nucleo del conversor BibTeX a RIS"""

import re

from .latex import unescape_latex


class BibtexRisConverter:
    """Convierte entre los formatos BibTeX y RIS"""

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

    # ------------------------------------------------------------------
    # Expresiones regulares
    # ------------------------------------------------------------------

    # Inicio de una entrada BibTeX: "@tipo{clave,".
    # re.IGNORECASE permite escribir "@Article" o "@article".
    ENTRY_PATTERN = re.compile(r'@(\w+)\s*\{\s*([^,]+),', re.IGNORECASE)

    # Inicio de un campo dentro de una entrada: "nombre =".
    FIELD_START_PATTERN = re.compile(r'(\w+)\s*=')

    # Linea RIS con etiqueta: "ETIQUETA  - valor".
    RIS_TAG_PATTERN = re.compile(r'(\w+)\s*-\s*(.*)')

    # Fin de registro: la etiqueta ER separa una entrada de la siguiente.
    RIS_ENTRY_END_PATTERN = re.compile(r'ER\s*-')

    # ------------------------------------------------------------------
    # Utilidades de formato
    # ------------------------------------------------------------------

    @staticmethod
    def _format_line(tag, value):
        return '{}  - {}'.format(tag, value)

    @staticmethod
    def _split_authors(value):
        return [name.strip() for name in re.split(r'\s+and\s+', value, flags=re.IGNORECASE)]

    @staticmethod
    def _split_pages(value):
        parts = [p.strip() for p in re.split(r'--|–|-', value.strip())]
        return [p for p in parts if p] or [value.strip()]

    @staticmethod
    def _split_keywords(value):
        return [k.strip() for k in value.split(',') if k.strip()]

    def _build_date(self, year, month=None, day=None):
        """Compone una fecha en formato YYYY/MM/DD"""
        parts = [str(year), '', '']
        if month:
            key = str(month).strip().lower()
            num = self.MONTHS.get(key[:3])
            if num is None and key.isdigit():
                num = '{:02d}'.format(int(key))
                if not 1 <= int(key) <= 12:
                    num = ''
            parts[1] = num or ''
        if day:
            parts[2] = str(day).strip()
        return '/'.join(parts)

    def _da_to_month_day(self, value):
        if not value:
            return None, None
        parts = str(value).split('/')
        month = None
        day = None
        if len(parts) >= 2 and parts[1]:
            month = self.MONTHS_REVERSE.get(parts[1])
        if len(parts) >= 3 and parts[2]:
            day = parts[2]
        return month, day

    # ------------------------------------------------------------------
    # Parser BibTeX
    # ------------------------------------------------------------------

    def parse_bibtex(self, content):
        """Extrae entradas BibTeX"""
        entries = []

        # 1) Localizar cada entrada con una regex sencilla.
        for match in self.ENTRY_PATTERN.finditer(content):
            entry_type = match.group(1).lower()
            entry_id = match.group(2).strip()

            # 2) Buscar la llave que cierra la entrada contando llaves.
            end = self._find_entry_end(content, match.end())
            fields_text = content[match.end():end]

            # 3) Leer los pares nombre = valor de dentro de la entrada.
            entries.append({
                'type': entry_type,
                'id': entry_id,
                'fields': self._parse_fields(fields_text),
            })

        return entries

    @staticmethod
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

    def _parse_fields(self, fields_text):
        """Convierte el bloque 'nombre = valor, ...' en un diccionario"""
        fields = {}
        position = 0

        # Paso 1: buscar el siguiente campo, que siempre empieza con "nombre =".
        while True:
            match = self.FIELD_START_PATTERN.search(fields_text, position)
            if match is None:
                break

            name = match.group(1).lower()

            # Paso 2: leer el valor que sigue al signo '='.
            # La posicion avanza hasta justo despues del valor leido.
            value, position = self._read_field_value(fields_text, match.end())
            if value is None:
                # Valor no valido: pasar al siguiente posible campo.
                position = match.end()
                continue

            # Paso 3: limpiar el valor y guardarlo.
            value = unescape_latex(value.strip())
            if name in ('author', 'editor'):
                fields[name] = self._split_authors(value)
            else:
                fields[name] = value

        return fields

    @staticmethod
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

    # ------------------------------------------------------------------
    # Parser RIS
    # ------------------------------------------------------------------

    def parse_ris(self, content):
        """Extrae entradas RIS"""
        entries = []

        # Cada entrada es un bloque de lineas "ETIQUETA  - valor"
        # que termina con la etiqueta ER (end of record).
        for block in self.RIS_ENTRY_END_PATTERN.split(content):
            entry = self._parse_ris_block(block)
            if entry:
                entries.append(entry)

        return entries

    def _parse_ris_block(self, block):
        """Convierte el texto de una entrada RIS en un diccionario"""
        entry = {}
        current_tag = None
        current_lines = []

        def save_value():
            """Guarda el valor acumulado de la etiqueta en curso"""
            if current_tag is None:
                return
            value = '\n'.join(current_lines).strip()
            # Etiquetas repetidas (AU, KW, ...) se agrupan en una lista.
            if current_tag in entry:
                if isinstance(entry[current_tag], list):
                    entry[current_tag].append(value)
                else:
                    entry[current_tag] = [entry[current_tag], value]
            else:
                entry[current_tag] = value

        for line in block.splitlines():
            match = self.RIS_TAG_PATTERN.match(line)

            # Linea sin etiqueta: es texto que continua el valor anterior.
            if match is None:
                current_lines.append(line)
                continue

            # Nueva etiqueta: guardar el valor anterior y empezar otro.
            save_value()
            current_tag = match.group(1).strip()
            current_lines = [match.group(2).strip()]

        # Guardar la ultima etiqueta del bloque.
        save_value()

        return entry

    # ------------------------------------------------------------------
    # Conversion BibTeX -> RIS
    # ------------------------------------------------------------------

    def bibtex_entry_to_ris(self, entry):
        """Convierte una entrada BibTeX a RIS"""
        ris_type = self.TYPES_TO_RIS.get(entry.get('type', ''), 'JOUR')
        lines = [self._format_line('TY', ris_type)]

        fields = entry.get('fields', {})

        # Autores y editores como listas
        for name in ('author', 'editor'):
            values = fields.get(name, [])
            if isinstance(values, str):
                values = [values]
            tag = self.BIBTEX_TO_RIS[name]
            for item in values:
                lines.append(self._format_line(tag, item))

        # Anio y fecha en formato YYYY/MM/DD
        year = fields.get('year')
        if year:
            lines.append(self._format_line('PY', year))
            date = self._build_date(year, fields.get('month'), fields.get('day'))
            lines.append(self._format_line('DA', date))

        # Resto de campos en orden
        for name in self.FIELD_ORDER:
            if name not in fields:
                continue
            value = fields[name]

            if name == 'pages':
                pages = self._split_pages(value)
                lines.append(self._format_line('SP', pages[0]))
                if len(pages) > 1:
                    lines.append(self._format_line('EP', pages[1]))
                continue

            if name == 'keywords':
                for kw in self._split_keywords(value):
                    lines.append(self._format_line('KW', kw))
                continue

            lines.append(self._format_line(self.BIBTEX_TO_RIS[name], value))

        lines.append(self._format_line('ID', entry.get('id', '')))
        lines.append('ER  -')
        return '\n'.join(lines)

    # ------------------------------------------------------------------
    # Conversion RIS -> BibTeX
    # ------------------------------------------------------------------

    def ris_entry_to_bibtex(self, entry):
        """Convierte una entrada RIS a BibTeX"""
        ris_type = entry.get('TY', 'JOUR')
        if isinstance(ris_type, list):
            ris_type = ris_type[0]
        bibtex_type = self.TYPES_TO_BIBTEX.get(ris_type, 'article')

        entry_id = entry.get('ID', 'unknown')
        if isinstance(entry_id, list):
            entry_id = entry_id[0]

        lines = ['@{}{{{},'.format(bibtex_type, entry_id)]
        handled = set()

        def add_field(name, value):
            lines.append('  {} = {{{}}},'.format(name, value))

        for tag in self.RIS_FIELD_ORDER:
            if tag not in entry:
                continue
            handled.add(tag)
            value = entry[tag]

            if tag == 'PY':
                add_field('year', value)
                month, day = self._da_to_month_day(entry.get('DA'))
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

            bibtex_field = self.RIS_TO_BIBTEX.get(tag)
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
            bibtex_field = self.RIS_TO_BIBTEX.get(tag)
            if not bibtex_field:
                continue
            if isinstance(value, list):
                value = value[0]
            add_field(bibtex_field, value)

        if lines[-1].endswith(','):
            lines[-1] = lines[-1].rstrip(',')
        lines.append('}')
        return '\n'.join(lines)

    # ------------------------------------------------------------------
    # Conversion de archivos
    # ------------------------------------------------------------------

    def convert_file(self, input_path, output_path, target_format):
        """Convierte un archivo completo al formato indicado"""
        with open(input_path, 'r', encoding='utf-8-sig') as f:
            content = f.read()

        output_lines = []
        target = target_format.lower()

        if target == 'ris':
            entries = self.parse_bibtex(content)
            for entry in entries:
                output_lines.append(self.bibtex_entry_to_ris(entry))
                output_lines.append('')
        else:
            entries = self.parse_ris(content)
            for entry in entries:
                output_lines.append(self.ris_entry_to_bibtex(entry))
                output_lines.append('')

        with open(output_path, 'w', encoding='utf-8') as f:
            f.write('\n'.join(output_lines))

        return len(entries)
