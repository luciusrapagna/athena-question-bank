from pathlib import Path

p = Path("app.py")
txt = p.read_text(encoding="utf-8")

if "from app.classificadores.classificador_competencias import classificar" not in txt:
    txt = txt.replace(
        "import streamlit as st",
        "import streamlit as st\nfrom app.classificadores.classificador_competencias import classificar"
    )

if "def preencher_competencia_habilidade" not in txt:
    bloco = r'''

def preencher_competencia_habilidade(q):
    comp = str(q.get("competencia", "") or "").strip()
    hab = str(q.get("habilidade", "") or "").strip()

    if comp and hab:
        return q

    texto = " ".join([
        str(q.get("grande_area", "") or ""),
        str(q.get("area", "") or ""),
        str(q.get("tema_indexado", "") or ""),
        str(q.get("tema", "") or ""),
        str(q.get("assunto", "") or ""),
        str(q.get("enunciado", "") or "")
    ])

    try:
        resultado = classificar(texto)

        if isinstance(resultado, dict):
            if not comp:
                q["competencia"] = resultado.get("competencia", "") or ""
            if not hab:
                q["habilidade"] = resultado.get("habilidade", "") or ""

    except Exception:
        q["competencia"] = comp
        q["habilidade"] = hab

    return q
'''

    txt = txt.replace("def gerar_word_question_selector", bloco + "\n\ndef gerar_word_question_selector")

p.write_text(txt, encoding="utf-8")
print("Função preencher_competencia_habilidade inserida.")
