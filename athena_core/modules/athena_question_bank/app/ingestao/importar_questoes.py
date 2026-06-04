import csv
import re
from pathlib import Path
from app.config_paths import DIR_PROVAS_ENTRADA, BANCO_QUESTOES
from app.ingestao.leitor_arquivos import ler_arquivo


def limpar_texto(texto):
    return " ".join(texto.replace("\n", " ").replace("\r", " ").split())


def inferir_fonte(nome):
    nome_lower = nome.lower()
    if "enamed" in nome_lower:
        return "ENAMED"
    if "enade" in nome_lower:
        return "ENADE"
    if "enare" in nome_lower:
        return "ENARE"
    return "Não identificada"


def inferir_ano(nome, texto):
    busca = nome + " " + texto[:1000]
    match = re.search(r"(20\d{2})", busca)
    return match.group(1) if match else ""


def inferir_area(texto):
    texto_lower = texto.lower()

    mapa = {
        "Saúde Coletiva": [
            "sus", "sistema único de saúde", "epidemiologia", "incidência", "prevalência",
            "vigilância", "território", "atenção primária", "atenção básica", "esf",
            "saúde da família", "notificação", "dengue", "vacinação", "campanha",
            "promoção da saúde", "prevenção", "política pública", "determinantes sociais", "internação involuntária", "caps", "centro de atenção psicossocial", "ubS", "unidade básica de saúde", "dependência", "substâncias psicoativas", "DSM-5", "penitenciária", "médico de família",
            "mortalidade", "morbidade", "risco relativo", "odds ratio"
        ],
        "Clínica Médica": [
            "sepse", "diabetes", "hipertensão", "pneumonia", "choque", "infarto",
            "insuficiência cardíaca", "asma", "dpoc", "doença renal", "anemia",
            "febre", "dispneia", "dor torácica", "lactato", "antibioticoterapia",
            "eletrocardiograma", "creatinina", "glicemia", "trombose", "avc", "trauma cranioencefálico", "inconsciente", "tomografia de crânio", "esporotricose", "itraconazol", "distonia", "haloperidol", "biperideno", "artrite reumatoide", "fator reumatoide", "metotrexato", "parkinson", "levodopa", "carbidopa", "intoxicação", "benzodiazepínico", "clonazepam", "flumazenil", "diarreia", "rifaximina", "tuberculose", "mycobacterium tuberculosis"
        ],
        "Pediatria": [
            "criança", "recém-nascido", "adolescente", "pediatria", "vacinação infantil",
            "aleitamento", "crescimento", "desenvolvimento", "baixo peso", "prematuro",
            "lactente", "neonato", "puericultura", "desidratação infantil"
        ],
        "Ginecologia e Obstetrícia": [
            "gestante", "pré-natal", "parto", "ginecologia", "obstetrícia",
            "puerpério", "contracepção", "colo do útero", "papanicolau",
            "sangramento uterino", "menstruação", "gravidez", "eclâmpsia",
            "pré-eclâmpsia", "mama", "câncer de mama", "insensibilidade androgênica", "amenorreia", "ausência do útero", "cariótipo 46 xy", "candidíase", "prurido genital", "corrimento esbranquiçado", "miconazol", "lesão intraepitelial", "citologia oncótica", "colposcopia", "sangramento vaginal", "endométrio", "leiomioma", "colo uterino"
        ],
        "Cirurgia": [
            "cirurgia", "pré-operatório", "pós-operatório", "abdome agudo",
            "apendicite", "trauma", "hemorragia", "anestesia", "ferida",
            "sutura", "colecistite", "hérnia", "laparotomia", "queimadura", "colisão", "samu", "pneumotórax", "desvio da traqueia", "murmúrio vesicular", "turgência de veias jugulares", "toracocentese", "cricotireoidostomia", "pericardiocentese", "atendimento pré-hospitalar"
        ],
    }

    pontuacao = {}

    for area, termos in mapa.items():
        pontos = 0
        for termo in termos:
            if termo in texto_lower:
                pontos += 1
        pontuacao[area] = pontos

    melhor_area = max(pontuacao, key=pontuacao.get)

    if pontuacao[melhor_area] == 0:
        return "Não classificada"

    return melhor_area


