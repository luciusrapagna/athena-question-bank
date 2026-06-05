import argparse
import sqlite3
import re
import csv
from pathlib import Path
from difflib import SequenceMatcher
from docx import Document

DB_PATH = "app/db/planos_aula.db"
OUTPUT_DIR = Path("outputs/simulados_por_aula")
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

AREAS = [
    "Clínica Médica",
    "Cirurgia",
    "Pediatria",
    "Ginecologia e Obstetrícia",
    "Saúde Coletiva",
]

def normalizar(texto):
    texto = (texto or "").lower()
    texto = re.sub(r"[^a-zà-ÿ0-9\s]", " ", texto)
    return re.sub(r"\s+", " ", texto).strip()

def score_texto(a, b):
    a = normalizar(a)
    b = normalizar(b)
    if not a or not b:
        return 0
    termos_a = set(a.split())
    termos_b = set(b.split())
    jaccard = len(termos_a & termos_b) / max(len(termos_a | termos_b), 1)
    seq = SequenceMatcher(None, a, b).ratio()
    return round((0.75 * jaccard) + (0.25 * seq), 4)

def buscar_aula(cur, data=None, termo=None):
    sql = """
        SELECT id, plano_id, aula_numero, data_aula, tema, objetivos
        FROM aulas_cronograma
        WHERE 1=1
    """
    params = []

    if data:
        sql += " AND data_aula = ?"
        params.append(data)

    if termo:
        sql += " AND (LOWER(tema) LIKE ? OR LOWER(objetivos) LIKE ?)"
        busca = f"%{termo.lower()}%"
        params.extend([busca, busca])

    sql += " ORDER BY data_aula, plano_id, CAST(aula_numero AS INTEGER) LIMIT 1"
    return cur.execute(sql, params).fetchone()

def buscar_questoes_por_area(cur, area):
    return cur.execute("""
        SELECT id, grande_area, tema, enunciado,
               alternativa_a, alternativa_b, alternativa_c, alternativa_d, alternativa_e,
               gabarito, fonte, ano, prova, instituicao
        FROM questoes
        WHERE grande_area = ?
          AND enunciado IS NOT NULL
          AND TRIM(enunciado) <> ''
    """, (area,)).fetchall()

def ranquear(aula, questoes):
    _, _, _, _, tema_aula, objetivos = aula
    texto_aula = f"{tema_aula or ''} {objetivos or ''}"

    resultado = []
    for q in questoes:
        texto_q = " ".join(str(x or "") for x in q[1:9])
        score = score_texto(texto_aula, texto_q)
        if score > 0:
            resultado.append((score, q))

    resultado.sort(key=lambda x: x[0], reverse=True)
    return resultado

def exportar_word(aula, selecionadas, nome):
    aula_id, plano_id, aula_numero, data_aula, tema, objetivos = aula

    doc = Document()
    doc.add_heading("ATHENA QUESTION BANK", level=1)
    doc.add_heading("Simulado por Aula", level=2)

    doc.add_paragraph(f"Aula: {aula_numero}")
    doc.add_paragraph(f"Data: {data_aula}")
    doc.add_paragraph(f"Tema: {tema}")
    doc.add_paragraph(f"Objetivos: {objetivos}")

    total = sum(len(v) for v in selecionadas.values())
    doc.add_paragraph(f"Total de questões: {total}")

    n = 1
    for area, itens in selecionadas.items():
        doc.add_heading(area, level=2)

        for score, q in itens:
            qid, grande_area, tema_q, enunciado, a, b, c, d, e, gabarito, fonte, ano, prova, instituicao = q

            doc.add_heading(f"Questão {n} — ID {qid}", level=3)
            doc.add_paragraph(f"Compatibilidade: {score}")
            doc.add_paragraph(f"Área: {grande_area or ''} | Tema: {tema_q or ''}")
            doc.add_paragraph(f"Fonte: {fonte or ''} | Prova: {prova or ''} | Ano: {ano or ''} | Instituição: {instituicao or ''}")
            doc.add_paragraph(enunciado or "")

            for letra, alt in [("A", a), ("B", b), ("C", c), ("D", d), ("E", e)]:
                if alt:
                    doc.add_paragraph(f"{letra}) {alt}")

            n += 1

    caminho = OUTPUT_DIR / nome
    doc.save(caminho)
    return caminho

def exportar_csv(aula, selecionadas, nome):
    caminho = OUTPUT_DIR / nome

    with open(caminho, "w", encoding="utf-8-sig", newline="") as f:
        writer = csv.writer(f, delimiter=";")
        writer.writerow([
            "numero", "aula_numero", "data_aula", "tema_aula",
            "questao_id", "score", "grande_area", "tema_questao",
            "fonte", "prova", "ano", "instituicao", "gabarito"
        ])

        n = 1
        for area, itens in selecionadas.items():
            for score, q in itens:
                qid, grande_area, tema_q, enunciado, a, b, c, d, e, gabarito, fonte, ano, prova, instituicao = q
                writer.writerow([
                    n, aula[2], aula[3], aula[4],
                    qid, score, grande_area, tema_q,
                    fonte, prova, ano, instituicao, gabarito
                ])
                n += 1

    return caminho

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--data", default=None)
    parser.add_argument("--termo", default=None)
    parser.add_argument("--clinica", type=int, default=0)
    parser.add_argument("--cirurgia", type=int, default=0)
    parser.add_argument("--pediatria", type=int, default=0)
    parser.add_argument("--go", type=int, default=0)
    parser.add_argument("--saude-coletiva", type=int, default=0)
    args = parser.parse_args()

    quotas = {
        "Clínica Médica": args.clinica,
        "Cirurgia": args.cirurgia,
        "Pediatria": args.pediatria,
        "Ginecologia e Obstetrícia": args.go,
        "Saúde Coletiva": args.saude_coletiva,
    }

    quotas = {area: qtd for area, qtd in quotas.items() if qtd > 0}

    if not quotas:
        print("Informe pelo menos uma quantidade por área.")
        return

    con = sqlite3.connect(DB_PATH)
    cur = con.cursor()

    aula = buscar_aula(cur, data=args.data, termo=args.termo)

    if not aula:
        print("Nenhuma aula encontrada.")
        con.close()
        return

    selecionadas = {}

    print(f"\nAula encontrada: {aula[2]} | {aula[3]} | {aula[4]}")
    print("Objetivos:", aula[5])

    for area, qtd in quotas.items():
        questoes = buscar_questoes_por_area(cur, area)
        ranqueadas = ranquear(aula, questoes)
        selecionadas[area] = ranqueadas[:qtd]

        print(f"\n{area}: solicitadas {qtd}, selecionadas {len(selecionadas[area])}")
        for score, q in selecionadas[area]:
            print(f"  Q{q[0]} | score {score} | {q[2]} | Fonte: {q[10]} | Ano: {q[11]}")

    sufixo = args.data or normalizar(args.termo or "aula").replace(" ", "_")
    word = exportar_word(aula, selecionadas, f"simulado_aula_{sufixo}.docx")
    csv_path = exportar_csv(aula, selecionadas, f"simulado_aula_{sufixo}.csv")

    print(f"\nWord: {word}")
    print(f"CSV: {csv_path}")

    con.close()

if __name__ == "__main__":
    main()
