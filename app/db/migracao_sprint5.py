import sqlite3

DB = "app/db/planos_aula.db"

con = sqlite3.connect(DB)
cur = con.cursor()

cur.execute("""
CREATE TABLE IF NOT EXISTS provas(
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    nome TEXT,
    ano INTEGER,
    instituicao TEXT,
    hash_arquivo TEXT UNIQUE,
    arquivo_origem TEXT,
    data_importacao TIMESTAMP DEFAULT CURRENT_TIMESTAMP
)
""")

try:
    cur.execute(
        "ALTER TABLE questoes ADD COLUMN prova_id INTEGER"
    )
except:
    pass

con.commit()
con.close()

print("Sprint 5 aplicada.")