import re
import sqlite3
from pathlib import Path

DB_PATH = Path("database/question_bank.db")

def conectar():
    return sqlite3.connect(DB_PATH)

def criar_tabela():
    conn = conectar()
    cur = conn.cursor()

    cur.execute("""
    CREATE TABLE IF NOT EXISTS questoes_struct (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        documento_id INTEGER,
        numero_questao INTEGER,
        enunciado TEXT,
        alternativa_a TEXT,
        alternativa_b TEXT,
        alternativa_c TEXT,
        alternativa_d TEXT,
        texto_original TEXT,
        qualidade TEXT
    )
    """)

    conn.commit()
    conn.close()

def separar_alternativas(texto):
    texto = texto or ""

    padrao = re.compile(
        r"\(A\)\s*(.*?)\s*\(B\)\s*(.*?)\s*\(C\)\s*(.*?)\s*\(D\)\s*(.*)",
        re.S
    )

    m = padrao.search(texto)

    if not m:
        return None

    enunciado = texto[:m.start()].strip()
    a = m.group(1).strip()
    b = m.group(2).strip()
    c = m.group(3).strip()
    d = m.group(4).strip()

    # corta sobra de próxima questão dentro da alternativa D
    d = re.split(r"\n\s*(?:QUESTÃO\s*)?\d{1,3}[\.\)]?\s+", d, maxsplit=1)[0].strip()

    return enunciado, a, b, c, d

def qualidade_struct(enunciado, a, b, c, d):
    if all([enunciado, a, b, c, d]) and len(enunciado) > 80:
        return "valida_struct"

    return "revisar_manual"

def main():
    criar_tabela()

    conn = conectar()
    cur = conn.cursor()

    cur.execute("DELETE FROM questoes_struct")

    cur.execute("""
    SELECT documento_id, numero_questao, texto_questao
    FROM questoes_extraidas
    """)

    rows = cur.fetchall()

    salvas = 0
    revisar = 0

    for documento_id, numero, texto in rows:
        partes = separar_alternativas(texto)

        if partes:
            enunciado, a, b, c, d = partes
            q = qualidade_struct(enunciado, a, b, c, d)
        else:
            enunciado = texto
            a = b = c = d = ""
            q = "revisar_manual"

        cur.execute("""
        INSERT INTO questoes_struct
        (documento_id, numero_questao, enunciado, alternativa_a, alternativa_b,
         alternativa_c, alternativa_d, texto_original, qualidade)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (documento_id, numero, enunciado, a, b, c, d, texto, q))

        if q == "valida_struct":
            salvas += 1
        else:
            revisar += 1

    conn.commit()

    cur.execute("SELECT qualidade, COUNT(*) FROM questoes_struct GROUP BY qualidade")
    print(cur.fetchall())

    conn.close()

    print(f"Questões estruturadas válidas: {salvas}")
    print(f"Revisão manual: {revisar}")

if __name__ == "__main__":
    main()
