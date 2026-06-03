import sqlite3
from pathlib import Path

Path("database").mkdir(exist_ok=True)

conn = sqlite3.connect("database/question_bank.db")

cursor = conn.cursor()

cursor.execute("""
CREATE TABLE IF NOT EXISTS questoes (
    id INTEGER PRIMARY KEY AUTOINCREMENT,

    texto TEXT NOT NULL,
    alternativas TEXT,
    gabarito TEXT,

    area TEXT,
    subarea TEXT,
    tema TEXT,

    competencia TEXT,
    habilidade TEXT,

    dificuldade TEXT,

    prova TEXT,
    instituicao TEXT,
    ano INTEGER,

    arquivo_origem TEXT,

    data_importacao TIMESTAMP DEFAULT CURRENT_TIMESTAMP
)
""")

conn.commit()
conn.close()

print("Banco Athena Question Bank criado com sucesso.")
