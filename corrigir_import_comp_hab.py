from pathlib import Path
import re

p = Path("app.py")
txt = p.read_text(encoding="utf-8")

# Remove import quebrado
txt = txt.replace(
    "from app.lesson_planner.planner import planejar\n",
    ""
)

# Substitui uso de planejar por classificador_competencias.classificar
if "from app.classificadores.classificador_competencias import classificar" not in txt:
    txt = txt.replace(
        "import streamlit as st",
        "import streamlit as st\nfrom app.classificadores.classificador_competencias import classificar"
    )

# Corrige função preencher_competencia_habilidade
txt = re.sub(
r'''def preencher_competencia_habilidade\(q\):.*?    return q\n''',
r'''def preencher_competencia_habilidade(q):
    """
    Garante competência e habilidade antes da exportação Word.
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

        resultado = classificar(texto)

        if isinstance(resultado, dict):
            if not comp:
                q["competencia"] = resultado.get("competencia", "") or resultado.get("competencias", "")
            if not hab:
                q["habilidade"] = resultado.get("habilidade", "") or resultado.get("habilidades", "")

    except Exception:
        q["competencia"] = comp
        q["habilidade"] = hab

    return q
''',
txt,
flags=re.DOTALL
)

p.write_text(txt, encoding="utf-8")
print("Import corrigido: removido planejar e aplicado classificar.")
