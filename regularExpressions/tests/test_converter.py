"""Tests del conversor BibTeX a RIS"""

from pathlib import Path

import pytest

from bibtex_ris.converter import BibtexRisConverter

DATA_DIR = Path(__file__).resolve().parent / 'data'

CONVERTER = BibtexRisConverter()


def read_bib(name):
    return (DATA_DIR / name).read_text(encoding='utf-8-sig')


def convert_bib_to_ris(bib_content):
    entries = CONVERTER.parse_bibtex(bib_content)
    return [CONVERTER.bibtex_entry_to_ris(entry) for entry in entries]


def semantic_entry(entry):
    """Normaliza una entrada para comparar semanticamente"""
    fields = dict(entry['fields'])
    for name, value in list(fields.items()):
        if name == 'pages' and isinstance(value, str):
            fields[name] = value.replace('--', '-')
    return {'type': entry['type'], 'id': entry['id'], 'fields': fields}


# Roundtrip BibTeX -> RIS -> BibTeX sobre los archivos de prueba
@pytest.mark.parametrize('bib', [
    'journal1.bib',
    'journal2.bib',
    'conference1.bib',
    'conference2.bib',
])
def test_roundtrip_bib_to_ris_to_bib(bib):
    original = CONVERTER.parse_bibtex(read_bib(bib))

    ris_output = convert_bib_to_ris(read_bib(bib))
    ris_entries = CONVERTER.parse_ris('\n'.join(ris_output))

    roundtripped = []
    for entry in ris_entries:
        bibtex_text = CONVERTER.ris_entry_to_bibtex(entry)
        roundtripped.extend(CONVERTER.parse_bibtex(bibtex_text))

    assert [semantic_entry(e) for e in roundtripped] == [semantic_entry(e) for e in original]


# Parser BibTeX

def test_parse_bibtex_single_entry():
    content = '@Article{k1, author={Uno, A}, title={Titulo}, year={2020}}'
    entries = CONVERTER.parse_bibtex(content)
    assert len(entries) == 1
    assert entries[0]['type'] == 'article'
    assert entries[0]['id'] == 'k1'
    assert entries[0]['fields']['year'] == '2020'


def test_parse_bibtex_multiple_entries():
    content = (
        '@Article{k1, author={Uno, A}, title={T1}, year={2020}}\n'
        '@Book{k2, author={Dos, B}, title={T2}, year={2021}}'
    )
    entries = CONVERTER.parse_bibtex(content)
    assert [e['id'] for e in entries] == ['k1', 'k2']
    assert [e['type'] for e in entries] == ['article', 'book']


def test_parse_bibtex_quoted_values():
    content = '@Article{k1, title="Entre comillas", year={2020}}'
    entry = CONVERTER.parse_bibtex(content)[0]
    assert entry['fields']['title'] == 'Entre comillas'


def test_parse_bibtex_authors_multiline():
    content = '@Article{k1, author={Uno, A\nand Dos, B\nand Tres, C}, title={T}}'
    entry = CONVERTER.parse_bibtex(content)[0]
    assert entry['fields']['author'] == ['Uno, A', 'Dos, B', 'Tres, C']


def test_parse_bibtex_case_insensitive():
    content = '@inproceedings{k1, Title={Hola}, YEAR={1999}}'
    entry = CONVERTER.parse_bibtex(content)[0]
    assert entry['type'] == 'inproceedings'
    assert entry['fields']['title'] == 'Hola'
    assert entry['fields']['year'] == '1999'


def test_parse_bibtex_nested_latex():
    content = r"@Article{k1, author={{\v{R}}epa, V{\'a}clav}, title={T}}"
    entry = CONVERTER.parse_bibtex(content)[0]
    assert entry['fields']['author'] == ['Řepa, Václav']


def test_parse_bibtex_bom_stripped():
    content = '\ufeff@Article{k1, author={Uno, A}, title={T}}'
    entry = CONVERTER.parse_bibtex(content)[0]
    assert entry['id'] == 'k1'


# Parser RIS

def test_parse_ris_repeated_tags_become_list():
    content = (
        'TY  - JOUR\n'
        'AU  - Uno, A\n'
        'AU  - Dos, B\n'
        'PY  - 2020\n'
        'ER  - \n'
    )
    entry = CONVERTER.parse_ris(content)[0]
    assert entry['TY'] == 'JOUR'
    assert entry['AU'] == ['Uno, A', 'Dos, B']
    assert entry['PY'] == '2020'


def test_parse_ris_multiple_entries():
    content = (
        'TY  - JOUR\n'
        'ID  - k1\n'
        'ER  - \n'
        '\n'
        'TY  - BOOK\n'
        'ID  - k2\n'
        'ER  - \n'
    )
    entries = CONVERTER.parse_ris(content)
    assert [e['ID'] for e in entries] == ['k1', 'k2']
    assert [e['TY'] for e in entries] == ['JOUR', 'BOOK']


