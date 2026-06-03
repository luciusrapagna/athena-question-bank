import re
from pathlib import Path
import fitz

def detectar_perfil(texto, nome_arquivo=""):
    t = texto.lower()
    n = nome_arquivo.lower()

    if "gabarito definitivo" in t or "gabarito" in n:
        return "gabarito"

    if "núcleo mineiro" in t or "teste de progresso" in t or "simulado" in n or "teste_progresso" in n:
        return "teste_progresso"

    if "enamed" in t or "enamed" in n:
        return "enamed"

    if "enare" in t or "enare" in n or "medway" in t:
        return "enare"

    if "enade" in t or "enade" in n:
        return "enade"

    return "generico"

def extrair_texto_pdf(pdf_path):
    doc = fitz.open(pdf_path)
    paginas = []

    for page in doc:
        blocks = page.get_text("blocks")
        blocks = sorted(blocks, key=lambda b: (round(b[1], 1), round(b[0], 1)))

        texto_pagina = []
        for b in blocks:
            txt = b[4].strip()
            if txt:
                texto_pagina.append(txt)

        paginas.append("\n".join(texto_pagina))

    return "\n\n".join(paginas)

def limpar_ruido(texto):
    texto = texto or ""
    texto = texto.replace("\uFFFE", "")
    texto = texto.replace("￾", "-")
    texto = texto.replace("\r", "")

    linhas = []
    for linha in texto.splitlines():
        l = linha.strip()

        if not l:
            continue

        if re.search(r"Medway\s*-\s*ENARE", l, re.I):
            continue
        if re.search(r"P[áa]ginas?\s+\d+/\d+", l, re.I):
            continue
        if re.search(r"^\*?[A-Z]?\d{6,}\*?$", l):
            continue
        if "ÁREA LIVRE" in l.upper():
            continue
        if "RASCUNHO" in l.upper():
            continue
        if "CADERNO DE QUESTÕES" in l.upper():
            continue
        if "LEIA COM ATENÇÃO" in l.upper():
            continue

        linhas.append(l)

    texto = "\n".join(linhas)
    texto = re.sub(r"[ \t]+", " ", texto)
    texto = re.sub(r"\n{3,}", "\n\n", texto)

    return texto.strip()

def normalizar_alternativas(texto):
    texto = re.sub(r"(?m)^([A-E])\.\s+", r"(\1) ", texto)
    texto = re.sub(r"(?m)^([A-E])\)\s+", r"(\1) ", texto)
    texto = re.sub(r"(?m)^\(([A-E])\)\s*", r"(\1) ", texto)
    return texto

def padrao_inicio(perfil, texto):
    # padrão QUESTÃO 1
    if re.search(r"QUESTÃO\s+\d{1,3}", texto, re.I):
        return r"(?=QUESTÃO\s+\d{1,3}\.?)"

    # padrão 1. Paciente...
    if re.search(r"(?m)^\d{1,3}\.\s+", texto):
        return r"(?m)(?=^\d{1,3}\.\s+)"

    return r"(?im)(?=(?:quest[aã]o\s*)?\d{1,3}[\.\)]\s+)"

def obter_numero(bloco):
    m = re.search(r"QUESTÃO\s+(\d{1,3})", bloco, re.I)
    if m:
        return int(m.group(1))

    m = re.search(r"^(\d{1,3})[\.\)]\s+", bloco.strip(), re.I)
    if m:
        return int(m.group(1))

    return None

def aparar_bloco(bloco):
    bloco = normalizar_alternativas(bloco)

    proximo_lixo = re.search(
        r"(Medway|Páginas|Núcleo Mineiro|Teste de Progresso|ENADE\s*-\s*\d{4})",
        bloco,
        re.I
    )

    if proximo_lixo:
        bloco = bloco[:proximo_lixo.start()].strip()

    return bloco.strip()

def extrair_questoes_por_perfil(texto, perfil):
    texto = limpar_ruido(texto)
    texto = normalizar_alternativas(texto)

    padrao = padrao_inicio(perfil, texto)
    partes = re.split(padrao, texto)

    questoes = []

    for parte in partes:
        bloco = parte.strip()

        if len(bloco) < 80:
            continue

        numero = obter_numero(bloco)

        if numero is None:
            continue

        if not (1 <= numero <= 200):
            continue

        bloco = aparar_bloco(bloco)
        questoes.append((numero, bloco))

    melhores = {}

    for numero, bloco in questoes:
        if numero not in melhores or len(bloco) > len(melhores[numero]):
            melhores[numero] = bloco

    return sorted(melhores.items(), key=lambda x: x[0])

def ler_pdf_inteligente(pdf_path):
    texto = extrair_texto_pdf(pdf_path)
    perfil = detectar_perfil(texto, Path(pdf_path).name)
    questoes = extrair_questoes_por_perfil(texto, perfil)

    return {
        "perfil": perfil,
        "texto": limpar_ruido(texto),
        "questoes": questoes
    }
