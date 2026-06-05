import sqlite3
import re
import csv
from pathlib import Path

DB_PATH = "app/db/planos_aula.db"
OUTPUT_DIR = Path("outputs/curadoria")
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

def normalizar(texto):
    texto = (texto or "").lower()
    texto = re.sub(r"[^a-zà-ÿ0-9\s]", " ", texto)
    texto = re.sub(r"\s+", " ", texto).strip()
    return texto

def deduplicar(executar=False):
    con = sqlite3.connect(DB_PATH)
    cur = con.cursor()

    questoes = cur.execute("""
        SELECT id, enunciado, fonte, ano, prova, arquivo_origem
        FROM questoes
        WHERE enunciado IS NOT NULL
          AND TRIM(enunciado) <> ''
        ORDER BY id
    """).fetchall()

    vistos = {}
    duplicadas = []

    for q in questoes:
        qid, enunciado, fonte, ano, prova, arquivo_origem = q
        chave = normalizar(enunciado)

        if len(chave) < 40:
            continue

        if chave in vistos:
            duplicadas.append({
                "duplicada_id": qid,
                "mantida_id": vistos[chave]["id"],
                "fonte": fonte,
                "ano": ano,
                "prova": prova,
                "arquivo_origem": arquivo_origem,
                "trecho": enunciado[:180]
            })
        else:
            vistos[chave] = {
                "id": qid,
                "fonte": fonte,
                "ano": ano,
                "prova": prova,
                "arquivo_origem": arquivo_origem
            }

    relatorio = OUTPUT_DIR / "duplicidades_questoes.csv"

    with open(relatorio, "w", encoding="utf-8-sig", newline="") as f:
        campos = ["duplicada_id", "mantida_id", "fonte", "ano", "prova", "arquivo_origem", "trecho"]
        writer = csv.DictWriter(f, fieldnames=campos, delimiter=";")
        writer.writeheader()
        writer.writerows(duplicadas)

    print(f"Questões analisadas: {len(questoes)}")
    print(f"Duplicadas encontradas: {len(duplicadas)}")
    print(f"Relatório: {relatorio}")

    if executar and duplicadas:
        ids = [d["duplicada_id"] for d in duplicadas]
        cur.executemany("DELETE FROM questoes WHERE id = ?", [(i,) for i in ids])
        con.commit()
        print(f"Duplicadas removidas: {len(ids)}")
    else:
        print("Modo diagnóstico. Nada foi removido.")
        print("Para remover, execute com --executar")

    con.close()

if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument("--executar", action="store_true")
    args = parser.parse_args()

    deduplicar(executar=args.executar)
