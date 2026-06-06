from pathlib import Path
import re

p = Path("app.py")
txt = p.read_text(encoding="utf-8")

# Corrige bloco do gerar_word_question_selector
txt = re.sub(
r'''            competencia = limpar_campo_word\(q\.get\("competencia", ""\)\)\n\s*habilidade = limpar_campo_word\(q\.get\("habilidade",""\)\)\ndoc\.add_paragraph\(\n    f"Área: \{area\} \| Assunto: \{assunto\} \| Competência: \{competencia\} \| Habilidade: \{habilidade\}"\n\)\n\n            doc\.add_paragraph\(separar_alternativas\(limpar_campo_word\(q\.get\("enunciado", ""\)\)\)\)''',
'''            competencia = limpar_campo_word(q.get("competencia", ""))
            habilidade = limpar_campo_word(q.get("habilidade", ""))

            doc.add_paragraph(
                f"Área: {area} | Assunto: {assunto} | Competência: {competencia} | Habilidade: {habilidade}"
            )

            doc.add_paragraph(separar_alternativas(limpar_campo_word(q.get("enunciado", ""))))''',
txt
)

# Corrige bloco do gerar_docx
txt = re.sub(
r'''        doc\.add_heading\(f"Questão \{i\}", level=2\)\n\s*doc\.add_paragraph\(\n    f"Área: \{q\.get\('area',''\)\} \| Assunto: \{q\.get\('assunto',''\)\} \| Competência: \{q\.get\('competencia',''\)\} \| Habilidade: \{q\.get\('habilidade',''\)\}"\n\)\n\n        doc\.add_paragraph\(separar_alternativas\(limpar_xml\(q\.get\("enunciado", ""\)\)\)\)''',
'''        doc.add_heading(f"Questão {i}", level=2)

        doc.add_paragraph(
            f"Área: {q.get('area','')} | Assunto: {q.get('assunto','')} | Competência: {q.get('competencia','')} | Habilidade: {q.get('habilidade','')}"
        )

        doc.add_paragraph(separar_alternativas(limpar_xml(q.get("enunciado", ""))))''',
txt
)

p.write_text(txt, encoding="utf-8")
print("Indentação Sprint 9 corrigida.")
