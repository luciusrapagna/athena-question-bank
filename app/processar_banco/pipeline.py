from pathlib import Path
import sqlite3
import pandas as pd
import re

BASE = Path(__file__).resolve().parents[2]
DATA = BASE / "data"
DB = DATA / "athena_question_bank.db"

PROVAS = DATA / "entrada" / "provas"
PLANOS = DATA / "entrada" / "planos_aula"

BANCO_QUESTOES_CSV = DATA / "banco_questoes" / "banco_questoes.csv"
BANCO_PLANOS_CSV = DATA / "banco_planos" / "banco_planos_aula.csv"
BANCO_REL_CSV = DATA / "banco_relacionamentos" / "questoes_planos.csv"

AREAS = {
    "Clínica Médica": ["cardiologia", "pneumologia", "nefrologia", "endocrinologia", "gastro", "sepse", "diabetes", "hipertensão", "asma", "dpoc"],
    "Cirurgia": ["cirurgia", "trauma", "abdome agudo", "pré-operatório", "pós-operatório", "colecistite", "apendicite"],
    "Pediatria": ["criança", "pediatria", "lactente", "recém-nascido", "neonato", "vacina", "crescimento", "desenvolvimento"],
    "Ginecologia e Obstetrícia": ["gestante", "gravidez", "pré-natal", "parto", "puerpério", "ginecologia", "obstetrícia", "colo uterino"],
    "Saúde Coletiva": ["sus", "atenção primária", "vigilância", "epidemiologia", "prevenção", "promoção", "território", "notificação"],
}

def normalizar(txt):
    if txt is None:
        return ""
    return str(txt).replace("\n", " ").replace("\r", " ").strip()

def classificar_area(texto):
    t = normalizar(texto).lower()
    placar = {}
    for area, termos in AREAS.items():
        placar[area] = sum(1 for termo in termos if termo in t)
    melhor = max(placar, key=placar.get)
    return melhor if placar[melhor] > 0 else "Não classificada"

def assunto_simples(texto):
    t = normalizar(texto).lower()
    termos = [
        "sepse", "diabetes", "hipertensão", "asma", "dpoc", "dengue",
        "pré-natal", "parto", "vacinação", "sus", "trauma",
        "abdome agudo", "cardiologia", "pediatria", "epidemiologia"
    ]
    for termo in termos:
        if termo in t:
            return termo.title()
    return "Assunto não identificado"

def init_db():
    DATA.mkdir(parents=True, exist_ok=True)
    for p in [PROVAS, PLANOS, BANCO_QUESTOES_CSV.parent, BANCO_PLANOS_CSV.parent, BANCO_REL_CSV.parent]:
        p.mkdir(parents=True, exist_ok=True)

    con = sqlite3.connect(DB)
    cur = con.cursor()

    cur.execute("""
    CREATE TABLE IF NOT EXISTS questoes (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        origem TEXT,
        numero TEXT,
        enunciado TEXT,
        alternativa_a TEXT,
        alternativa_b TEXT,
        alternativa_c TEXT,
        alternativa_d TEXT,
        alternativa_e TEXT,
        gabarito TEXT,
        area TEXT,
        assunto TEXT,
        competencia TEXT,
        criado_em TEXT
    )
    """)

    cur.execute("""
    CREATE TABLE IF NOT EXISTS planos (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        origem TEXT,
        titulo TEXT,
        conteudo TEXT,
        temas TEXT,
        criado_em TEXT
    )
    """)

    cur.execute("""
    CREATE TABLE IF NOT EXISTS questoes_planos (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        questao_id INTEGER,
        plano_id INTEGER,
        score INTEGER,
        criterio TEXT,
        criado_em TEXT
    )
    """)

    con.commit()
    con.close()

def carregar_excel_questoes(arquivo):
    df = pd.read_excel(arquivo)
    cols = {c.lower().strip(): c for c in df.columns}

    registros = []
    for i, row in df.iterrows():
        enunciado = normalizar(row.get(cols.get("enunciado", ""), ""))
        if not enunciado:
            continue

        texto_total = " ".join([normalizar(v) for v in row.values])
        registros.append({
            "origem": Path(arquivo).name,
            "numero": normalizar(row.get(cols.get("numero", ""), i + 1)),
            "enunciado": enunciado,
            "alternativa_a": normalizar(row.get(cols.get("a", ""), "")),
            "alternativa_b": normalizar(row.get(cols.get("b", ""), "")),
            "alternativa_c": normalizar(row.get(cols.get("c", ""), "")),
            "alternativa_d": normalizar(row.get(cols.get("d", ""), "")),
            "alternativa_e": normalizar(row.get(cols.get("e", ""), "")),
            "gabarito": normalizar(row.get(cols.get("gabarito", ""), "")),
            "area": classificar_area(texto_total),
            "assunto": assunto_simples(texto_total),
            "competencia": "A definir",
            "criado_em": pd.Timestamp.now().isoformat(timespec="seconds"),
        })
    return registros

