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

def texto_util(txt):
    t = txt.upper()
    lixos = [
        "ÁREA LIVRE", "RASCUNHO", "LEIA COM ATENÇÃO", "INSTRUÇÕES",
        "CADERNO", "CARTÃO-RESPOSTA", "NÚCLEO MINEIRO",
        "TESTE DE PROGRESSO", "MEDWAY - ENARE", "PÁGINAS"
    ]
    return not any(x in t for x in lixos)

def extrair_linhas_por_coluna(pdf_path):
    doc = fitz.open(pdf_path)
    linhas = []

    for pnum, page in enumerate(doc, start=1):
        w = page.rect.width
        h = page.rect.height

        blocks = page.get_text("blocks")

        for b in blocks:
            x0, y0, x1, y1, txt = b[:5]

            if y0 < h * 0.06 or y1 > h * 0.94:
                continue

            if x1 < w * 0.04 or x0 > w * 0.96:
                continue

            txt = limpar(txt)

            if not txt or not texto_util(txt):
                continue

            coluna = 1 if x0 < w / 2 else 2

            for linha in txt.splitlines():
                linha = limpar(linha)

                if not linha:
                    continue

                if not texto_util(linha):
                    continue

                if re.match(r"^\d{1,3}$", linha):
                    continue

                linhas.append({
                    "pagina": pnum,
                    "coluna": coluna,
                    "y": y0,
                    "x": x0,
                    "texto": linha
                })

    return sorted(linhas, key=lambda r: (r["pagina"], r["coluna"], r["y"], r["x"]))

def eh_inicio(linha):
    return re.match(r"^\s*(QUESTÃO\s*)?\d{1,3}[\.\)]?\s+", linha, re.I) is not None

def numero(linha):
    m = re.match(r"^\s*(QUESTÃO\s*)?(\d{1,3})[\.\)]?\s+", linha, re.I)
    if not m:
        return None
    n = int(m.group(2))
    return n if 1 <= n <= 200 else None

def normalizar_alt(txt):
    txt = re.sub(r"(?m)^([A-E])\.\s+", r"(\1) ", txt)
    txt = re.sub(r"(?m)^([A-E])\)\s+", r"(\1) ", txt)
    txt = re.sub(r"(?m)^\(([A-E])\)\s*", r"(\1) ", txt)
    return txt

def montar_questoes(linhas):
    questoes = {}
    atual = None

    for item in linhas:
        linha = item["texto"]

        if eh_inicio(linha):
            n = numero(linha)
            if n:
                atual = n
                questoes.setdefault(n, [])
                questoes[n].append(linha)
                continue

        if atual is not None:
            questoes[atual].append(linha)

    saida = []

    for n in sorted(questoes):
        txt = "\n".join(questoes[n])
        txt = normalizar_alt(txt)
        txt = cortar_sobras(txt, n)
        saida.append((n, txt, qualidade(txt)))

    return saida

def cortar_sobras(txt, n):
    # corta se a próxima questão entrou no bloco
    m = re.search(rf"\n\s*(QUESTÃO\s*)?({n+1}|{n+2})[\.\)]?\s+", txt, re.I)
    if m:
        txt = txt[:m.start()].strip()

    # corta se apareceu segundo conjunto de alternativas
    pos_a = [m.start() for m in re.finditer(r"\(A\)", txt)]
    if len(pos_a) > 1:
        txt = txt[:pos_a[1]].strip()

    # corta sobra isolada depois do primeiro D quando ela parece ser de outra questão
    pos_d = txt.find("(D)")
    if pos_d != -1:
        depois_d = txt[pos_d + 3:]
        m2 = re.search(r"\n\s*\([A-C]\)\s+", depois_d)
        if m2:
            txt = txt[:pos_d + 3 + m2.start()].strip()

    return txt.strip()

def qualidade(txt):
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

    for d in docs:
        print(f"ID {d[0]} | {d[1]} | {d[2]} | {d[3]} | {d[4]} | {d[5]}")

    documento_id = int(input("\nDigite o ID do documento: "))
    doc = [d for d in docs if d[0] == documento_id][0]
    pdf_path = doc[5]

    if not Path(pdf_path).exists():
        print(f"PDF não encontrado: {pdf_path}")
        return

    linhas = extrair_linhas_por_coluna(pdf_path)
    questoes = montar_questoes(linhas)
    salvar(documento_id, questoes)

    print("\nATHENA PAGE READER concluído.")
    print(f"Questões: {len(questoes)}")
    print(f"Válidas: {sum(1 for _,_,q in questoes if q == 'valida')}")
    print(f"Válidas parciais: {sum(1 for _,_,q in questoes if q == 'valida_parcial')}")
    print(f"Revisar manual: {sum(1 for _,_,q in questoes if q == 'revisar_manual')}")

if __name__ == "__main__":
    main()
