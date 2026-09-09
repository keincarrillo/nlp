# Conversor BibTeX a RIS

Practica de expresiones regulares: convierte referencias bibliograficas entre **BibTeX** (`.bib`) y **RIS** (`.ris`) usando `re` de Python.

## Estructura

```
regularExpressions/
├── Makefile
├── pyproject.toml
├── src/bibtex_ris/
│   ├── converter.py     # parseo y conversion (regex)
│   ├── latex.py         # desescapado LaTeX a Unicode
│   └── cli.py           # linea de comandos
└── tests/
    └── data/            # archivos de entrada (.bib y .ris)
```

## Instalacion

```bash
make setup
```

Crea `.venv` e instala el paquete (queda el comando `bibtex-ris`).

## Uso

```bash
# BibTeX a RIS
.venv/bin/bibtex-ris archivo.bib -f ris -o salida.ris

# RIS a BibTeX
.venv/bin/bibtex-ris archivo.ris -f bibtex -o salida.bib
```

- `-f ris|bibtex`: formato de salida (obligatorio).
- `-o`: archivo de salida. Si se omite, se genera junto al de entrada como `out.<nombre>.ris|bib` (al ejecutar desde el proyecto con un archivo de `tests/data/`, queda en `tests/data/out.*` y `make clean` lo borra).

Tambien: `make run ARGS="archivo.bib -f ris -o salida.ris"`.

## Makefile

| Objetivo | Descripcion |
|---|---|
| `make setup` | Crea el entorno virtual e instala |
| `make run` | Ejecuta el conversor (`ARGS=...`) |
| `make demo` | Convierte los archivos de `tests/data/` |
| `make clean` | Borra caches y archivos generados |
| `make purge` | Limpia y borra el entorno virtual |

## Salida

RIS con separador de dos espacios y orden canonico `TY, AU, ED, PY, DA, TI, JO/BT, SP, EP, VL, IS, PB, CY, ET, AB, KW, SN, UR, DO, ID, ER`.

- `DA` = `YYYY/MM/DD` (mes/dia vacios si no existen: `YYYY//`).
- `pages` → `SP`/`EP`; `keywords` → una `KW` por linea.
- `ID` (clave) antes de `ER`.
- `SN` → `issn` (revista) o `isbn` (resto) al volver a BibTeX.
- Comandos LaTeX conocidos → Unicode (`{\&}` → `&`, `{\v{R}}` → `Ř`).