def carregar_texto_simples(arquivo):
    texto = Path(arquivo).read_text(encoding="utf-8", errors="ignore")
    blocos = re.split(r"\n\s*\n", texto)
    registros = []
    for idx, bloco in enumerate(blocos, start=1):
        b = normalizar(bloco)
        if len(b) < 40:
            continue
        registros.append({
            "origem": Path(arquivo).name,
            "numero": str(idx),
            "enunciado": b,
            "alternativa_a": "",
            "alternativa_b": "",
            "alternativa_c": "",
            "alternativa_d": "",
            "alternativa_e": "",
            "gabarito": "",
            "area": classificar_area(b),
            "assunto": assunto_simples(b),
            "competencia": "A definir",
            "criado_em": pd.Timestamp.now().isoformat(timespec="seconds"),
        })
    return registros

def processar_provas():
    init_db()
    arquivos = list(PROVAS.glob("*.xlsx")) + list(PROVAS.glob("*.xls")) + list(PROVAS.glob("*.txt")) + list(PROVAS.glob("*.md"))
    todos = []

    for arq in arquivos:
        if arq.suffix.lower() in [".xlsx", ".xls"]:
            todos.extend(carregar_excel_questoes(arq))
        elif arq.suffix.lower() in [".txt", ".md"]:
            todos.extend(carregar_texto_simples(arq))

    if not todos:
        return 0

    con = sqlite3.connect(DB)
    pd.DataFrame(todos).to_sql("questoes", con, if_exists="append", index=False)
    con.close()

    df = pd.DataFrame(todos)
    if BANCO_QUESTOES_CSV.exists():
        antigo = pd.read_csv(BANCO_QUESTOES_CSV)
        df = pd.concat([antigo, df], ignore_index=True)
    df.to_csv(BANCO_QUESTOES_CSV, index=False, encoding="utf-8-sig")
    return len(todos)

def processar_planos():
    init_db()
    arquivos = list(PLANOS.glob("*.txt")) + list(PLANOS.glob("*.md"))
    registros = []

    for arq in arquivos:
        texto = Path(arq).read_text(encoding="utf-8", errors="ignore")
        linhas = [normalizar(l) for l in texto.splitlines() if normalizar(l)]
        titulo = linhas[0] if linhas else arq.stem
        temas = "; ".join(linhas[1:8]) if len(linhas) > 1 else ""
        registros.append({
            "origem": arq.name,
            "titulo": titulo,
            "conteudo": normalizar(texto),
            "temas": temas,
            "criado_em": pd.Timestamp.now().isoformat(timespec="seconds"),
        })

    if not registros:
        return 0

    con = sqlite3.connect(DB)
    pd.DataFrame(registros).to_sql("planos", con, if_exists="append", index=False)
    con.close()

    df = pd.DataFrame(registros)
    if BANCO_PLANOS_CSV.exists():
        antigo = pd.read_csv(BANCO_PLANOS_CSV)
        df = pd.concat([antigo, df], ignore_index=True)
    df.to_csv(BANCO_PLANOS_CSV, index=False, encoding="utf-8-sig")
    return len(registros)

def relacionar_questoes_planos():
    init_db()
    con = sqlite3.connect(DB)
    q = pd.read_sql_query("SELECT id, enunciado, area, assunto FROM questoes", con)
    p = pd.read_sql_query("SELECT id, titulo, conteudo, temas FROM planos", con)

    rels = []
    for _, questao in q.iterrows():
        texto_q = f"{questao.get('enunciado','')} {questao.get('area','')} {questao.get('assunto','')}".lower()
        palavras_q = set(re.findall(r"\w+", texto_q))
        for _, plano in p.iterrows():
            texto_p = f"{plano.get('titulo','')} {plano.get('conteudo','')} {plano.get('temas','')}".lower()
            palavras_p = set(re.findall(r"\w+", texto_p))
            comuns = palavras_q.intersection(palavras_p)
            score = len([w for w in comuns if len(w) > 4])
            if score >= 2:
                rels.append({
                    "questao_id": int(questao["id"]),
                    "plano_id": int(plano["id"]),
                    "score": int(score),
                    "criterio": "sobreposição de termos",
                    "criado_em": pd.Timestamp.now().isoformat(timespec="seconds"),
                })

    if rels:
        pd.DataFrame(rels).to_sql("questoes_planos", con, if_exists="append", index=False)
        pd.DataFrame(rels).to_csv(BANCO_REL_CSV, index=False, encoding="utf-8-sig")

    con.close()
    return len(rels)

def processar_tudo():
    n_q = processar_provas()
    n_p = processar_planos()
    n_r = relacionar_questoes_planos()
    return {
        "questoes_processadas": n_q,
        "planos_processados": n_p,
        "relacionamentos_criados": n_r,
        "banco": str(DB),
    }

if __name__ == "__main__":
    print(processar_tudo())
