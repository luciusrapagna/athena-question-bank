from app.services.gerador_plano_aula import gerar_plano_aula, salvar_plano_markdown


def main():
    plano = gerar_plano_aula(
        tema="Sepse urinária e choque séptico",
        disciplina="Clínica Médica",
        periodo="Ciclo Clínico",
        competencias=[
            "Raciocínio clínico",
            "Tomada de decisão",
            "Interpretação de sinais de gravidade"
        ],
        habilidades=[
            "Reconhecer sinais de sepse",
            "Interpretar dados clínicos e laboratoriais",
            "Propor conduta inicial baseada em prioridades"
        ]
    )

    caminho = salvar_plano_markdown(
        plano,
        "planos_aula/plano_sepse_urinaria.md"
    )

    print(f"Plano de aula gerado com sucesso: {caminho}")


if __name__ == "__main__":
    main()
