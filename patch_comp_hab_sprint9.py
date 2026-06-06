from pathlib import Path

p = Path("app.py")
txt = p.read_text(encoding="utf-8")

# Importa classificador se ainda não estiver importado
if "from app.lesson_planner.planner import planejar" not in txt:
    txt = txt.replace(
        "import streamlit as st",
        "import streamlit as st\nfrom app.lesson_planner.planner import planejar"
    )

# Adiciona função auxiliar
if "def preencher_competencia_habilidade" not in txt:
    bloco = r'''

def preencher_competencia_habilidade(q):
    """
    Garante que cada questão tenha competência e habilidade antes da exportação Word.
    Usa o classificador existente do ATHENA quando os campos estiverem vazios.
    """
    comp = str(q.get("competencia", "") or "").strip()
    hab = str(q.get("habilidade", "") or "").strip()

    if comp and hab:
        return q

    try:
        texto = " ".join([
            str(q.get("grande_area", "") or ""),
            str(q.get("area", "") or ""),
            str(q.get("tema_indexado", "") or ""),
            str(q.get("tema", "") or ""),
            str(q.get("assunto", "") or ""),
            str(q.get("enunciado", "") or "")
        ])

        resultado = planejar(texto)

        if not comp:
            q["competencia"] = resultado.competencias[0] if getattr(resultado, "competencias", None) else ""

        if not hab:
            q["habilidade"] = resultado.habilidades[0] if getattr(resultado, "habilidades", None) else ""

    except Exception:
        q["competencia"] = comp
        q["habilidade"] = hab

    return q
'''
    txt = txt.replace("def gerar_word_question_selector", bloco + "\n\ndef gerar_word_question_selector")

# Aplica no Word semanal
txt = txt.replace(
    "for i, q in enumerate(questoes, start=1):\n            doc.add_heading",
    "for i, q in enumerate(questoes, start=1):\n            q = preencher_competencia_habilidade(q)\n            doc.add_heading"
)

# Aplica no gerar_docx geral
txt = txt.replace(
    "for i, q in enumerate(questoes, 1):\n        doc.add_heading",
    "for i, q in enumerate(questoes, 1):\n        q = preencher_competencia_habilidade(q)\n        doc.add_heading"
)

p.write_text(txt, encoding="utf-8")
print("Competência e habilidade ENAMED preenchidas antes do Word.")
