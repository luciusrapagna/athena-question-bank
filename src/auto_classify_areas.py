import sqlite3
from pathlib import Path

DB_PATH = Path("database/question_bank.db")

REGRAS = {
    "Saúde Coletiva": [
        "atenção primária", "ubs", "sus", "estratégia saúde da família",
        "conselho municipal de saúde", "vigilância", "vacinação",
        "epidemiologia", "prevenção", "rastreamento", "notificação"
    ],
    "Clínica Médica": [
        "dor torácica", "diabetes", "hipertensão", "insuficiência cardíaca",
        "tuberculose", "hiv", "anemia", "asma", "dpoc", "renal"
    ],
    "Cirurgia": [
        "trauma", "abdome agudo", "apendicite", "colecistite",
        "pós-operatório", "cirurgia", "hérnia", "queimadura"
    ],
    "Pediatria": [
        "criança", "lactente", "recém-nascido", "adolescente",
        "puericultura", "vacina tríplice", "crescimento", "desenvolvimento"
    ],
    "Ginecologia e Obstetrícia": [
        "gestante", "pré-natal", "parto", "puerpério",
        "menstruação", "contracepção", "colo do útero", "mama"
    ]
}

def classificar(texto):
    texto_lower = texto.lower()

    pontuacoes = {}

    for area, palavras in REGRAS.items():
        pontos = sum(1 for p in palavras if p in texto_lower)
        pontuacoes[area] = pontos

    area_escolhida = max(pontuacoes, key=pontuacoes.get)

    if pontuacoes[area_escolhida] == 0:
        return "Não classificada"

    return area_escolhida

conn = sqlite3.connect(DB_PATH)
cur = conn.cursor()

cur.execute("SELECT id, texto_questao FROM questoes_extraidas")
questoes = cur.fetchall()

total = 0

for qid, texto in questoes:
    area = classificar(texto or "")

    cur.execute("""
    UPDATE questoes_extraidas
    SET area = ?
    WHERE id = ?
    """, (area, qid))

    total += 1

conn.commit()
conn.close()

print(f"Classificação automática concluída. Questões processadas: {total}")
