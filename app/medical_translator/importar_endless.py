import json
import sqlite3

from app.medical_translator.tradutor_icd10 import classificar_icd10, classificar_por_nome, classificar_por_dicionario

DB = "app/db/athena_medical_translator.db"

with open(
    "data/dicionarios/DiseasesOutput.json",
    encoding="utf-8"
) as f:
    diseases = json.load(f)

con = sqlite3.connect(DB)
cur = con.cursor()

total = 0

for d in diseases:

    icd10 = d.get("ICD10", "")
    cls = classificar_icd10(icd10)

    if not cls:
        cls = classificar_por_nome(d.get("text",""))

    if not cls:
        cls = classificar_por_dicionario(d.get("text",""))

    if cls:
        area = cls["area"]
        especialidade = cls["especialidade"]
        competencia = cls["competencia"]
        habilidade = cls["habilidade"]
    else:
        area = ""
        especialidade = ""
        competencia = ""
        habilidade = ""

    cur.execute("""
    INSERT INTO medical_translation (
        termo_en,
        termo_pt,
        icd10,
        categoria,
        especialidade,
        area,
        competencia_enamed,
        habilidade_enamed
    )
    VALUES (?,?,?,?,?,?,?,?)
    """, (
        d.get("text",""),
        "",
        icd10,
        d.get("category",""),
        especialidade,
        area,
        competencia,
        habilidade
    ))

    total += 1

con.commit()
con.close()

print(f"{total} doenças importadas.")
