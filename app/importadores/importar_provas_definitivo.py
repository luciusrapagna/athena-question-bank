import re, hashlib, sqlite3
from pathlib import Path
from datetime import datetime

try:
    import fitz
except ImportError:
    raise SystemExit("Instale: ./venv/bin/pip install pymupdf")

DB = Path("app/db/planos_aula.db")
PASTA = Path("data/entrada/provas")
LOG = Path("outputs/importacao/importacao_provas_definitiva.log")
LOG.parent.mkdir(parents=True, exist_ok=True)

TIPOS = ["REVALIDA", "ENADE", "ENAMED", "ENARE"]

def limpar(txt):
    return re.sub(r"\s+", " ", txt or "").strip()

def detectar_tipo(nome):
    n = nome.lower()
    if "revalida" in n: return "REVALIDA"
    if "enade" in n: return "ENADE"
    if "enamed" in n: return "ENAMED"
    if "enare" in n or "erane" in n: return "ENARE"
    return None

def detectar_ano(nome):
    m = re.search(r"(20\d{2})", nome)
    return m.group(1) if m else "ANO_NAO_IDENTIFICADO"

def hash_q(tipo, prova, numero, enunciado):
    base = f"{tipo}|{prova}|{numero}|{limpar(enunciado).lower()}"
    return hashlib.sha256(base.encode("utf-8")).hexdigest()

def extrair_texto(pdf):
    doc = fitz.open(pdf)
    return "\n".join(page.get_text("text") for page in doc)

def extrair_questoes(texto):
    texto = texto.replace("\r", "\n")
    padrao = re.compile(
        r"(?im)(?:^|\n)\s*(?:quest[aã]o\s*)?(\d{1,3})[\.\)\-–]?\s+(.*?)(?=(?:\n\s*(?:quest[aã]o\s*)?\d{1,3}[\.\)\-–]?\s+)|\Z)",
        re.S
    )

    itens = []
    for num, bloco in padrao.findall(texto):
        n = int(num)
        if not 1 <= n <= 150:
            continue

        bloco = bloco.strip()
        if len(bloco) < 60:
            continue

        alts = {}
        for letra in "ABCDE":
            m = re.search(
                rf"(?is)(?:^|\n|\s)({letra})[\)\.\-–]\s+(.*?)(?=(?:\s+[A-E][\)\.\-–]\s+)|\Z)",
                bloco
            )
            if m:
                alts[letra.lower()] = limpar(m.group(2))

        enunciado = bloco
        m_alt = re.search(r"(?is)(?:^|\n|\s)A[\)\.\-–]\s+", bloco)
        if m_alt:
            enunciado = bloco[:m_alt.start()]

        itens.append({
            "numero": n,
            "enunciado": limpar(enunciado),
            "alternativa_a": alts.get("a", ""),
            "alternativa_b": alts.get("b", ""),
            "alternativa_c": alts.get("c", ""),
            "alternativa_d": alts.get("d", ""),
            "alternativa_e": alts.get("e", ""),
        })

    unicos = {}
    for q in itens:
        unicos[q["numero"]] = q

    return [unicos[k] for k in sorted(unicos)]

def garantir_colunas(cur):
    cur.execute("""
    CREATE TABLE IF NOT EXISTS importacoes_questoes (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        arquivo TEXT,
        prova TEXT,
        fonte TEXT,
        total_extraidas INTEGER,
        total_inseridas INTEGER,
        data_importacao TEXT,
        observacao TEXT
    )
    """)

    cols = [c[1] for c in cur.execute("PRAGMA table_info(questoes)").fetchall()]
    obrigatorias = {
        "hash_questao": "TEXT",
        "fonte": "TEXT",
        "prova": "TEXT",
        "numero": "INTEGER",
        "enunciado": "TEXT",
        "alternativa_a": "TEXT",
        "alternativa_b": "TEXT",
        "alternativa_c": "TEXT",
        "alternativa_d": "TEXT",
        "alternativa_e": "TEXT",
        "assunto": "TEXT",
        "tema_indexado": "TEXT",
        "grande_area": "TEXT",
        "area": "TEXT",
    }

    for col, tipo in obrigatorias.items():
        if col not in cols:
            cur.execute(f"ALTER TABLE questoes ADD COLUMN {col} {tipo}")

def importar():
    con = sqlite3.connect(DB)
    cur = con.cursor()
    garantir_colunas(cur)

    pdfs = []
    for p in PASTA.glob("*.pdf"):
        tipo = detectar_tipo(p.name)
        if tipo:
            pdfs.append((p, tipo))

    total_extraidas = 0
    total_inseridas = 0

    with LOG.open("a", encoding="utf-8") as log:
        log.write(f"\n\n=== IMPORTAÇÃO UNIVERSAL {datetime.now()} ===\n")

        for pdf, tipo in sorted(pdfs):
            ano = detectar_ano(pdf.name)
            prova = f"{tipo} {ano}"

            texto = extrair_texto(pdf)
            questoes = extrair_questoes(texto)

            inseridas = 0

            for q in questoes:
                h = hash_q(tipo, prova, q["numero"], q["enunciado"])

                existe = cur.execute(
                    "SELECT COUNT(*) FROM questoes WHERE hash_questao=?",
                    (h,)
                ).fetchone()[0]

                if existe:
                    continue

                cur.execute("""
                    INSERT INTO questoes
                    (hash_questao, fonte, prova, numero, enunciado,
                     alternativa_a, alternativa_b, alternativa_c, alternativa_d, alternativa_e,
                     assunto, tema_indexado, grande_area, area)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    h,
                    tipo,
                    prova,
                    q["numero"],
                    q["enunciado"],
                    q["alternativa_a"],
                    q["alternativa_b"],
                    q["alternativa_c"],
                    q["alternativa_d"],
                    q["alternativa_e"],
                    "",
                    "",
                    "",
                    ""
                ))

                inseridas += 1

            cur.execute("""
                INSERT INTO importacoes_questoes
                (arquivo, prova, fonte, total_extraidas, total_inseridas, data_importacao, observacao)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (
                str(pdf),
                prova,
                tipo,
                len(questoes),
                inseridas,
                datetime.now().isoformat(timespec="seconds"),
                "Importação universal definitiva ENADE/ENAMED/ENARE/REVALIDA"
            ))

            total_extraidas += len(questoes)
            total_inseridas += inseridas

            msg = f"{pdf.name}: {prova} | extraídas={len(questoes)} | inseridas={inseridas}"
            print(msg)
            log.write(msg + "\n")

    con.commit()
    con.close()

    print("\nRESUMO FINAL")
    print("Total extraídas:", total_extraidas)
    print("Total inseridas:", total_inseridas)
    print("Log:", LOG)

if __name__ == "__main__":
    importar()
