from pathlib import Path

BASE_DIR = Path(".")

DIR_PROVAS_ENTRADA = BASE_DIR / "data" / "entrada" / "provas"
DIR_PLANOS_ENTRADA = BASE_DIR / "data" / "entrada" / "planos_aula"

BANCO_QUESTOES = BASE_DIR / "data" / "banco_questoes" / "banco_questoes.csv"
BANCO_PLANOS = BASE_DIR / "data" / "banco_planos" / "banco_planos_aula.csv"
BANCO_RELACIONAMENTOS = BASE_DIR / "data" / "banco_relacionamentos" / "questoes_planos.csv"

DIR_WORD = BASE_DIR / "outputs" / "word"
DIR_RELATORIOS = BASE_DIR / "outputs" / "relatorios"
DIR_SIMULADOS = BASE_DIR / "outputs" / "simulados"
