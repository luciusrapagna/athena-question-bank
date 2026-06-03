import sqlite3

DB_PATH = "app/db/planos_aula.db"

REGRAS = {

    "Clínica Médica": {
        "Cardiologia": [
            "infarto",
            "ecg",
            "troponina",
            "angina",
            "cardiopatia",
            "insuficiência cardíaca",
            "bnp",
            "fração de ejeção"
        ],

        "Pneumologia": [
            "asma",
            "dpoc",
            "dispneia",
            "espirometria"
        ],

        "Nefrologia": [
            "creatinina",
            "acidose",
            "hemodiálise",
            "proteinúria"
        ]
    },

    "Pediatria": {
        "Pediatria Geral": [
            "lactente",
            "recém-nascido",
            "puericultura",
            "vacinação",
            "aleitamento"
        ]
    },

    "Cirurgia": {
        "Trauma": [
            "politrauma",
            "trauma",
            "escada",
            "glasgow"
        ]
    },

    "Ginecologia e Obstetrícia": {
        "Ginecologia": [
            "dismenorreia",
            "dispareunia",
            "endometriose",
            "colo uterino"
        ]
    },

    "Saúde Coletiva": {
        "APS": [
            "ubs",
            "atenção primária",
            "prevenção",
            "território"
        ]
    }
}


def classificar(texto):

    texto = (texto or "").lower()

    melhor_area = None
    melhor_subarea = None
    melhor_score = 0

    for area, subareas in REGRAS.items():

        for subarea, termos in subareas.items():

            score = sum(
                1 for termo in termos
                if termo in texto
            )

            if score > melhor_score:
                melhor_score = score
                melhor_area = area
                melhor_subarea = subarea

    return melhor_area, melhor_subarea


def executar():

    con = sqlite3.connect(DB_PATH)
    cur = con.cursor()

    questoes = cur.execute("""
        SELECT id, enunciado
        FROM questoes
    """).fetchall()

    total = 0

    for questao_id, enunciado in questoes:

        area, subarea = classificar(enunciado)

        cur.execute("""
            UPDATE questoes
            SET grande_area = ?,
                subarea = ?
            WHERE id = ?
        """,
        (
            area,
            subarea,
            questao_id
        ))

        total += 1

    con.commit()
    con.close()

    print(f"{total} questões classificadas.")


if __name__ == "__main__":
    executar()