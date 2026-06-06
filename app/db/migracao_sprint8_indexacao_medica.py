import sqlite3

DB = "app/db/planos_aula.db"

NOVOS_CAMPOS = {
    "especialidade": "TEXT",
    "subtema_indexado": "TEXT",
    "competencia_enamed": "TEXT",
    "confianca_indexacao": "REAL DEFAULT 0"
}

def colunas(cur, tabela):
    cur.execute(f"PRAGMA table_info({tabela})")
    return [c[1] for c in cur.fetchall()]

def main():
    con = sqlite3.connect(DB)
    cur = con.cursor()

    cols = colunas(cur, "questoes")

    for campo, tipo in NOVOS_CAMPOS.items():
        if campo not in cols:
            cur.execute(f"ALTER TABLE questoes ADD COLUMN {campo} {tipo}")
            print(f"Campo criado: {campo}")

    cur.execute("""
        UPDATE questoes
        SET tema_indexado = NULL
        WHERE tema_indexado IS NULL
           OR TRIM(tema_indexado) = ''
           OR tema_indexado = 'Assunto não identificado'
    """)

    cur.execute("""
        UPDATE questoes
        SET assunto = NULL
        WHERE assunto IS NULL
           OR TRIM(assunto) = ''
           OR assunto = 'Assunto não identificado'
    """)

    con.commit()
    con.close()
    print("Migração Sprint 8 concluída.")

if __name__ == "__main__":
    main()
