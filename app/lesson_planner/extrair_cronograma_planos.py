import re
import sqlite3

DB_PATH = "app/db/planos_aula.db"

def normalizar(texto):
    return re.sub(r"\s+", " ", texto or "").strip()

def extrair_linhas_cronograma(texto, ano="2026"):
    linhas = texto.splitlines()
    registros = []
    atual = None

    padrao = re.compile(r"^\s*(\d{1,2})\s+(\d{2}/\d{2})\s+(.+?)\s*$")

    for linha in linhas:
        linha = normalizar(linha)
        if not linha:
            continue

        m = padrao.match(linha)

        if m:
            if atual:
                registros.append(atual)

            aula_numero, data, tema = m.groups()
            dia, mes = data.split("/")

            atual = {
                "aula_numero": aula_numero,
                "data_aula": f"{ano}-{mes}-{dia}",
                "tema": tema,
                "objetivos": []
            }
        else:
            if atual:
                atual["objetivos"].append(linha)

    if atual:
        registros.append(atual)

    for r in registros:
        r["objetivos"] = normalizar(" ".join(r["objetivos"]))

    return registros

def processar(ano="2026"):
    con = sqlite3.connect(DB_PATH)
    cur = con.cursor()

    cur.execute("""
        CREATE TABLE IF NOT EXISTS aulas_cronograma (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            plano_id INTEGER,
            aula_numero TEXT,
            data_aula TEXT,
            tema TEXT,
            objetivos TEXT
        )
    """)

    cur.execute("DELETE FROM aulas_cronograma")

    planos = cur.execute("""
        SELECT id, conteudo
        FROM planos_aula
    """).fetchall()

    total = 0

    for plano_id, conteudo in planos:
        registros = extrair_linhas_cronograma(conteudo or "", ano)

        for r in registros:
            cur.execute("""
                INSERT INTO aulas_cronograma (
                    plano_id, aula_numero, data_aula, tema, objetivos
                )
                VALUES (?, ?, ?, ?, ?)
            """, (
                plano_id,
                r["aula_numero"],
                r["data_aula"],
                r["tema"],
                r["objetivos"]
            ))
            total += 1

    con.commit()
    con.close()

    print(f"Cronogramas extraídos: {total}")

if __name__ == "__main__":
    processar()
