"""Tests del desescapado LaTeX"""

import pytest

from bibtex_ris.latex import LATEX_ACCENTS, LATEX_SYMBOLS, unescape_latex


@pytest.mark.parametrize('token,char', LATEX_SYMBOLS.items())
def test_symbols(token, char):
    assert unescape_latex(token) == char


@pytest.mark.parametrize('token,char', LATEX_ACCENTS.items())
def test_accents(token, char):
    assert unescape_latex(token) == char


def test_symbols_within_text():
    text = r"Journal of Electrical Engineering {\&} Technology"
    assert unescape_latex(text) == 'Journal of Electrical Engineering & Technology'


def test_accents_within_text():
    text = r"{{\v{R}}epa, V{\'a}clav}"
    assert unescape_latex(text) == '{Řepa, Václav}'


def test_percent_within_text():
    text = r"overall accuracy of 97{\%}"
    assert unescape_latex(text) == 'overall accuracy of 97%'


def test_unknown_command_preserved():
    text = r"valor {\zz{}} crudo"
    assert unescape_latex(text) == text


def test_plain_text_unchanged():
    text = 'Texto plano sin comandos'
    assert unescape_latex(text) == text