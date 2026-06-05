from pathlib import Path
import sqlite3
import pandas as pd
import re

BASE = Path(__file__).resolve().parents[2]
DATA = BASE / "data"
DB = DATA / "athena_question_bank.db"
OUT = BASE / "outputs" / "relatorios"
OUT.mkdir(parents=True, exist_ok=True)

def normalizar(texto):
    if texto is None:
        return ""
    return re.sub(r"\s+", " ", str(texto)).strip().lower()

def carregar_questoes():
    if not DB.exists():
        return pd.DataFrame()
    con = sqlite3.connect(DB)
    try:
        df = pd.read_sql_query("SELECT * FROM questoes", con)
    except Exception:
        df = pd.DataFrame()
    con.close()
    return df.fillna("")

def diagnosticar_banco():
    df = carregar_questoes()

    if df.empty:
        resumo = pd.DataFrame([{
            "indicador": "Questões totais",
            "quantidade": 0
        }])
        return resumo, pd.DataFrame(), ""

    for col in ["area", "assunto", "competencia", "enunciado"]:
        if col not in df.columns:
            df[col] = ""

    df["_enunciado_norm"] = df["enunciado"].apply(normalizar)

    sem_area = df[df["area"].astype(str).str.strip().isin(["", "Não classificada", "nan"])]
    sem_assunto = df[df["assunto"].astype(str).str.strip().isin(["", "Assunto não identificado", "nan"])]
    sem_competencia = df[df["competencia"].astype(str).str.strip().isin(["", "A definir", "nan"])]

    incompletas = df[
        (df["enunciado"].astype(str).str.len() < 40) |
        (df["_enunciado_norm"] == "")
    ]

    duplicadas = df[df.duplicated("_enunciado_norm", keep=False) & (df["_enunciado_norm"] != "")]

    resumo = pd.DataFrame([
        {"indicador": "Questões totais", "quantidade": int(len(df))},
        {"indicador": "Sem área", "quantidade": int(len(sem_area))},
        {"indicador": "Sem assunto", "quantidade": int(len(sem_assunto))},
        {"indicador": "Sem competência", "quantidade": int(len(sem_competencia))},
        {"indicador": "Possíveis duplicadas", "quantidade": int(len(duplicadas))},
        {"indicador": "Incompletas", "quantidade": int(len(incompletas))},
    ])

    problemas = []

    def adicionar(sub, problema):
        if sub.empty:
            return
        tmp = sub.copy()
        tmp["problema"] = problema
        problemas.append(tmp)

    adicionar(sem_area, "Sem área")
    adicionar(sem_assunto, "Sem assunto")
    adicionar(sem_competencia, "Sem competência")
    adicionar(duplicadas, "Possível duplicada")
    adicionar(incompletas, "Incompleta")

    df_problemas = pd.concat(problemas, ignore_index=True) if problemas else pd.DataFrame()

    caminho = OUT / "curadoria_banco_questoes.csv"
    df_problemas.drop(columns=["_enunciado_norm"], errors="ignore").to_csv(caminho, index=False, encoding="utf-8-sig")

    return resumo, df_problemas.drop(columns=["_enunciado_norm"], errors="ignore"), str(caminho)

if __name__ == "__main__":
    resumo, problemas, caminho = diagnosticar_banco()
    print(resumo)
    print(f"Problemas encontrados: {len(problemas)}")
    print(f"Relatório: {caminho}")

def corrigir_automaticamente():
    """
    Correções seguras:
    - competência vazia ou 'A definir' vira 'Competência a definir';
    - área vazia tenta reclassificar usando o classificador do pipeline;
    - assunto vazio tenta inferir usando o classificador simples do pipeline.
    """
    from app.processar_banco.pipeline import classificar_area, assunto_simples

    if not DB.exists():
        return {"corrigidas": 0, "mensagem": "Banco não encontrado."}

    con = sqlite3.connect(DB)
    df = pd.read_sql_query("SELECT * FROM questoes", con).fillna("")

    if df.empty:
        con.close()
        return {"corrigidas": 0, "mensagem": "Banco vazio."}

    corrigidas = 0

    for _, row in df.iterrows():
        qid = row.get("id")
        enunciado = str(row.get("enunciado", ""))
        area = str(row.get("area", "")).strip()
        assunto = str(row.get("assunto", "")).strip()
        competencia = str(row.get("competencia", "")).strip()

        nova_area = area
        novo_assunto = assunto
        nova_competencia = competencia

        if area in ["", "Não classificada", "nan"]:
            nova_area = classificar_area(enunciado)

        if assunto in ["", "Assunto não identificado", "nan"]:
            novo_assunto = assunto_simples(enunciado)

        if competencia in ["", "A definir", "nan"]:
            nova_competencia = "Competência a definir"

        if (nova_area != area) or (novo_assunto != assunto) or (nova_competencia != competencia):
            con.execute(
                "UPDATE questoes SET area=?, assunto=?, competencia=? WHERE id=?",
                (nova_area, novo_assunto, nova_competencia, qid)
            )
            corrigidas += 1

    con.commit()
    con.close()

    return {
        "corrigidas": corrigidas,
        "mensagem": "Correção automática concluída com backup prévio recomendado."
    }
