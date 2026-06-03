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

def limpar(txt):
    txt = txt.replace("￾", "-").replace("\r", "")
    txt = re.sub(r"[ \t]+", " ", txt)
    return txt.strip()

def util(txt):
    t = txt.upper()
    lixos = [
        "ÁREA LIVRE", "RASCUNHO", "LEIA COM ATENÇÃO", "INSTRUÇÕES",
        "CADERNO", "CARTÃO-RESPOSTA", "NÚCLEO MINEIRO",
        "TESTE DE PROGRESSO", "MEDWAY - ENARE", "PÁGINAS"
    ]
    return not any(x in t for x in lixos)

def eh_inicio(txt):
    return re.match(r"^\s*(QUESTÃO\s*)?\d{1,3}[\.\)]?\s+", txt, re.I) is not None

def numero(txt):
    m = re.match(r"^\s*(QUESTÃO\s*)?(\d{1,3})[\.\)]?\s+", txt, re.I)
    if not m:
        return None
    n = int(m.group(2))
    return n if 1 <= n <= 200 else None

def normalizar_alt(txt):
    txt = re.sub(r"(?m)^([A-E])\.\s+", r"(\1) ", txt)
    txt = re.sub(r"(?m)^([A-E])\)\s+", r"(\1) ", txt)
    txt = re.sub(r"(?m)^\(([A-E])\)\s*", r"(\1) ", txt)
    return txt

def qualidade(txt):
    txt = normalizar_alt(txt)

    tem_a = "(A)" in txt
    tem_b = "(B)" in txt
    tem_c = "(C)" in txt
    tem_d = "(D)" in txt

    duplicada = any(txt.count(f"({l})") > 1 for l in "ABCD")

    if tem_a and tem_b and tem_c and tem_d and not duplicada and len(txt) > 120:
        return "valida"

    if tem_a and tem_b and tem_c and not duplicada and len(txt) > 120:
        return "valida_parcial"

    return "revisar_manual"

def cortar_sobras(txt, n):
    m = re.search(rf"\n\s*(QUESTÃO\s*)?({n+1}|{n+2})[\.\)]?\s+", txt, re.I)
    if m:
        txt = txt[:m.start()].strip()

    pos_a = [m.start() for m in re.finditer(r"\(A\)", txt)]
    if len(pos_a) > 1:
        txt = txt[:pos_a[1]].strip()

    return txt.strip()

def extrair_blocos_colunas(pdf_path):
    doc = fitz.open(pdf_path)
    blocos_por_fluxo = []

    for pnum, page in enumerate(doc, start=1):
        w = page.rect.width
        h = page.rect.height

        esquerda = []
        direita = []
        largura_total = []

        for b in page.get_text("blocks"):
            x0, y0, x1, y1, txt = b[:5]

            if y0 < h * 0.055 or y1 > h * 0.955:
                continue

            txt = limpar(txt)

            if not txt or not util(txt):
                continue

            if re.match(r"^\d{1,3}$", txt):
                continue

            bloco = {
                "pagina": pnum,
                "x0": x0,
                "x1": x1,
                "y0": y0,
                "texto": txt
            }

            if x0 < w * 0.45 and x1 < w * 0.62:
                esquerda.append(bloco)
            elif x0 > w * 0.38:
                direita.append(bloco)
            else:
                largura_total.append(bloco)

        esquerda = sorted(esquerda, key=lambda b: (b["y0"], b["x0"]))
        direita = sorted(direita, key=lambda b: (b["y0"], b["x0"]))
        largura_total = sorted(largura_total, key=lambda b: (b["y0"], b["x0"]))

        # processa cada coluna como fluxo independente
        blocos_por_fluxo.extend(esquerda)
        blocos_por_fluxo.extend(direita)
        blocos_por_fluxo.extend(largura_total)

    return blocos_por_fluxo

def montar_questoes(blocos):
    questoes = {}
    atual = None

    for b in blocos:
        txt = b["texto"]

        if eh_inicio(txt):
            n = numero(txt)
            if n:
                atual = n
                questoes.setdefault(n, [])
                questoes[n].append(txt)
                continue

        if atual is not None:
            questoes[atual].append(txt)

    saida = []

    for n in sorted(questoes):
        txt = "\n".join(questoes[n])
        txt = normalizar_alt(txt)
        txt = cortar_sobras(txt, n)
        txt = re.sub(r"\n{3,}", "\n\n", txt).strip()
        saida.append((n, txt, qualidade(txt)))

    return saida

def listar_docs():
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
    docs = listar_docs()

    print("\nDOCUMENTOS")
    print("-" * 90)

    for d in docs:
        print(f"ID {d[0]} | {d[1]} | {d[2]} | {d[3]} | {d[4]} | {d[5]}")

    documento_id = int(input("\nDigite o ID do documento: "))
    doc = [d for d in docs if d[0] == documento_id][0]
    pdf_path = doc[5]

    if not Path(pdf_path).exists():
        print(f"PDF não encontrado: {pdf_path}")
        return

    blocos = extrair_blocos_colunas(pdf_path)
    questoes = montar_questoes(blocos)
    salvar(documento_id, questoes)

    print("\nATHENA COLUMN READER concluído.")
    print(f"Questões: {len(questoes)}")
    print(f"Válidas: {sum(1 for _,_,q in questoes if q == 'valida')}")
    print(f"Válidas parciais: {sum(1 for _,_,q in questoes if q == 'valida_parcial')}")
    print(f"Revisar manual: {sum(1 for _,_,q in questoes if q == 'revisar_manual')}")

if __name__ == "__main__":
    main()
