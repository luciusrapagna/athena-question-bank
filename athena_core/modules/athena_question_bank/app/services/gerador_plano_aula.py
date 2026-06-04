from pathlib import Path
from datetime import datetime


def gerar_plano_aula(tema, disciplina=None, periodo=None, competencias=None, habilidades=None):
    competencias = competencias or []
    habilidades = habilidades or []

    plano = {
        "tema": tema,
        "disciplina": disciplina or "Não informada",
        "periodo": periodo or "Não informado",
        "data_geracao": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "objetivos": [
            f"Compreender os fundamentos relacionados ao tema: {tema}.",
            "Aplicar o conhecimento em situações clínicas contextualizadas.",
            "Relacionar competências, habilidades e tomada de decisão médica."
        ],
        "competencias": competencias,
        "habilidades": habilidades,
        "metodologia": [
            "Aula dialogada contextualizada.",
            "Discussão de caso clínico.",
            "Estratégia ativa com PBL ou TBL.",
            "Resolução de questões orientadas por competências."
        ],
        "avaliacao": [
            "Participação na discussão.",
            "Resolução de situação-problema.",
            "Questões objetivas e discursivas contextualizadas."
        ],
        "bibliografia": [
            "Diretrizes Curriculares Nacionais do Curso de Medicina.",
            "Bibliografia básica e complementar indicada no PPC.",
            "Artigos científicos recentes relacionados ao tema."
        ]
    }

    return plano


def salvar_plano_markdown(plano, caminho_saida):
    caminho_saida = Path(caminho_saida)
    caminho_saida.parent.mkdir(parents=True, exist_ok=True)

    texto = f"""# PLANO DE AULA

## Tema
{plano['tema']}

## Disciplina
{plano['disciplina']}

## Período
{plano['periodo']}

## Data de geração
{plano['data_geracao']}

## Objetivos de aprendizagem
"""    

    for item in plano["objetivos"]:
        texto += f"- {item}\n"

    texto += "\n## Competências\n"
    for item in plano["competencias"]:
        texto += f"- {item}\n"

    texto += "\n## Habilidades\n"
    for item in plano["habilidades"]:
        texto += f"- {item}\n"

    texto += "\n## Metodologia\n"
    for item in plano["metodologia"]:
        texto += f"- {item}\n"

    texto += "\n## Avaliação\n"
    for item in plano["avaliacao"]:
        texto += f"- {item}\n"

    texto += "\n## Bibliografia\n"
    for item in plano["bibliografia"]:
        texto += f"- {item}\n"

    caminho_saida.write_text(texto, encoding="utf-8")
    return caminho_saida
