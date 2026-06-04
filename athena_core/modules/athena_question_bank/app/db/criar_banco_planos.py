import sqlite3
from pathlib import Path

DB_PATH = Path("app/db/planos_aula.db")
DB_PATH.parent.mkdir(parents=True, exist_ok=True)

conn = sqlite3.connect(DB_PATH)
cursor = conn.cursor()

cursor.execute("""
CREATE TABLE IF NOT EXISTS planos_aula (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    disciplina TEXT,
    modulo TEXT,
    periodo TEXT,
    aula TEXT,
    data_aula TEXT,
    objetivos TEXT,
    conteudo TEXT,
    metodologia TEXT,
    referencia TEXT,
    arquivo_origem TEXT,
    criado_em TEXT DEFAULT CURRENT_TIMESTAMP
)
""")

cursor.execute("""
CREATE TABLE IF NOT EXISTS temas_plano (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    plano_id INTEGER,
    tema TEXT,
    FOREIGN KEY(plano_id) REFERENCES planos_aula(id)
)
""")

cursor.execute("""
CREATE TABLE IF NOT EXISTS compatibilidade_plano_questao (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    plano_id INTEGER,
    questao_id INTEGER,
    score REAL,
    FOREIGN KEY(plano_id) REFERENCES planos_aula(id)
)
""")

cursor.execute("""
CREATE TABLE IF NOT EXISTS provas_por_aula (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    plano_id INTEGER,
    data_geracao TEXT DEFAULT CURRENT_TIMESTAMP,
    total_questoes INTEGER,
    observacoes TEXT,
    FOREIGN KEY(plano_id) REFERENCES planos_aula(id)
)
""")

conn.commit()
conn.close()

print("Banco SQLite dos planos de aula criado com sucesso.")
