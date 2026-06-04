from pathlib import Path
import hashlib
import re


def gerar_hash(caminho):
    caminho = Path(caminho)
    h = hashlib.sha256()

    with open(caminho, "rb") as f:
        for bloco in iter(lambda: f.read(8192), b""):
            h.update(bloco)

    return h.hexdigest()


def identificar_nome(caminho):
    caminho = Path(caminho)
    nome = caminho.stem

    dados = {
        "arquivo": caminho.name,
        "nome_prova": nome,
        "disciplina": None,
        "periodo": None,
        "turma": None,
        "ano": None,
        "semestre": None,
        "hash": gerar_hash(caminho),
    }

    match_periodo = re.search(r"(\d+)\s*[ºo]?\s*periodo", nome, re.IGNORECASE)
    if match_periodo:
        dados["periodo"] = match_periodo.group(1)

    match_turma = re.search(r"\b([1-9][AB])\b", nome, re.IGNORECASE)
    if match_turma:
        dados["turma"] = match_turma.group(1).upper()

    match_ano = re.search(r"(20\d{2})", nome)
    if match_ano:
        dados["ano"] = match_ano.group(1)

    match_semestre = re.search(r"(20\d{2})[._-]?([12])", nome)
    if match_semestre:
        dados["ano"] = match_semestre.group(1)
        dados["semestre"] = match_semestre.group(2)

    return dados


def identificar_prova(caminho):
    return identificar_nome(caminho)
