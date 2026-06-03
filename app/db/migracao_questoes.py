import sqlite3

DB_PATH = "app/db/planos_aula.db"

con = sqlite3.connect(DB_PATH)
cur = con.cursor()

cur.execute("""
CREATE TABLE IF NOT EXISTS questoes (

    id INTEGER PRIMARY KEY AUTOINCREMENT,

    instituicao TEXT,
    ano INTEGER,
    prova TEXT,

    grande_area TEXT,
    subarea TEXT,
    tema TEXT,

    enunciado TEXT,

    alternativa_a TEXT,
    alternativa_b TEXT,
    alternativa_c TEXT,
    alternativa_d TEXT,
    alternativa_e TEXT,

    gabarito TEXT,

    comentario TEXT,

    dificuldade TEXT,

    fonte TEXT,

    arquivo_origem TEXT,

    criado_em TIMESTAMP DEFAULT CURRENT_TIMESTAMP
)
""")

con.commit()
con.close()

print("Tabela questoes criada.")
