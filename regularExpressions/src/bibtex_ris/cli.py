"""interfaz de linea de comandos del conversor"""

import argparse
import sys
from pathlib import Path

from .converter import BibtexRisConverter


def build_parser():
    return argparse.ArgumentParser(
        description='Conversor BibTeX a RIS y viceversa',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Ejemplos de uso:
  bibtex-ris archivo.bib -f ris -o salida.ris
  bibtex-ris archivo.ris -f bibtex -o salida.bib
        """,
    )


def main(argv=None):
    parser = build_parser()

    parser.add_argument(
        'input',
        help='Archivo de entrada .bib o .ris',
    )

    parser.add_argument(
        '-f', '--format',
        choices=['ris', 'bibtex'],
        required=True,
        help='Formato de salida',
    )

    parser.add_argument(
        '-o', '--output',
        help='Archivo de salida',
    )

    parser.add_argument(
        '-v', '--verbose',
        action='store_true',
        help='Mostrar informacion detallada',
    )

    args = parser.parse_args(argv)

    input_path = Path(args.input)
    if not input_path.exists():
        print('Error: el archivo {} no existe'.format(args.input), file=sys.stderr)
        return 1

    # nombre de salida junto al archivo si no se especifica
    # usa el prefijo out. para que make clean lo borre
    if not args.output:
        suffix = 'ris' if args.format == 'ris' else 'bib'
        default_name = 'out.' + input_path.stem + '.' + suffix
        args.output = str(input_path.parent / default_name)

    if args.verbose:
        print('Leyendo: {}'.format(args.input))
        print('Convirtiendo a: {}'.format(args.format.upper()))
        print('Guardando en: {}'.format(args.output))
        print()

    converter = BibtexRisConverter()

    try:
        num_entries = converter.convert_file(args.input, args.output, args.format)
    except (IOError, OSError) as exc:
        print('Error durante la conversion: {}'.format(exc), file=sys.stderr)
        return 1

    print('Conversion completada exitosamente')
    print('  Entradas procesadas: {}'.format(num_entries))
    print('  Archivo de salida: {}'.format(args.output))

    if args.verbose:
        output_size = Path(args.output).stat().st_size
        print('  Tamano del archivo: {:.2f} KB'.format(output_size / 1024))

    return 0


if __name__ == '__main__':
    sys.exit(main())