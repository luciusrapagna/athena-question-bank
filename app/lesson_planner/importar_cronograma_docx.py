import argparse
import sqlite3
from pathlib import Path
from docx import Document

DB_PATH = "app/db/planos_aula.db"

def limpar(texto):
    return " ".join((texto or "").replace("\n", " ").split()).strip()

def importar_docx(arquivo, plano_id=0, ano="2026"):
    arquivo = Path(arquivo)

    if not arquivo.exists():
        print(f"Arquivo não encontrado: {arquivo}")
        return

    doc = Document(str(arquivo))

    con = sqlite3.connect(DB_PATH)
    cur = con.cursor()

    cur.execute("""
        CREATE TABLE IF NOT EXISTS aulas_cronograma (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            plano_id INTEGER,
            aula_numero TEXT,
            data_aula TEXT,
            tema TEXT,
            objetivos TEXT,
            atividades TEXT,
            preparacao_previa TEXT,
            recursos TEXT,
            arquivo_origem TEXT
        )
    """)

    inseridas = 0

    for tabela in doc.tables:
        if len(tabela.rows) < 2:
            continue

        cabecalho = [limpar(c.text).lower() for c in tabela.rows[0].cells]

        if not ("aula" in cabecalho and "data" in cabecalho and "tema" in cabecalho and "objetivos" in cabecalho):
            continue

        for row in tabela.rows[1:]:
            cells = [limpar(c.text) for c in row.cells]

            if len(cells) < 4:
                continue

            aula = cells[0]
            data = cells[1]
            tema = cells[2]
            objetivos = cells[3]
            atividades = cells[4] if len(cells) > 4 else ""
            preparacao = cells[5] if len(cells) > 5 else ""
            recursos = cells[6] if len(cells) > 6 else ""

            if not aula or not data or not tema:
                continue

            if "/" in data:
                partes = data.split("/")
                if len(partes) == 2:
                    dia, mes = partes
                    data = f"{ano}-{mes.zfill(2)}-{dia.zfill(2)}"

            cur.execute("""
                INSERT INTO aulas_cronograma (
                    plano_id, aula_numero, data_aula, tema, objetivos,
                    atividades, preparacao_previa, recursos, arquivo_origem
                )
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                plano_id, aula, data, tema, objetivos,
                atividades, preparacao, recursos, str(arquivo)
            ))

            inseridas += 1

    con.commit()
    con.close()

    print(f"Arquivo importado: {arquivo}")
    print(f"Aulas inseridas: {inseridas}")

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("arquivo")
    parser.add_argument("--plano-id", type=int, default=0)
    parser.add_argument("--ano", default="2026")
    args = parser.parse_args()

    importar_docx(args.arquivo, plano_id=args.plano_id, ano=args.ano)

if __name__ == "__main__":
    main()
