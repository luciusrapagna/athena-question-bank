import re
import sqlite3
from pathlib import Path

DB_PATH = Path("database/question_bank.db")

def conectar():
    return sqlite3.connect(DB_PATH)

def criar_tabela_questoes_extraidas():
    conn = conectar()
    cur = conn.cursor()

    cur.execute("""
    CREATE TABLE IF NOT EXISTS questoes_extraidas (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        documento_id INTEGER,
        numero_questao INTEGER,
        texto_questao TEXT,
        status_revisao TEXT DEFAULT 'pendente',
        data_extracao TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (documento_id) REFERENCES documentos(id)
    )
    """)

    conn.commit()
    conn.close()

def listar_documentos():
    conn = conectar()
    cur = conn.cursor()

    cur.execute("""
    SELECT id, prova, instituicao, ano, length(texto_bruto)
    FROM documentos
    ORDER BY id DESC
    """)

    docs = cur.fetchall()
    conn.close()
    return docs

def buscar_texto_documento(documento_id):
    conn = conectar()
    cur = conn.cursor()

    cur.execute("""
    SELECT texto_bruto
    FROM documentos
    WHERE id = ?
    """, (documento_id,))

    resultado = cur.fetchone()
    conn.close()

    return resultado[0] if resultado else ""

def extrair_questoes(texto):
    padrao = re.compile(
        r'(?im)^(?:quest[aã]o\s*)?(\d{1,3})[\.\-\)]\s+'
    )

    matches_validos = []

    for match in padrao.finditer(texto):
        numero = int(match.group(1))

        if 1 <= numero <= 200:
            matches_validos.append(match)

    questoes = []

    for i, match in enumerate(matches_validos):
        numero = int(match.group(1))
        inicio = match.start()
        fim = matches_validos[i + 1].start() if i + 1 < len(matches_validos) else len(texto)

        bloco = texto[inicio:fim].strip()

        if len(bloco) >= 80:
            questoes.append((numero, bloco))

    return questoes

def salvar_questoes(documento_id, questoes):
    conn = conectar()
    cur = conn.cursor()

    cur.execute("""
    DELETE FROM questoes_extraidas
    WHERE documento_id = ?
    """, (documento_id,))

    for numero, texto_questao in questoes:
        cur.execute("""
        INSERT INTO questoes_extraidas
        (documento_id, numero_questao, texto_questao)
        VALUES (?, ?, ?)
        """, (documento_id, numero, texto_questao))

    conn.commit()
    conn.close()

def main():
    criar_tabela_questoes_extraidas()

    documentos = listar_documentos()

    if not documentos:
        print("Nenhum documento importado encontrado.")
        return

    print("\nDOCUMENTOS IMPORTADOS")
    print("-" * 60)

    for doc in documentos:
        print(f"ID: {doc[0]} | Prova: {doc[1]} | Instituição: {doc[2]} | Ano: {doc[3]} | Caracteres: {doc[4]}")

    documento_id = input("\nDigite o ID do documento para extrair questões: ")

    try:
        documento_id = int(documento_id)
    except ValueError:
        print("ID inválido.")
        return

    texto = buscar_texto_documento(documento_id)

    if not texto:
        print("Documento sem texto bruto.")
        return

    questoes = extrair_questoes(texto)
    salvar_questoes(documento_id, questoes)

    print(f"\nExtração concluída. Questões encontradas: {len(questoes)}")

    for numero, bloco in sorted(questoes, key=lambda x: x[0])[:10]:
        print("\n" + "=" * 60)
        print(f"Questão {numero}")
        print("-" * 60)
        print(bloco[:500])

if __name__ == "__main__":
    main()
