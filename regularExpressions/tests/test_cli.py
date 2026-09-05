"""Tests de la interfaz de linea de comandos"""

import subprocess
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent


def run_cli(args):
    """Ejecuta el CLI en un subproceso"""
    return subprocess.run(
        [sys.executable, '-m', 'bibtex_ris.cli'] + list(args),
        capture_output=True,
        text=True,
        encoding='utf-8',
        cwd=str(PROJECT_ROOT),
    )


def test_cli_converts_bib_to_ris(tmp_path):
    src = tmp_path / 'in.bib'
    src.write_text('@Article{k1, author={Uno, A}, title={T}, year={2020}}', encoding='utf-8')
    dst = tmp_path / 'out.ris'

    result = run_cli([str(src), '-f', 'ris', '-o', str(dst)])
    assert result.returncode == 0
    assert dst.exists()

    content = dst.read_text(encoding='utf-8')
    assert 'TY  - JOUR' in content
    assert 'ID  - k1' in content
    assert 'ER  -' in content


def test_cli_converts_ris_to_bib(tmp_path):
    src = tmp_path / 'in.ris'
    src.write_text('TY  - JOUR\nTI  - T\nID  - k1\nER  - \n', encoding='utf-8')
    dst = tmp_path / 'out.bib'

    result = run_cli([str(src), '-f', 'bibtex', '-o', str(dst)])
    assert result.returncode == 0
    assert '@article{k1,' in dst.read_text(encoding='utf-8')


def test_cli_default_output_name(tmp_path):
    src = tmp_path / 'paper.bib'
    src.write_text('@Article{k1, title={T}}', encoding='utf-8')

    result = run_cli([str(src), '-f', 'ris'])
    assert result.returncode == 0
    generated = tmp_path / 'out.paper.ris'
    assert generated.exists()
    assert 'Conversion completada exitosamente' in result.stdout
    assert 'Entradas procesadas: 1' in result.stdout


def test_cli_missing_input_file(tmp_path):
    missing = tmp_path / 'no_existe.bib'
    result = run_cli([str(missing), '-f', 'ris'])
    assert result.returncode == 1
    assert 'no existe' in result.stderr


def test_cli_verbose_output(tmp_path):
    src = tmp_path / 'in.bib'
    src.write_text('@Article{k1, title={T}}', encoding='utf-8')
    dst = tmp_path / 'out.ris'

    result = run_cli([str(src), '-f', 'ris', '-o', str(dst), '-v'])
    assert result.returncode == 0
    assert 'Leyendo:' in result.stdout
    assert 'Convirtiendo a: RIS' in result.stdout


def test_cli_rejects_invalid_format(tmp_path):
    src = tmp_path / 'in.bib'
    src.write_text('@Article{k1, title={T}}', encoding='utf-8')

    result = run_cli([str(src), '-f', 'xml'])
    assert result.returncode != 0


def test_cli_sample_data_files(tmp_path):
    data_dir = PROJECT_ROOT / 'tests' / 'data'
    dst = tmp_path / 'out.journal1.ris'

    result = run_cli([str(data_dir / 'journal1.bib'), '-f', 'ris', '-o', str(dst)])
    assert result.returncode == 0
    content = dst.read_text(encoding='utf-8')
    assert 'DA  - 2024/09/01' in content
    assert 'ID  - Ohri2024' in content