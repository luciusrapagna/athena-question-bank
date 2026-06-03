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

def listar_documentos():
    conn = conectar()
    cur = conn.cursor()

    cur.execute("""
    SELECT id, prova, instituicao, ano, tipo, arquivo_origem
    FROM documentos
    ORDER BY id DESC
    """)

    docs = cur.fetchall()
    conn.close()
    return docs

def buscar_documento(documento_id):
    conn = conectar()
    cur = conn.cursor()

    cur.execute("""
    SELECT arquivo_origem
    FROM documentos
    WHERE id = ?
    """, (documento_id,))

    row = cur.fetchone()
    conn.close()

    return row[0] if row else None

def limpar_linha(texto):
    texto = texto.replace("￾", "-")
    texto = texto.replace("\r", "")
    texto = re.sub(r"[ \t]+", " ", texto)
    return texto.strip()

def extrair_blocos_posicionais(pdf_path):
    doc = fitz.open(pdf_path)
    todos = []

    for page_index, page in enumerate(doc, start=1):
        largura = page.rect.width
        blocks = page.get_text("blocks")

        for b in blocks:
            x0, y0, x1, y1, txt = b[:5]
            txt = limpar_linha(txt)

            if not txt:
                continue

            if "Núcleo Mineiro" in txt:
                continue

            if "Teste de Progresso" in txt:
                continue

            if "ÁREA LIVRE" in txt.upper():
                continue

            coluna = 1 if x0 < largura / 2 else 2

            todos.append({
                "pagina": page_index,
                "coluna": coluna,
                "x0": x0,
                "y0": y0,
                "texto": txt
            })

    todos = sorted(todos, key=lambda b: (b["pagina"], b["coluna"], b["y0"], b["x0"]))

    return todos

def eh_inicio_questao(texto):
    return re.match(r"^\s*(?:QUESTÃO\s*)?\d{1,3}[\.\)]\s+", texto, flags=re.I) is not None

def numero_questao(texto):
    m = re.match(r"^\s*(?:QUESTÃO\s*)?(\d{1,3})[\.\)]\s+", texto, flags=re.I)
    if m:
        n = int(m.group(1))
        if 1 <= n <= 200:
            return n
    return None

def reconstruir_questoes(blocos):
    questoes = {}
    atual = None

    for b in blocos:
        texto = b["texto"]

        if eh_inicio_questao(texto):
            n = numero_questao(texto)

            if n:
                atual = n

                if n not in questoes:
                    questoes[n] = []

                questoes[n].append(texto)
                continue

        if atual is not None:
            questoes[atual].append(texto)

    saida = []

    for n in sorted(questoes):
        bloco = "\n".join(questoes[n])
        bloco = normalizar_alternativas(bloco)
        bloco = aparar_questao(bloco)
        saida.append((n, bloco))

    return saida

def normalizar_alternativas(texto):
    texto = re.sub(r"(?m)^([A-E])\.\s+", r"(\1) ", texto)
    texto = re.sub(r"(?m)^([A-E])\)\s+", r"(\1) ", texto)
    texto = re.sub(r"(?m)^\(([A-E])\)\s*", r"(\1) ", texto)
    return texto

def aparar_questao(texto):
    linhas = []

    for linha in texto.splitlines():
        l = linha.strip()

        if not l:
            continue

        if "Núcleo Mineiro" in l:
            continue

        if "Teste de Progresso" in l:
            continue

        if re.match(r"^\d+\s*$", l):
            continue

        linhas.append(l)

    texto = "\n".join(linhas)
    texto = re.sub(r"\n{3,}", "\n\n", texto)
    return texto.strip()

def qualidade(texto):
    tem_a = "(A)" in texto
    tem_b = "(B)" in texto
    tem_c = "(C)" in texto
    tem_d = "(D)" in texto

    duplicada = any(texto.count(alt) > 1 for alt in ["(A)", "(B)", "(C)", "(D)"])

    if tem_a and tem_b and tem_c and tem_d and not duplicada and len(texto) > 120:
        return "valida"

    return "revisar_manual"

def salvar_questoes(documento_id, questoes):
    conn = conectar()
    cur = conn.cursor()

    cur.execute("DELETE FROM questoes_extraidas WHERE documento_id = ?", (documento_id,))

    for n, texto in questoes:
        cur.execute("""
        INSERT INTO questoes_extraidas
        (documento_id, numero_questao, texto_questao, qualidade)
        VALUES (?, ?, ?, ?)
        """, (documento_id, n, texto, qualidade(texto)))

    conn.commit()
    conn.close()

def main():
    docs = listar_documentos()

    print("\nDOCUMENTOS IMPORTADOS")
    print("-" * 90)

    for d in docs:
        print(f"ID {d[0]} | {d[1]} | {d[2]} | {d[3]} | {d[4]} | {d[5]}")

    documento_id = int(input("\nDigite o ID do documento para reconstrução posicional: "))

    pdf_path = buscar_documento(documento_id)

    if not pdf_path:
        print("PDF original não encontrado no banco.")
        return

    if not Path(pdf_path).exists():
        print(f"Arquivo original não existe mais neste caminho: {pdf_path}")
        return

    blocos = extrair_blocos_posicionais(pdf_path)
    questoes = reconstruir_questoes(blocos)

    salvar_questoes(documento_id, questoes)

    print(f"\nReconstrução concluída.")
    print(f"Questões reconstruídas: {len(questoes)}")

    validas = sum(1 for _, t in questoes if qualidade(t) == "valida")
    revisar = len(questoes) - validas

    print(f"Válidas: {validas}")
    print(f"Revisar manual: {revisar}")

    for n, texto in questoes[:10]:
        print("\n" + "=" * 60)
        print(f"QUESTÃO {n} | {qualidade(texto)}")
        print(texto[:700])

if __name__ == "__main__":
    main()
