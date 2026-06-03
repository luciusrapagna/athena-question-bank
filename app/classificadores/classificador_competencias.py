from app.services.competencias_service import buscar_por_codigo

PALAVRAS_CHAVE = {
    "sepse": "CM001",
    "choque": "CM001",
    "hipotensao": "CM001",
    "lactato": "CM001",
    "diagnostico": "CM002",
    "tratamento": "CM002",
    "conduta": "CM002",
    "risco": "CM003",
    "seguranca": "CM003",
    "erro medico": "CM003",
    "etica": "ET001",
    "bioetica": "ET001",
    "epidemiologia": "SC002",
    "incidencia": "SC002",
    "prevalencia": "SC002",
    "crianca": "PED001",
    "pediatria": "PED001",
    "gestante": "GO001",
    "obstetricia": "GO001",
    "cirurgia": "CIR001"
}


def classificar(texto):
    texto = texto.lower()

    for palavra, codigo in PALAVRAS_CHAVE.items():
        if palavra in texto:
            return buscar_por_codigo(codigo)

    return None
