from pathlib import Path

arquivo = Path("app.py")
txt = arquivo.read_text(encoding="utf-8")

txt = txt.replace(
    'st.write("**Objetivos da semana:**", aula_area.get("objetivos", ""))',
    '# objetivos removidos sprint9'
)

txt = txt.replace(
    'doc.add_paragraph(f"Área: {area} | Assunto: {assunto} | Competência: {competencia}")',
    '''
habilidade = limpar_campo_word(q.get("habilidade",""))
doc.add_paragraph(
    f"Área: {area} | Assunto: {assunto} | Competência: {competencia} | Habilidade: {habilidade}"
)
'''
)

txt = txt.replace(
    '''doc.add_paragraph(f"Área: {q.get('area','')} | Assunto: {q.get('assunto','')} | Competência: {q.get('competencia','')}")''',
    '''
doc.add_paragraph(
    f"Área: {q.get('area','')} | Assunto: {q.get('assunto','')} | Competência: {q.get('competencia','')} | Habilidade: {q.get('habilidade','')}"
)
'''
)

if "def separar_alternativas(" not in txt:
    bloco = r'''

def separar_alternativas(texto):
    import re
    if not texto:
        return ""

    texto = re.sub(r'\s+A\)', '\nA)', texto)
    texto = re.sub(r'\s+B\)', '\nB)', texto)
    texto = re.sub(r'\s+C\)', '\nC)', texto)
    texto = re.sub(r'\s+D\)', '\nD)', texto)
    texto = re.sub(r'\s+E\)', '\nE)', texto)

    return texto
'''
    txt = txt.replace("def limpar_campo_word", bloco + "\n\ndef limpar_campo_word")

txt = txt.replace(
    'doc.add_paragraph(limpar_campo_word(q.get("enunciado", "")))',
    'doc.add_paragraph(separar_alternativas(limpar_campo_word(q.get("enunciado", ""))))'
)

txt = txt.replace(
    'doc.add_paragraph(limpar_xml(q.get("enunciado", "")))',
    'doc.add_paragraph(separar_alternativas(limpar_xml(q.get("enunciado", ""))))'
)

arquivo.write_text(txt, encoding="utf-8")
print("Sprint 9 aplicado com sucesso no VPS.")
