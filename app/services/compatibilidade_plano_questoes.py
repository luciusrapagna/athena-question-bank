import sqlite3
import re
from difflib import SequenceMatcher

DB_PATH = "app/db/planos_aula.db"


def normalizar(texto):
    if texto is None:
        return ""

    texto = texto.lower()
    texto = re.sub(r"[^a-zà-ÿ0-9\s]", " ", texto)
    texto = re.sub(r"\s+", " ", texto)

    return texto.strip()


def similaridade(a, b):
    a = normalizar(a)
    b = normalizar(b)

    if not a or not b:
        return 0.0

    return SequenceMatcher(None, a, b).ratio()


def buscar_questoes(cur):
    tabelas = cur.execute(
        "SELECT name FROM sqlite_master WHERE type='table';"
    ).fetchall()

    nomes = [t[0] for t in tabelas]

    if "questoes" not in nomes:
        print("Tabela 'questoes' não encontrada.")
        return []

    colunas = cur.execute("PRAGMA table_info(questoes);").fetchall()
    nomes_colunas = [c[1] for c in colunas]

    possiveis_textos = [
        "enunciado",
        "texto",
        "questao",
        "conteudo",
        "pergunta"
    ]

    coluna_texto = None

    for nome in possiveis_textos:
        if nome in nomes_colunas:
            coluna_texto = nome
            break

    if coluna_texto is None:
        print("Nenhuma coluna textual encontrada na tabela questoes.")
        print("Colunas disponíveis:", nomes_colunas)
        return []

    return cur.execute(
        f"SELECT id, {coluna_texto} FROM questoes;"
    ).fetchall()


def calcular_compatibilidade():
    con = sqlite3.connect(DB_PATH)
    cur = con.cursor()

    cur.execute("DELETE FROM compatibilidade_plano_questao;")

    planos = cur.execute(
        """
        SELECT p.id, p.aula, GROUP_CONCAT(t.tema, ' ')
        FROM planos_aula p
        LEFT JOIN temas_plano t ON t.plano_id = p.id
        GROUP BY p.id, p.aula
        """
    ).fetchall()

    questoes = buscar_questoes(cur)

    if not questoes:
        con.commit()
        con.close()
        print("Compatibilidade não calculada porque não há questões disponíveis.")
        return

    total = 0

    for plano_id, aula, temas in planos:
        temas = temas or ""

        for questao_id, texto_questao in questoes:
            score = similaridade(temas, texto_questao)

            if score >= 0.15:
                cur.execute(
                    """
                    INSERT INTO compatibilidade_plano_questao (
                        plano_id,
                        questao_id,
                        score
                    )
                    VALUES (?, ?, ?)
                    """,
                    (plano_id, questao_id, score)
                )
                total += 1

    con.commit()
    con.close()

    print(f"Compatibilidade calculada. Total de vínculos: {total}")


if __name__ == "__main__":
    calcular_compatibilidade()
