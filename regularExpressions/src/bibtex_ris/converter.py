"""fachada del conversor bibtex a ris"""

from .constants import (
    BIBTEX_TO_RIS,
    FIELD_ORDER,
    MONTHS,
    MONTHS_REVERSE,
    RIS_FIELD_ORDER,
    RIS_TO_BIBTEX,
    TYPES_TO_BIBTEX,
    TYPES_TO_RIS,
)
from .parsers.bibtex_parser import parse_bibtex
from .parsers.ris_parser import parse_ris
from .utils import build_date, da_to_month_day
from .writers.bibtex_writer import ris_entry_to_bibtex
from .writers.ris_writer import bibtex_entry_to_ris


class BibtexRisConverter:
    """convierte entre bibtex y ris

    delega cada tarea en un modulo
    - constants guarda los mapeos de tipos y campos
    - parsers leen los archivos de entrada
    - writers generan el texto de salida
    """

    # tipos de entrada bibtex a ris
    TYPES_TO_RIS = TYPES_TO_RIS

    # tipos de entrada ris a bibtex
    TYPES_TO_BIBTEX = TYPES_TO_BIBTEX

    # campos bibtex a etiquetas ris
    BIBTEX_TO_RIS = BIBTEX_TO_RIS

    # campos ris a etiquetas bibtex
    RIS_TO_BIBTEX = RIS_TO_BIBTEX

    # nombres de mes a numero
    MONTHS = MONTHS

    # numero de mes a nombre
    MONTHS_REVERSE = MONTHS_REVERSE

    # orden de campos al escribir ris
    FIELD_ORDER = FIELD_ORDER

    # orden de etiquetas al escribir bibtex
    RIS_FIELD_ORDER = RIS_FIELD_ORDER

    def _build_date(self, year, month=None, day=None):
        """compone una fecha en formato yyyy/mm/dd"""
        return build_date(year, month, day)

    def _da_to_month_day(self, value):
        """convierte una fecha da en mes y dia para bibtex"""
        return da_to_month_day(value)

    def parse_bibtex(self, content):
        """extrae las entradas bibtex del texto"""
        return parse_bibtex(content)

    def parse_ris(self, content):
        """extrae las entradas ris del texto"""
        return parse_ris(content)

    def bibtex_entry_to_ris(self, entry):
        """convierte una entrada bibtex a texto ris"""
        return bibtex_entry_to_ris(entry)

    def ris_entry_to_bibtex(self, entry):
        """convierte una entrada ris a texto bibtex"""
        return ris_entry_to_bibtex(entry)

    def convert_file(self, input_path, output_path, target_format):
        """convierte un archivo completo al formato indicado"""
        # lee el archivo de entrada
        with open(input_path, 'r', encoding='utf-8-sig') as f:
            content = f.read()

        output_lines = []
        target = target_format.lower()

        if target == 'ris':
            # convierte bibtex a ris
            entries = self.parse_bibtex(content)
            for entry in entries:
                output_lines.append(self.bibtex_entry_to_ris(entry))
                output_lines.append('')
        else:
            # convierte ris a bibtex
            entries = self.parse_ris(content)
            for entry in entries:
                output_lines.append(self.ris_entry_to_bibtex(entry))
                output_lines.append('')

        # escribe el archivo de salida
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write('\n'.join(output_lines))

        return len(entries)