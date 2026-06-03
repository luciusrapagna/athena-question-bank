import sqlite3
from pathlib import Path

DB_PATH = Path("database/question_bank.db")

def conectar():
    DB_PATH.parent.mkdir(exist_ok=True)
    return sqlite3.connect(DB_PATH)

def criar_tabelas():
    conn = conectar()
    cur = conn.cursor()

    cur.execute("""
    CREATE TABLE IF NOT EXISTS documentos (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        tipo TEXT,
        prova TEXT,
        instituicao TEXT,
        ano INTEGER,
        arquivo_origem TEXT,
        texto_bruto TEXT,
        data_importacao TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    """)

    conn.commit()
    conn.close()

def salvar_documento(tipo, prova, instituicao, ano, arquivo_origem, texto_bruto):
    conn = conectar()
    cur = conn.cursor()

    cur.execute("""
    INSERT INTO documentos
    (tipo, prova, instituicao, ano, arquivo_origem, texto_bruto)
    VALUES (?, ?, ?, ?, ?, ?)
    """, (tipo, prova, instituicao, ano, arquivo_origem, texto_bruto))

    conn.commit()
    conn.close()
