# Conversor BibTeX a RIS

Práctica de expresiones regulares: convierte referencias bibliográficas entre **BibTeX** (`.bib`) y **RIS** (`.ris`) usando `re` de Python.

## Estructura

```
regularExpressions/
├── Makefile
├── pyproject.toml
├── src/bibtex_ris/
│   ├── converter.py     # parseo y conversión (regex)
│   ├── latex.py         # desescapado LaTeX a Unicode
│   └── cli.py           # línea de comandos
└── tests/
    ├── data/            # archivos de entrada (.bib)
    ├── test_converter.py
    ├── test_latex.py
    └── test_cli.py
```

## Instalación

```bash
make setup
```

Crea `.venv`, instala pytest y el paquete (queda el comando `bibtex-ris`).

## Uso

```bash
# BibTeX a RIS
.venv/bin/bibtex-ris archivo.bib -f ris -o salida.ris

# RIS a BibTeX
.venv/bin/bibtex-ris archivo.ris -f bibtex -o salida.bib
```

- `-f ris|bibtex`: formato de salida (obligatorio).
- `-o`: archivo de salida. Si se omite, se genera junto al de entrada como `out.<nombre>.ris|bib` (al ejecutar desde el proyecto con un archivo de `tests/data/`, queda en `tests/data/out.*` y `make clean` lo borra).

También: `make run ARGS="archivo.bib -f ris -o salida.ris"`.

## Makefile

| Objetivo | Descripción |
|---|---|
| `make setup` | Crea el entorno virtual e instala |
| `make test` | Ejecuta la suite de pruebas |
| `make run` | Ejecuta el conversor (`ARGS=...`) |
| `make demo` | Convierte los archivos de `tests/data/` |
| `make clean` | Borra caches y archivos generados |
| `make purge` | Limpia y borra el entorno virtual |

## Salida

RIS con separador de dos espacios y orden canónico `TY, AU, ED, PY, DA, TI, JO/BT, SP, EP, VL, IS, PB, CY, ET, AB, KW, SN, UR, DO, ID, ER`.

- `DA` = `YYYY/MM/DD` (mes/día vacíos si no existen: `YYYY//`).
- `pages` → `SP`/`EP`; `keywords` → una `KW` por línea.
- `ID` (clave) antes de `ER`.
- `SN` → `issn` (revista) o `isbn` (resto) al volver a BibTeX.
- Comandos LaTeX conocidos → Unicode (`{\&}` → `&`, `{\v{R}}` → `Ř`).

## Tests

```bash
make test
```

120 pruebas: roundtrip `BibTeX -> RIS -> BibTeX` sobre los archivos de `tests/data/`, unidades del parser y de la salida, desescapado LaTeX y CLI.