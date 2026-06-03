import sqlite3
from pathlib import Path

DB_PATH = Path("database/question_bank.db")

REGRAS = {
    "Saúde Coletiva": [
        "atenção primária", "aps", "ubs", "unidade básica", "saúde da família",
        "estratégia saúde da família", "esf", "sus", "conselho municipal",
        "controle social", "vigilância", "vigilância epidemiológica",
        "vigilância sanitária", "vigilância em saúde", "notificação",
        "notificação compulsória", "epidemiologia", "prevalência",
        "incidência", "mortalidade", "letalidade", "risco relativo",
        "odds ratio", "rastreamento", "prevenção", "promoção da saúde",
        "vacinação", "imunização", "calendário vacinal", "pacto pela saúde",
        "financiamento", "regionalização", "rede de atenção",
        "atenção integral", "equidade", "territorialização",
        "agente comunitário", "visita domiciliar", "saúde pública",
        "política nacional", "programa nacional"
    ],

    "Clínica Médica": [
        "dor torácica", "infarto", "angina", "síndrome coronariana",
        "hipertensão", "diabetes", "insuficiência cardíaca", "arritmia",
        "ecg", "troponina", "dispneia", "asma", "dpoc", "pneumonia",
        "tuberculose", "hiv", "aids", "anemia", "leucemia",
        "insuficiência renal", "doença renal", "creatinina",
        "proteinúria", "cirrose", "hepatite", "gastrite", "úlcera",
        "diarreia", "endocrinologia", "tireoide", "hipotireoidismo",
        "hipertireoidismo", "cetoacidose", "coma hiperosmolar",
        "avc", "convulsão", "cefaleia", "demência", "parkinson",
        "lúpus", "artrite", "febre reumática", "sepse"
    ],

    "Cirurgia": [
        "trauma", "politrauma", "abdome agudo", "apendicite",
        "colecistite", "colangite", "pancreatite aguda",
        "obstrução intestinal", "hérnia", "peritonite",
        "pós-operatório", "pré-operatório", "cirurgia",
        "laparotomia", "laparoscopia", "ferida operatória",
        "queimadura", "hemorragia", "choque hipovolêmico",
        "fratura", "luxação", "suturar", "drenagem",
        "abscesso", "anestesia", "risco cirúrgico",
        "transfusão", "trombose venosa", "embolia pulmonar"
    ],

    "Pediatria": [
        "criança", "lactente", "recém-nascido", "neonato",
        "adolescente", "puericultura", "crescimento",
        "desenvolvimento infantil", "aleitamento materno",
        "amamentação", "desnutrição infantil", "baixo peso",
        "prematuro", "icterícia neonatal", "teste do pezinho",
        "vacina tríplice", "bronquiolite", "asma infantil",
        "diarreia infantil", "desidratação infantil",
        "febre em criança", "convulsão febril", "exantema",
        "varicela", "sarampo", "coqueluche", "otite média",
        "síndrome nefrótica", "cardiopatia congênita"
    ],

    "Ginecologia e Obstetrícia": [
        "gestante", "gestação", "gravidez", "pré-natal",
        "parto", "cesárea", "puerpério", "abortamento",
        "sangramento vaginal", "eclâmpsia", "pré-eclâmpsia",
        "diabetes gestacional", "hipertensão gestacional",
        "bolsa rota", "trabalho de parto", "contrações",
        "colo uterino", "colo do útero", "papanicolau",
        "preventivo", "hpv", "câncer de colo", "câncer de mama",
        "mama", "nódulo mamário", "menstruação", "amenorreia",
        "dismenorreia", "contracepção", "anticoncepcional",
        "diu", "climatério", "menopausa", "endometriose",
        "mioma", "corrimento vaginal", "infecção sexualmente transmissível"
    ]
}

def classificar(texto):
    texto_lower = texto.lower()
    pontuacoes = {}

    for area, palavras in REGRAS.items():
        pontos = 0
        for palavra in palavras:
            if palavra in texto_lower:
                pontos += 1
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

print(f"Classificação automática aprimorada concluída. Questões processadas: {total}")