def test_parse_ris_tag_with_digits():
    content = 'TY  - JOUR\nT2  - Acta\nER  - \n'
    entry = CONVERTER.parse_ris(content)[0]
    assert entry['T2'] == 'Acta'


def test_parse_ris_values_with_spaces():
    content = 'TY  - JOUR\nJO  - Journal of Electrical Engineering & Technology\nER  - \n'
    entry = CONVERTER.parse_ris(content)[0]
    assert entry['JO'] == 'Journal of Electrical Engineering & Technology'


# Salida BibTeX -> RIS

def test_ris_types_for_entry_types():
    cases = {
        'article': 'JOUR',
        'inproceedings': 'CONF',
        'book': 'BOOK',
        'chapter': 'CHAP',
        'thesis': 'THES',
        'misc': 'JOUR',
    }
    for bib_type, ris_type in cases.items():
        entry = {'type': bib_type, 'id': 'k', 'fields': {'title': 'T'}}
        assert CONVERTER.bibtex_entry_to_ris(entry).startswith('TY  - ' + ris_type)


def test_ris_lines_use_two_space_separator():
    entry = {'type': 'article', 'id': 'k', 'fields': {'title': 'T', 'year': '2020'}}
    output = CONVERTER.bibtex_entry_to_ris(entry)
    lines = output.splitlines()
    assert all(line[2:4] == '  ' for line in lines if line != 'ER  -')


def test_ris_pages_range_single_hyphen():
    entry = {'type': 'article', 'id': 'k', 'fields': {'pages': '165-183'}}
    output = CONVERTER.bibtex_entry_to_ris(entry)
    assert 'SP  - 165' in output
    assert 'EP  - 183' in output


def test_ris_pages_range_latex_dash():
    entry = {'type': 'article', 'id': 'k', 'fields': {'pages': '375--386'}}
    output = CONVERTER.bibtex_entry_to_ris(entry)
    assert 'SP  - 375' in output
    assert 'EP  - 386' in output


def test_ris_pages_single_value_only_sp():
    entry = {'type': 'article', 'id': 'k', 'fields': {'pages': '12'}}
    output = CONVERTER.bibtex_entry_to_ris(entry)
    assert 'SP  - 12' in output
    assert 'EP' not in output


def test_ris_keywords_written_one_per_line():
    entry = {'type': 'article', 'id': 'k', 'fields': {'keywords': 'rojo, verde, azul'}}
    output = CONVERTER.bibtex_entry_to_ris(entry)
    assert 'KW  - rojo' in output
    assert 'KW  - verde' in output
    assert 'KW  - azul' in output


def test_ris_authors_and_editors_in_order():
    entry = {
        'type': 'inproceedings',
        'id': 'k',
        'fields': {
            'author': ['Uno, A', 'Dos, B'],
            'editor': ['Ed, X'],
            'title': 'T',
        },
    }
    lines = CONVERTER.bibtex_entry_to_ris(entry).splitlines()
    assert lines[1] == 'AU  - Uno, A'
    assert lines[2] == 'AU  - Dos, B'
    assert lines[3] == 'ED  - Ed, X'
    assert lines[4] == 'TI  - T'


def test_ris_year_and_da_after_authors():
    entry = {
        'type': 'article',
        'id': 'k',
        'fields': {'author': ['Uno, A'], 'year': '2024', 'month': 'Sep', 'day': '01', 'title': 'T'},
    }
    lines = CONVERTER.bibtex_entry_to_ris(entry).splitlines()
    assert lines == [
        'TY  - JOUR',
        'AU  - Uno, A',
        'PY  - 2024',
        'DA  - 2024/09/01',
        'TI  - T',
        'ID  - k',
        'ER  -',
    ]


def test_ris_date_year_only():
    assert CONVERTER._build_date('2023') == '2023//'
    assert CONVERTER._build_date('2023', 'Sep') == '2023/09/'
    assert CONVERTER._build_date('2023', 'September') == '2023/09/'
    assert CONVERTER._build_date('2024', 'Sep', '01') == '2024/09/01'
    assert CONVERTER._build_date('2024', '9', '1') == '2024/09/1'


def test_ris_issn_and_isbn_map_to_sn():
    entry = {'type': 'article', 'id': 'k', 'fields': {'issn': '2192-6360'}}
    assert 'SN  - 2192-6360' in CONVERTER.bibtex_entry_to_ris(entry)

    entry = {'type': 'inproceedings', 'id': 'k', 'fields': {'isbn': '978-3-031-44693-1'}}
    assert 'SN  - 978-3-031-44693-1' in CONVERTER.bibtex_entry_to_ris(entry)


