from app.ingestao.importar_planos_aula import importar_planos
from app.ingestao.importar_questoes import importar_questoes
from app.question_selector.relacionar_questoes_planos import gerar_relacionamentos
from app.exam_analytics.estatisticas_banco import gerar_estatisticas


def main():
    print("ATHENA QUESTION BANK - PIPELINE COMPLETO")
    print("-" * 60)

    print("1/4 Importando questões...")
    importar_questoes()

    print("2/4 Importando planos de aula...")
    importar_planos()

    print("3/4 Relacionando questões aos planos...")
    gerar_relacionamentos()

    print("4/4 Gerando estatísticas...")
    gerar_estatisticas()

    print("-" * 60)
    print("Pipeline concluído.")


if __name__ == "__main__":
    main()
