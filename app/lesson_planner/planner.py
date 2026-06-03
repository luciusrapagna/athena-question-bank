from app.classificadores.classificador_competencias import classificar
from app.services.gerador_plano_aula import gerar_plano_aula


def gerar_de_texto(texto):

    comp = classificar(texto)

    if not comp:
        return None

    return gerar_plano_aula(
        tema=texto[:60],
        competencias=[comp["competencia"]],
        habilidades=[comp["habilidade"]]
    )
