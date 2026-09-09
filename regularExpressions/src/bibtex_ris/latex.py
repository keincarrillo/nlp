"""desescapa comandos latex a caracteres unicode"""

# simbolos latex comunes
LATEX_SYMBOLS = {
    r"{\&}": '&',
    r"{\%}": '%',
    r"{\#}": '#',
    r"{\_}": '_',
    r"{\$}": '$',
    r"{\{": '{',
    r"{\}}": '}',
}

# acentos y diacriticos latex a caracteres unicode
LATEX_ACCENTS = {
    r"{\'a}": 'á', r"{\'e}": 'é', r"{\'i}": 'í', r"{\'o}": 'ó', r"{\'u}": 'ú',
    r"{\'A}": 'Á', r"{\'E}": 'É', r"{\'I}": 'Í', r"{\'O}": 'Ó', r"{\'U}": 'Ú',
    r"{\`a}": 'à', r"{\`e}": 'è', r"{\`i}": 'ì', r"{\`o}": 'ò', r"{\`u}": 'ù',
    r"{\`A}": 'À', r"{\`E}": 'È', r"{\`I}": 'Ì', r"{\`O}": 'Ò', r"{\`U}": 'Ù',
    r"{\^a}": 'â', r"{\^e}": 'ê', r"{\^i}": 'î', r"{\^o}": 'ô', r"{\^u}": 'û',
    r"{\^A}": 'Â', r"{\^E}": 'Ê', r"{\^I}": 'Î', r"{\^O}": 'Ô', r"{\^U}": 'Û',
    r'{\"a}': 'ä', r'{\"e}': 'ë', r'{\"i}': 'ï', r'{\"o}': 'ö', r'{\"u}': 'ü',
    r'{\"A}': 'Ä', r'{\"E}': 'Ë', r'{\"I}': 'Ï', r'{\"O}': 'Ö', r'{\"U}': 'Ü',
    r'{\~a}': 'ã', r'{\~n}': 'ñ', r'{\~o}': 'õ', r'{\~N}': 'Ñ',
    r'{\c{c}}': 'ç', r'{\c{C}}': 'Ç',
    r'{\v{c}}': 'č', r'{\v{C}}': 'Č', r'{\v{s}}': 'š', r'{\v{S}}': 'Š',
    r'{\v{r}}': 'ř', r'{\v{R}}': 'Ř', r'{\v{z}}': 'ž', r'{\v{Z}}': 'Ž',
    r'{\v{d}}': 'ď', r'{\v{D}}': 'Ď', r'{\v{t}}': 'ť', r'{\v{T}}': 'Ť',
    r'{\v{n}}': 'ň', r'{\v{N}}': 'Ň', r'{\v{e}}': 'ě', r'{\v{E}}': 'Ě',
}

# tabla completa para un solo recorrido
LATEX_MAP = {**LATEX_SYMBOLS, **LATEX_ACCENTS}


def unescape_latex(text):
    """reemplaza cada comando latex conocido por su caracter unicode"""
    for token, char in LATEX_MAP.items():
        text = text.replace(token, char)
    return text