def test_ris_id_is_last_before_er():
    entry = {'type': 'article', 'id': 'k1', 'fields': {'title': 'T'}}
    lines = CONVERTER.bibtex_entry_to_ris(entry).splitlines()
    assert lines[-2] == 'ID  - k1'
    assert lines[-1] == 'ER  -'


# Salida RIS -> BibTeX

def test_bibtex_from_ris_pages_join_with_double_dash():
    entry = {'TY': 'JOUR', 'SP': '165', 'EP': '183', 'ID': 'k1'}
    output = CONVERTER.ris_entry_to_bibtex(entry)
    assert 'pages = {165--183}' in output


def test_bibtex_from_ris_pages_without_ep():
    entry = {'TY': 'JOUR', 'SP': '12', 'ID': 'k1'}
    output = CONVERTER.ris_entry_to_bibtex(entry)
    assert 'pages = {12}' in output


def test_bibtex_from_ris_da_splits_month_and_day():
    entry = {'TY': 'JOUR', 'PY': '2024', 'DA': '2024/09/01', 'ID': 'k1'}
    output = CONVERTER.ris_entry_to_bibtex(entry)
    assert 'year = {2024}' in output
    assert 'month = {Sep}' in output
    assert 'day = {01}' in output


def test_bibtex_from_ris_sn_is_issn_for_jour():
    entry = {'TY': 'JOUR', 'SN': '2192-6360', 'ID': 'k1'}
    output = CONVERTER.ris_entry_to_bibtex(entry)
    assert 'issn = {2192-6360}' in output


def test_bibtex_from_ris_sn_is_isbn_for_conf():
    entry = {'TY': 'CONF', 'SN': '978-3-031-44693-1', 'ID': 'k1'}
    output = CONVERTER.ris_entry_to_bibtex(entry)
    assert 'isbn = {978-3-031-44693-1}' in output


def test_bibtex_from_ris_keywords_joined():
    entry = {'TY': 'JOUR', 'KW': ['rojo', 'verde'], 'ID': 'k1'}
    output = CONVERTER.ris_entry_to_bibtex(entry)
    assert 'keywords = {rojo, verde}' in output


def test_bibtex_from_ris_authors_joined():
    entry = {'TY': 'JOUR', 'AU': ['Uno, A', 'Dos, B'], 'ID': 'k1'}
    output = CONVERTER.ris_entry_to_bibtex(entry)
    assert 'author = {Uno, A and Dos, B}' in output


def test_bibtex_from_ris_t2_maps_to_booktitle():
    entry = {'TY': 'CONF', 'T2': 'Acta', 'BT': 'Acta Alterna', 'ID': 'k1'}
    output = CONVERTER.ris_entry_to_bibtex(entry)
    assert 'booktitle = {Acta}' in output


def test_bibtex_from_ris_default_id_and_type():
    entry = {'TY': 'MISC', 'TI': 'T'}
    output = CONVERTER.ris_entry_to_bibtex(entry)
    assert output.startswith('@article{unknown,')
    assert 'title = {T}' in output


def test_bibtex_entry_ends_with_closing_brace():
    entry = {'TY': 'JOUR', 'TI': 'T', 'ID': 'k1'}
    output = CONVERTER.ris_entry_to_bibtex(entry)
    assert output.endswith('}')


# convert_file

def test_convert_file_bib_to_ris(tmp_path):
    src = tmp_path / 'in.bib'
    src.write_text('@Article{k1, author={Uno, A}, title={T}, year={2020}}', encoding='utf-8')
    dst = tmp_path / 'out.ris'

    count = CONVERTER.convert_file(str(src), str(dst), 'ris')
    assert count == 1
    assert dst.read_text(encoding='utf-8') == (
        'TY  - JOUR\n'
        'AU  - Uno, A\n'
        'PY  - 2020\n'
        'DA  - 2020//\n'
        'TI  - T\n'
        'ID  - k1\n'
        'ER  -\n'
    )


def test_convert_file_ris_to_bib(tmp_path):
    src = tmp_path / 'in.ris'
    src.write_text('TY  - JOUR\nTI  - T\nID  - k1\nER  - \n', encoding='utf-8')
    dst = tmp_path / 'out.bib'

    count = CONVERTER.convert_file(str(src), str(dst), 'bibtex')
    assert count == 1
    assert '@article{k1,' in dst.read_text(encoding='utf-8')


def test_convert_file_reads_bom(tmp_path):
    src = tmp_path / 'in.bib'
    src.write_bytes(b'\xef\xbb\xbf@Article{k1, author={Uno, A}, title={T}}')
    dst = tmp_path / 'out.ris'

    count = CONVERTER.convert_file(str(src), str(dst), 'ris')
    assert count == 1
    assert 'ID  - k1' in dst.read_text(encoding='utf-8')