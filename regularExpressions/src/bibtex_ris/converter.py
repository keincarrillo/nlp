"""Fachada del conversor: expone la API publica BibtexRisConverter"""

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
    """Convierte entre los formatos BibTeX y RIS

    Es una fachada: cada tarea esta delegada en un modulo especifico.
      - constants: mapeos de tipos y campos.
      - parsers:   leen BibTeX y RIS.
      - writers:   generan la salida en cada formato.
    """

    # Tipos de entrada BibTeX a RIS
    TYPES_TO_RIS = TYPES_TO_RIS

    # Tipos de entrada RIS a BibTeX
    TYPES_TO_BIBTEX = TYPES_TO_BIBTEX

    # Campos BibTeX a etiquetas RIS
    BIBTEX_TO_RIS = BIBTEX_TO_RIS

    # Campos RIS a etiquetas BibTeX
    RIS_TO_BIBTEX = RIS_TO_BIBTEX

    # Nombres de mes a numero
    MONTHS = MONTHS

    # Numero de mes a nombre
    MONTHS_REVERSE = MONTHS_REVERSE

    # Orden de campos al escribir RIS
    FIELD_ORDER = FIELD_ORDER

    # Orden de etiquetas al escribir BibTeX
    RIS_FIELD_ORDER = RIS_FIELD_ORDER

    # ------------------------------------------------------------------
    # Utilidades (delegadas a utils para compatibilidad de API)
    # ------------------------------------------------------------------

    def _build_date(self, year, month=None, day=None):
        """Compone una fecha en formato YYYY/MM/DD"""
        return build_date(year, month, day)

    def _da_to_month_day(self, value):
        """Convierte una fecha DA 'YYYY/MM/DD' en (mes, dia) para BibTeX"""
        return da_to_month_day(value)

    # ------------------------------------------------------------------
    # Parser BibTeX
    # ------------------------------------------------------------------

    def parse_bibtex(self, content):
        """Extrae entradas BibTeX"""
        return parse_bibtex(content)

    # ------------------------------------------------------------------
    # Parser RIS
    # ------------------------------------------------------------------

    def parse_ris(self, content):
        """Extrae entradas RIS"""
        return parse_ris(content)

    # ------------------------------------------------------------------
    # Conversion BibTeX -> RIS
    # ------------------------------------------------------------------

    def bibtex_entry_to_ris(self, entry):
        """Convierte una entrada BibTeX a RIS"""
        return bibtex_entry_to_ris(entry)

    # ------------------------------------------------------------------
    # Conversion RIS -> BibTeX
    # ------------------------------------------------------------------

    def ris_entry_to_bibtex(self, entry):
        """Convierte una entrada RIS a BibTeX"""
        return ris_entry_to_bibtex(entry)

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