import sqlite3
import pandas as pd
import hashlib
from pathlib import Path

DB = Path("app/db/planos_aula.db")
OUT = Path("outputs/relatorios")
OUT.mkdir(parents=True, exist_ok=True)

def normalizar(txt):
    return " ".join(str(txt or "").lower().split())

def hash_texto(txt):
    return hashlib.md5(normalizar(txt).encode("utf-8")).hexdigest()

con = sqlite3.connect(DB)
df = pd.read_sql_query("""
    SELECT id, fonte, ano, area, assunto, enunciado
    FROM questoes
    WHERE enunciado IS NOT NULL
""", con)
con.close()

df["texto_norm"] = df["enunciado"].apply(normalizar)
df = df[df["texto_norm"].str.len() > 40].copy()
df["hash_enunciado"] = df["texto_norm"].apply(hash_texto)

duplicados = df[df.duplicated("hash_enunciado", keep=False)].copy()
duplicados = duplicados.sort_values(["hash_enunciado", "id"])

remover = duplicados[duplicados.duplicated("hash_enunciado", keep="first")].copy()

duplicados.to_csv(OUT / "duplicidades_exatas_hash.csv", index=False, encoding="utf-8-sig")
remover.to_csv(OUT / "candidatas_remocao_hash.csv", index=False, encoding="utf-8-sig")

print("Grupos com duplicidade exata:", duplicados["hash_enunciado"].nunique())
print("Questões em grupos duplicados:", len(duplicados))
print("Candidatas à remoção segura:", len(remover))
print(remover[["id", "fonte", "ano", "area", "assunto"]].head(30))
