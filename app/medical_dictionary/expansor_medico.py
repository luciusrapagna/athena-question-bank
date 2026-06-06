import os
import json
import urllib.parse
import urllib.request

from app.medical_dictionary.dicionario_medico_local import DICIONARIO_MEDICO


def normalizar_basico(texto: str) -> str:
    return (texto or "").lower().strip()


def expandir_com_dicionario_local(texto: str) -> str:
    base = normalizar_basico(texto)
    termos = []

    for chave, sinonimos in DICIONARIO_MEDICO.items():
        if chave in base:
            termos.extend(sinonimos)

    return " ".join([texto or "", *termos])


def consultar_merriam_webster_medical(termo: str) -> list[str]:
    """
    Usa a API Medical Dictionary se a variável de ambiente existir:
    MERRIAM_WEBSTER_MEDICAL_KEY
    """
    api_key = os.getenv("MERRIAM_WEBSTER_MEDICAL_KEY")

    if not api_key or not termo:
        return []

    termo_url = urllib.parse.quote(termo)
    url = f"https://www.dictionaryapi.com/api/v3/references/medical/json/{termo_url}?key={api_key}"

    try:
        with urllib.request.urlopen(url, timeout=8) as response:
            data = json.loads(response.read().decode("utf-8"))
    except Exception:
        return []

    termos = []

    if isinstance(data, list):
        for item in data:
            if isinstance(item, dict):
                meta = item.get("meta", {})
                termos.extend(meta.get("stems", []) or [])
                termos.extend(item.get("shortdef", []) or [])
            elif isinstance(item, str):
                termos.append(item)

    return termos[:20]


def expandir_termo_medico(texto: str, usar_api: bool = False) -> str:
    expandido = expandir_com_dicionario_local(texto)

    if usar_api:
        extras = consultar_merriam_webster_medical(texto)
        expandido = " ".join([expandido, *extras])

    return expandido
