import sqlite3

DB_PATH = "app/db/planos_aula.db"


def buscar_prova_por_hash(hash_arquivo):
    con = sqlite3.connect(DB_PATH)
    cur = con.cursor()

    row = cur.execute("""
        SELECT id, nome, ano, instituicao
        FROM provas
        WHERE hash_arquivo = ?
    """, (hash_arquivo,)).fetchone()

    con.close()
    return row


def criar_prova(nome, ano, instituicao, hash_arquivo, arquivo_origem):
    con = sqlite3.connect(DB_PATH)
    cur = con.cursor()

    cur.execute("""
        INSERT INTO provas (
            nome,
            ano,
            instituicao,
            hash_arquivo,
            arquivo_origem
        )
        VALUES (?, ?, ?, ?, ?)
    """, (
        nome,
        ano,
        instituicao,
        hash_arquivo,
        arquivo_origem
    ))

    prova_id = cur.lastrowid

    con.commit()
    con.close()

    return prova_id
