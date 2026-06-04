import csv
import re
from pathlib import Path
from app.config_paths import DIR_PLANOS_ENTRADA, BANCO_PLANOS
from app.ingestao.leitor_arquivos import ler_arquivo


def limpar_texto(texto):
    return " ".join(texto.replace("\n", " ").replace("\r", " ").split())


def inferir_area(texto):
    texto_lower = texto.lower()

    mapa = {
        "Saúde Coletiva": ["saúde coletiva", "sus", "epidemiologia", "vigilância", "atenção primária"],
        "Clínica Médica": ["clínica médica", "sepse", "diabetes", "hipertensão", "pneumonia"],
        "Pediatria": ["pediatria", "criança", "recém-nascido", "adolescente"],
        "Ginecologia e Obstetrícia": ["ginecologia", "obstetrícia", "gestante", "pré-natal"],
        "Cirurgia": ["cirurgia", "pré-operatório", "pós-operatório", "abdome agudo"],
    }

    for area, termos in mapa.items():
        for termo in termos:
            if termo in texto_lower:
                return area

    return "Não classificada"


def inferir_aula(nome_arquivo, texto):
    padroes = [
        r"aula\s*0?(\d+)",
        r"encontro\s*0?(\d+)",
        r"dia\s*0?(\d+)",
    ]

    base = nome_arquivo.lower() + " " + texto.lower()

    for padrao in padroes:
        match = re.search(padrao, base)
        if match:
            return f"Aula {match.group(1)}"

    return Path(nome_arquivo).stem


def importar_planos():
    arquivos = (
        list(DIR_PLANOS_ENTRADA.glob("*.txt")) +
        list(DIR_PLANOS_ENTRADA.glob("*.md")) +
        list(DIR_PLANOS_ENTRADA.glob("*.docx")) +
        list(DIR_PLANOS_ENTRADA.glob("*.pdf"))
    )

    registros = []

    for i, arquivo in enumerate(arquivos, start=1):
        texto = ler_arquivo(arquivo)
        texto_limpo = limpar_texto(texto)

        registro = {
            "id_aula": f"AULA{i:04d}",
            "aula": inferir_aula(arquivo.name, texto),
            "data": "",
            "disciplina": "",
            "area": inferir_area(texto),
            "assunto": Path(arquivo.name).stem,
            "objetivos": texto_limpo[:500],
            "conteudos": texto_limpo[:1000],
        }

        registros.append(registro)

    with open(BANCO_PLANOS, "w", encoding="utf-8-sig", newline="") as f:
        campos = ["id_aula", "aula", "data", "disciplina", "area", "assunto", "objetivos", "conteudos"]
        writer = csv.DictWriter(f, fieldnames=campos)
        writer.writeheader()
        writer.writerows(registros)

    print(f"Planos importados: {len(registros)}")
    print(f"Banco gerado em: {BANCO_PLANOS}")


if __name__ == "__main__":
    importar_planos()
