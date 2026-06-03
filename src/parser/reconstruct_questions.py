import sys
import re
import sqlite3
from pathlib import Path
import fitz

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

DB_PATH = ROOT / "database" / "question_bank.db"

def conectar():
    return sqlite3.connect(DB_PATH)

def limpar_texto(txt):
    txt = txt.replace("￾", "-").replace("\r", "")
    txt = re.sub(r"[ \t]+", " ", txt)
    return txt.strip()

def bloco_util(page, x0, y0, x1, y1, txt):
    largura = page.rect.width
    altura = page.rect.height
    t = txt.strip()

    if not t:
        return False

    # remove cabeçalho e rodapé
    if y0 < altura * 0.06:
        return False
    if y1 > altura * 0.94:
        return False

    # remove margens extremas
    if x1 < largura * 0.04 or x0 > largura * 0.96:
        return False

    lixo = [
        "ÁREA LIVRE",
        "RASCUNHO",
        "LEIA COM ATENÇÃO",
        "INSTRUÇÕES",
        "CADERNO",
        "CARTÃO-RESPOSTA",
        "Núcleo Mineiro",
        "Teste de Progresso",
        "Medway - ENARE",
        "Páginas",
        "ENADE -",
        "MEDICINA"
    ]

    if any(p.upper() in t.upper() for p in lixo):
        return False

    # remove numeração isolada de página
    if re.match(r"^\d{1,3}$", t):
        return False

    return True

def extrair_blocos_pdf(pdf_path):
    doc = fitz.open(pdf_path)
    blocos = []

    for pagina, page in enumerate(doc, start=1):
        largura = page.rect.width

        for b in page.get_text("blocks"):
            x0, y0, x1, y1, txt = b[:5]
            txt = limpar_texto(txt)

            if not bloco_util(page, x0, y0, x1, y1, txt):
                continue

            coluna = 1 if x0 < largura / 2 else 2

            blocos.append({
                "pagina": pagina,
                "coluna": coluna,
                "x0": x0,
                "y0": y0,
                "texto": txt
            })

    return sorted(blocos, key=lambda b: (b["pagina"], b["coluna"], b["y0"], b["x0"]))

def eh_inicio_questao(txt):
    return re.match(r"^\s*(QUESTÃO\s*)?\d{1,3}[\.\)]?\s+", txt, re.I)

def numero_questao(txt):
    m = re.match(r"^\s*(QUESTÃO\s*)?(\d{1,3})[\.\)]?\s+", txt, re.I)
    if not m:
        return None
    n = int(m.group(2))
    return n if 1 <= n <= 200 else None

def normalizar_alternativas(txt):
    txt = re.sub(r"(?m)^([A-E])\.\s+", r"(\1) ", txt)
    txt = re.sub(r"(?m)^([A-E])\)\s+", r"(\1) ", txt)
    txt = re.sub(r"(?m)^\(([A-E])\)\s*", r"(\1) ", txt)
    return txt

def qualidade(txt):
    txt = normalizar_alternativas(txt)
    tem = [(f"({l})" in txt) for l in "ABCD"]
    duplicada = any(txt.count(f"({l})") > 1 for l in "ABCD")

    if all(tem) and not duplicada and len(txt) > 120:
        return "valida"

    if tem[0] and tem[1] and tem[2] and not duplicada and len(txt) > 120:
        return "valida_parcial"

    return "revisar_manual"

def reconstruir(blocos):
    questoes = {}
    atual = None

    for b in blocos:
        txt = b["texto"]

        if eh_inicio_questao(txt):
            n = numero_questao(txt)
            if n:
                atual = n
                questoes.setdefault(n, [])
                questoes[n].append(txt)
                continue

        if atual:
            questoes[atual].append(txt)

    saida = []
    for n in sorted(questoes):
        txt = "\n".join(questoes[n])
        txt = normalizar_alternativas(txt)
        txt = re.sub(r"\n{3,}", "\n\n", txt).strip()
        saida.append((n, txt, qualidade(txt)))

    return saida

def listar_documentos():
    conn = conectar()
    cur = conn.cursor()
    cur.execute("""
    SELECT id, prova, instituicao, ano, tipo, arquivo_origem
    FROM documentos
    ORDER BY id DESC
    """)
    rows = cur.fetchall()
    conn.close()
    return rows

def salvar(documento_id, questoes):
    conn = conectar()
    cur = conn.cursor()

    cur.execute("DELETE FROM questoes_extraidas WHERE documento_id=?", (documento_id,))

    for n, txt, q in questoes:
        cur.execute("""
        INSERT INTO questoes_extraidas
        (documento_id, numero_questao, texto_questao, qualidade)
        VALUES (?, ?, ?, ?)
        """, (documento_id, n, txt, q))

    conn.commit()
    conn.close()

def main():
    docs = listar_documentos()

    for d in docs:
        print(f"ID {d[0]} | {d[1]} | {d[2]} | {d[3]} | {d[4]} | {d[5]}")

    documento_id = int(input("\nDigite o ID do documento: "))

    doc = [d for d in docs if d[0] == documento_id][0]
    pdf_path = doc[5]

    if not Path(pdf_path).exists():
        print(f"PDF não encontrado: {pdf_path}")
        return

    blocos = extrair_blocos_pdf(pdf_path)
    questoes = reconstruir(blocos)
    salvar(documento_id, questoes)

    print(f"\nQuestões reconstruídas: {len(questoes)}")
    print(f"Válidas: {sum(1 for _,_,q in questoes if q == 'valida')}")
    print(f"Válidas parciais: {sum(1 for _,_,q in questoes if q == 'valida_parcial')}")
    print(f"Revisar manual: {sum(1 for _,_,q in questoes if q == 'revisar_manual')}")

if __name__ == "__main__":
    main()
