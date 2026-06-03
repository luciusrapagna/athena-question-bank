import hashlib
import re
from pathlib import Path


def gerar_hash(caminho):
    with open(caminho, "rb") as f:
        return hashlib.sha256(f.read()).hexdigest()


def identificar_prova(caminho):
    nome_arquivo = Path(caminho).stem.upper()

    prova = "DESCONHECIDA"
    instituicao = "DESCONHECIDA"
    ano = None

    if "ENAMED" in nome_arquivo:
        prova = "ENAMED"
        instituicao = "INEP"
    elif "ENADE" in nome_arquivo:
        prova = "ENADE"
        instituicao = "INEP"
    elif "REVALIDA" in nome_arquivo:
        prova = "REVALIDA"
        instituicao = "INEP"

    m = re.search(r"(20\d{2})", nome_arquivo)
    if m:
        ano = int(m.group(1))

    return {
        "prova": prova,
        "instituicao": instituicao,
        "ano": ano
    }


def identificar_nome(caminho):
    dados = identificar_prova(caminho)
    return dados["prova"], dados["ano"]
