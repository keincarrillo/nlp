.PHONY: help setup install test run demo clean purge

help:
	@echo "make setup   - crea el entorno virtual aislado e instala dependencias"
	@echo "make install - instala el paquete y las dependencias de desarrollo"
	@echo "make test    - ejecuta la suite de pruebas con pytest"
	@echo "make run     - ejecuta el conversor con argumentos ARGS=..."
	@echo "make demo    - convierte todos los archivos de tests/data/ (BibTeX y RIS)"
	@echo "make clean   - borra caches y archivos generados"
	@echo "make purge   - limpia y ademas borra el entorno virtual"

PYTHON := python3
VENV := .venv
VENV_PY := $(VENV)/bin/python
VENV_PIP := $(VENV)/bin/pip
BIN := $(VENV)/bin/bibtex-ris

$(VENV_PY):
	$(PYTHON) -m venv $(VENV)
	$(VENV_PIP) install --upgrade pip

setup: $(VENV_PY)
	$(VENV_PIP) install -r requirements-dev.txt
	$(VENV_PIP) install -e .

install: $(VENV_PY)
	$(VENV_PIP) install -r requirements-dev.txt
	$(VENV_PIP) install -e .

test: install
	$(VENV_PY) -m pytest tests -v

run: install
	$(BIN) $(ARGS)

demo: install
	@echo "BibTeX -> RIS"
	@for f in tests/data/*.bib; do \
		case "$$f" in \
			*/out.*|*_convertido.bib) ;; \
			*) $(BIN) "$$f" -f ris -o "tests/data/out.$$(basename "$$f" .bib).ris" ;; \
		esac; \
	done
	@echo "RIS -> BibTeX"
	@for f in tests/data/*.ris; do \
		case "$$f" in \
			*/out.*|*_convertido.ris) ;; \
			*) $(BIN) "$$f" -f bibtex -o "tests/data/out.$$(basename "$$f" .ris).bib" ;; \
		esac; \
	done
	@echo "Archivos generados en tests/data/out.*"

clean:
	rm -rf .pytest_cache
	find . -name '*.egg-info' -type d -prune -exec rm -rf {} +
	rm -rf build dist
	find . -name __pycache__ -type d -prune -exec rm -rf {} +
	rm -f tests/data/out.*

purge: clean
	rm -rf $(VENV)