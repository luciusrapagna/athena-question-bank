from app.config_paths import (
    DIR_PROVAS_ENTRADA,
    DIR_PLANOS_ENTRADA,
    BANCO_QUESTOES,
    BANCO_PLANOS,
    BANCO_RELACIONAMENTOS,
    DIR_WORD,
    DIR_RELATORIOS,
    DIR_SIMULADOS,
)


def main():
    caminhos = [
        DIR_PROVAS_ENTRADA,
        DIR_PLANOS_ENTRADA,
        BANCO_QUESTOES,
        BANCO_PLANOS,
        BANCO_RELACIONAMENTOS,
        DIR_WORD,
        DIR_RELATORIOS,
        DIR_SIMULADOS,
    ]

    print("VALIDAÇÃO DA ESTRUTURA ATHENA QUESTION BANK")
    print("-" * 60)

    for caminho in caminhos:
        status = "OK" if caminho.exists() else "NÃO ENCONTRADO"
        print(f"{status}: {caminho}")


if __name__ == "__main__":
    main()
