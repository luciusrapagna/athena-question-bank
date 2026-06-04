import re
import sqlite3
from collections import Counter

DB_PATH = "app/db/planos_aula.db"

STOPWORDS = {
    "a", "o", "as", "os", "de", "da", "do", "das", "dos", "em", "para",
    "com", "por", "um", "uma", "e", "ou", "no", "na", "nos", "nas",
    "objetivo", "objetivos", "conteúdo", "conteudos", "metodologia",
    "referência", "referencias", "aula", "plano", "ensino"
}


def limpar_texto(texto):
    texto = texto.replace("\t", " ")
    texto = re.sub(r"\s+", " ", texto)
    return texto.strip()


def normalizar_tema(tema):
    tema = limpar_texto(tema)
    tema = re.sub(r"^[\-\•\*\d\.\)\s]+", "", tema)
    tema = tema.strip(" .;:-")
    return tema


def extrair_linhas_relevantes(texto):
    temas = []

    for linha in texto.splitlines():
        linha = normalizar_tema(linha)

        if len(linha) < 5:
            continue

        if len(linha) > 140:
            continue

        if not re.search(r"[A-Za-zÀ-ÿ]", linha):
            continue

        if linha.lower() in STOPWORDS:
            continue

        temas.append(linha)

    return temas


def extrair_palavras_chave(texto, limite=30):
    texto = texto.lower()
    texto = re.sub(r"[^a-zà-ÿ0-9\s]", " ", texto)

    palavras = [
        p for p in texto.split()
        if len(p) > 4 and p not in STOPWORDS
    ]

    contagem = Counter(palavras)

    return [p for p, _ in contagem.most_common(limite)]


def extrair_temas(texto):
    temas_linhas = extrair_linhas_relevantes(texto)
    palavras_chave = extrair_palavras_chave(texto)

    temas = temas_linhas + palavras_chave

    vistos = set()
    temas_unicos = []

    for tema in temas:
        chave = tema.lower().strip()

        if chave not in vistos:
            vistos.add(chave)
            temas_unicos.append(tema)

    return temas_unicos


def limpar_temas_anteriores(cur, plano_id):
    cur.execute(
        "DELETE FROM temas_plano WHERE plano_id = ?",
        (plano_id,)
    )


def processar_planos():
    con = sqlite3.connect(DB_PATH)
    cur = con.cursor()

    planos = cur.execute(
        """
        SELECT id, conteudo
        FROM planos_aula
        """
    ).fetchall()

    total_temas = 0

    for plano_id, conteudo in planos:
        limpar_temas_anteriores(cur, plano_id)

        if not conteudo:
            continue

        temas = extrair_temas(conteudo)

        for tema in temas:
            cur.execute(
                """
                INSERT INTO temas_plano (plano_id, tema)
                VALUES (?, ?)
                """,
                (plano_id, tema)
            )

        total_temas += len(temas)

    con.commit()
    con.close()

    print(f"Extração concluída. Total de temas extraídos: {total_temas}")


if __name__ == "__main__":
    processar_planos()
