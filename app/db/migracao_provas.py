import sqlite3

con = sqlite3.connect("app/db/planos_aula.db")
cur = con.cursor()

cur.execute("""
CREATE TABLE IF NOT EXISTS provas (

    id INTEGER PRIMARY KEY AUTOINCREMENT,

    nome TEXT,
    ano INTEGER,
    instituicao TEXT,

    hash_arquivo TEXT UNIQUE,

    arquivo_origem TEXT,

    data_importacao TIMESTAMP DEFAULT CURRENT_TIMESTAMP
)
""")

con.commit()
con.close()

print("Tabela provas criada.")
