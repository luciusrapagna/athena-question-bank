import re
from pathlib import Path
import fitz

def detectar_perfil(texto, nome_arquivo=""):
    t = texto.lower()
    n = nome_arquivo.lower()

    if "enamed" in t or "enamed" in n:
        return "enamed"

    if "enare" in t or "enare" in n:
        return "enare"

    if "enade" in t or "enade" in n:
        return "enade"

    if "núcleo mineiro" in t or "teste de progresso" in t:
        return "teste_progresso"

    if "gabarito definitivo" in t:
        return "gabarito"

    return "generico"

def extrair_texto_por_blocos(pdf_path):
    doc = fitz.open(pdf_path)
    paginas = []

    for page in doc:
        texto = page.get_text()
        paginas.append(texto)

    return "\n\n".join(paginas)

def limpar_ruido(texto):
    texto = texto.replace("￾", "-")
    texto = re.sub(r"\n{3,}", "\n\n", texto)
    return texto

def extrair_questoes_por_perfil(texto, perfil):

    if perfil == "enamed":
        padrao = r"(?=QUESTÃO\s+\d{1,3})"

    elif perfil == "enare":
        padrao = r"(?=QUESTÃO\s+\d{1,3})"

    elif perfil == "enade":
        padrao = r"(?=QUESTÃO\s+\d{1,3})"

    elif perfil == "teste_progresso":
        padrao = r"(?m)(?=^\d{1,3}\.\s+)"

    else:
        padrao = r"(?im)(?=(?:QUESTÃO\s*)?\d{1,3}[\.\)]\s+)"

    partes = re.split(padrao, texto)

    questoes = []

    for parte in partes:
        parte = parte.strip()

        if len(parte) < 120:
            continue

        m = re.search(r"(\d{1,3})", parte)

        if not m:
            continue

        numero = int(m.group(1))

        if 1 <= numero <= 200:
            questoes.append((numero, parte))

    return questoes

def ler_pdf_inteligente(pdf_path):

    texto = extrair_texto_por_blocos(pdf_path)

    perfil = detectar_perfil(
        texto,
        Path(pdf_path).name
    )

    texto = limpar_ruido(texto)

    questoes = extrair_questoes_por_perfil(
        texto,
        perfil
    )

    return {
        "perfil": perfil,
        "texto": texto,
        "questoes": questoes
    }
