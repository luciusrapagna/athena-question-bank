import sys
import sqlite3
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]

if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from src.reader.smart_pdf_reader import detectar_perfil, extrair_questoes_por_perfil

DB_PATH = ROOT / "database" / "question_bank.db"

def conectar():
    return sqlite3.connect(DB_PATH)

def criar_tabela():
    conn = conectar()
    cur = conn.cursor()

    cur.execute("""
    CREATE TABLE IF NOT EXISTS questoes_extraidas (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        documento_id INTEGER,
        numero_questao INTEGER,
        texto_questao TEXT,
        status_revisao TEXT DEFAULT 'pendente',
        area TEXT,
        subarea TEXT,
        tema TEXT,
        competencia TEXT,
        periodo TEXT,
        qualidade TEXT,
        data_extracao TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    """)

    conn.commit()
    conn.close()

def listar_documentos():
    conn = conectar()
    cur = conn.cursor()

    cur.execute("""
    SELECT id, prova, instituicao, ano, tipo, arquivo_origem, length(texto_bruto)
    FROM documentos
    ORDER BY id DESC
    """)

    docs = cur.fetchall()
    conn.close()
    return docs

def buscar_documento(documento_id):
    conn = conectar()
    cur = conn.cursor()

    cur.execute("""
    SELECT prova, tipo, arquivo_origem, texto_bruto
    FROM documentos
    WHERE id = ?
    """, (documento_id,))

    doc = cur.fetchone()
    conn.close()
    return doc

def salvar_questoes(documento_id, questoes):
    conn = conectar()
    cur = conn.cursor()

    cur.execute("DELETE FROM questoes_extraidas WHERE documento_id = ?", (documento_id,))

    for numero, bloco in questoes:
        cur.execute("""
        INSERT INTO questoes_extraidas
        (documento_id, numero_questao, texto_questao)
        VALUES (?, ?, ?)
        """, (documento_id, numero, bloco))

    conn.commit()
    conn.close()

def main():
    criar_tabela()

    docs = listar_documentos()

    if not docs:
        print("Nenhum documento importado.")
        return

    print("\nDOCUMENTOS IMPORTADOS")
    print("-" * 90)

    for d in docs[:30]:
        print(f"ID {d[0]} | {d[1]} | {d[2]} | {d[3]} | {d[4]} | caracteres: {d[6]}")

    documento_id = int(input("\nDigite o ID do documento: "))

    doc = buscar_documento(documento_id)

    if not doc:
        print("Documento não encontrado.")
        return

    prova, tipo, arquivo_origem, texto = doc

    perfil = detectar_perfil(texto, arquivo_origem or prova or tipo or "")
    questoes = extrair_questoes_por_perfil(texto, perfil)

    salvar_questoes(documento_id, questoes)

    print(f"\nPerfil detectado: {perfil}")
    print(f"Questões extraídas: {len(questoes)}")

    for numero, bloco in questoes[:10]:
        print("\n" + "=" * 60)
        print(f"QUESTÃO {numero}")
        print(bloco[:500])

if __name__ == "__main__":
    main()