def inferir_assunto(texto):
    texto_lower = texto.lower()

    mapa = {
        "Cardiologia": ["hipertensão arterial", "has", "insuficiência cardíaca", "bnp", "fração de ejeção", "angina", "troponina", "cateterismo", "síndrome coronariana", "fibrilação atrial"],
        "Nefrologia": ["síndrome nefrótica", "proteinúria", "albumina sérica", "hematúria"],
        "Endometriose": ["dismenorreia", "dispareunia", "endometriose"],
        "Hipertensão Arterial": ["pressão arterial", "losartana"],
        "Neurologia Vascular": ["acidente vascular", "avc", "artéria cerebral média", "trombólise"],
        "Diabetes Mellitus": ["cetoacidose", "hálito cetótico", "cetonúria", "insulina", "gasometria arterial"],
        "Hepatologia": ["colangiorressonância", "colestática", "vias biliares", "icterícia", "colúria", "acolia", "gama-gt", "fosfatase alcalina"],
        "Arboviroses": ["chikungunya", "aedes", "dengue"],
        "Imunizações": ["vacinas", "imunização", "influenza", "covid-19", "hepatite b"],
        "Violência e Vulnerabilidade": ["conselho tutelar", "violência contra adolescentes", "medidas socioeducativas", "equimoses"],
        "Endocrinologia": ["tireoide", "tsh", "t4 livre", "tireoidite", "metimazol", "diabetes mellitus"],
        "Coloproctologia": ["diverticulite", "fossa ilíaca esquerda", "hematoquezia", "colonoscopia"],
        "Saúde Prisional": ["penitenciária", "unidade prisional", "pessoas privadas de liberdade", "cela"],
        "Cirurgia de Cabeça e Pescoço": ["tireoidectomia", "nervo laríngeo", "laríngeo recorrente", "rouquidão"],
        "Oncologia": ["câncer", "ca 19.9", "perda de peso", "lesão tumoral"],
        "Sepse": ["sepse", "lactato", "antibioticoterapia", "choque séptico", "antibiótico de amplo espectro"],
        "Dengue e Vigilância Epidemiológica": ["vigilância epidemiológica", "incidência", "prevalência"],
        "Trauma e Atendimento Pré-Hospitalar": ["trauma", "colisão", "samu", "atendimento pré-hospitalar", "toracocentese", "cricotireoidostomia"],
        "Doenças Infecciosas": ["tuberculose", "mycobacterium", "esporotricose", "itraconazol", "hiv", "sífilis"],
        "Saúde Mental": ["caps", "esquizofrenia", "haloperidol", "distonia", "substâncias psicoativas", "internação involuntária", "dsm-5"],
        "Reumatologia": ["artrite reumatoide", "fator reumatoide", "metotrexato", "lúpus", "fan", "arterite temporal", "velocidade de hemossedimentação"],
        "Neurologia": ["parkinson", "levodopa", "carbidopa", "convulsão"],
        "Ginecologia": ["citologia oncótica", "lesão intraepitelial", "colo uterino", "papanicolau", "colposcopia", "candidíase", "prurido genital", "corrimento esbranquiçado"],
        "Obstetrícia": ["gestante", "pré-natal", "parto", "puerpério", "pré-eclâmpsia"],
        "Pediatria": ["criança", "recém-nascido", "lactente", "puericultura", "aleitamento", "menino", "menina"],
        "Cirurgia Geral": ["abdome agudo", "apendicite", "colecistite", "hérnia", "laparotomia"],
        "Toxicologia": ["intoxicação", "clonazepam", "flumazenil", "benzodiazepínico"],
        "Gastroenterologia": ["diarreia", "rifaximina", "lactulose", "intestino", "endoscopia"],
        "Atenção Primária à Saúde": ["unidade básica de saúde", "ubs", "médico de família", "saúde da família", "atenção primária"],
    }

    pontuacao = {}

    for assunto, termos in mapa.items():
        pontos = 0
        for termo in termos:
            if termo in texto_lower:
                pontos += 1
        pontuacao[assunto] = pontos

    melhor_assunto = max(pontuacao, key=pontuacao.get)

    if pontuacao[melhor_assunto] == 0:
        return "Assunto não identificado"

    return melhor_assunto
def inferir_competencia(texto):
    texto_lower = texto.lower()

    if any(t in texto_lower for t in ["conduta", "tratamento", "manejo", "prescrever", "medicação", "terapêutico"]):
        return "Definir conduta e manejo terapêutico"

    if any(t in texto_lower for t in ["hipótese diagnóstica", "diagnóstico", "principal hipótese", "achado laboratorial"]):
        return "Estabelecer hipótese diagnóstica"

    if any(t in texto_lower for t in ["incidência", "prevalência", "indicadores", "risco relativo", "odds ratio"]):
        return "Interpretar indicadores e dados epidemiológicos"

    if any(t in texto_lower for t in ["prevenção", "promoção", "vigilância", "notificação", "busca ativa"]):
        return "Planejar ações de prevenção e vigilância em saúde"

    if any(t in texto_lower for t in ["lei", "legislação", "direito", "ética", "consentimento"]):
        return "Aplicar princípios éticos e legais na prática médica"

    return "Competência clínica geral"

def dividir_questoes(texto):
    padrao = r"(?=(?:QUESTÃO|Questão)\s+\d{1,3}\b)"
    partes = re.split(padrao, texto)
    partes = [p.strip() for p in partes if len(p.strip()) > 30]

    if partes:
        return partes

    return [texto] if len(texto.strip()) > 30 else []


def extrair_alternativa(bloco, letra):
    padrao = rf"{letra}\)\s*(.*?)(?=\s+[A-E]\)|$)"
    match = re.search(padrao, bloco, flags=re.IGNORECASE | re.DOTALL)
    return limpar_texto(match.group(1)) if match else ""


def importar_questoes():
    arquivos = (
        list(DIR_PROVAS_ENTRADA.glob("*.txt")) +
        list(DIR_PROVAS_ENTRADA.glob("*.md")) +
        list(DIR_PROVAS_ENTRADA.glob("*.docx")) +
        list(DIR_PROVAS_ENTRADA.glob("*.pdf"))
    )
    registros = []
    contador = 1

    for arquivo in arquivos:
        texto = ler_arquivo(arquivo)
        blocos = dividir_questoes(texto)

        for bloco in blocos:
            bloco_upper = bloco.upper()

            if "LEIA COM ATENÇÃO AS INSTRUÇÕES" in bloco_upper:
                continue

            if "CARTÃO-RESPOSTA" in bloco_upper:
                continue

            if len(bloco.strip()) < 80:
                continue

            bloco_upper = bloco.upper()

            termos_excluir = [
                "QUAL O GRAU DE DIFICULDADE",
                "TEMPO GASTO POR VOCÊ",
                "VOCÊ SE DEPAROU COM ALGUMA DIFICULDADE",
                "COMO VOCÊ AVALIA A SEQUÊNCIA",
                "QUESTÕES DA PROVA",
                "PERCEPÇÃO DA PROVA",
                "TEMPO TOTAL DE APLICAÇÃO",
                "ENUNCIADOS DAS QUESTÕES",
                "INFORMAÇÕES/INSTRUÇÕES",
                "ATIVIDADES PRÁTICAS DESENVOLVIDAS"
            ]

            if any(t in bloco_upper for t in termos_excluir):
                continue

            enunciado = re.split(r"\s+[A-E]\)", bloco, maxsplit=1)[0]
            enunciado = limpar_texto(enunciado)

            registro = {
                "id_questao": f"Q{contador:05d}",
                "fonte": inferir_fonte(arquivo.name),
                "ano": inferir_ano(arquivo.name, texto),
                "prova": arquivo.stem,
                "area": inferir_area(bloco),
                "assunto": inferir_assunto(bloco),
                "competencia": inferir_competencia(bloco),
                "enunciado": enunciado,
                "alternativa_a": extrair_alternativa(bloco, "A"),
                "alternativa_b": extrair_alternativa(bloco, "B"),
                "alternativa_c": extrair_alternativa(bloco, "C"),
                "alternativa_d": extrair_alternativa(bloco, "D"),
                "alternativa_e": extrair_alternativa(bloco, "E"),
                "gabarito": "",
            }

            registros.append(registro)
            contador += 1

    with open(BANCO_QUESTOES, "w", encoding="utf-8-sig", newline="") as f:
        campos = [
            "id_questao", "fonte", "ano", "prova", "area", "assunto", "competencia", "enunciado",
            "alternativa_a", "alternativa_b", "alternativa_c", "alternativa_d",
            "alternativa_e", "gabarito"
        ]
        writer = csv.DictWriter(f, fieldnames=campos)
        writer.writeheader()
        writer.writerows(registros)

    print(f"Questões importadas: {len(registros)}")
    print(f"Banco gerado em: {BANCO_QUESTOES}")


if __name__ == "__main__":
    importar_questoes()








