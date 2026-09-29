"""
Modulo de aquisicao de dados: fala com a API "The Solar System OpenData".

IMPORTANTE: a API exige um token. Gere o seu em:
https://api.le-systeme-solaire.net/en/generatekey.html
"""

import json
import os
from typing import List

import requests

from src.modelos.corpo_celeste import CorpoCeleste

BASE_URL = "https://api.le-systeme-solaire.net/rest/bodies"


def obter_token() -> str:
    """Le o token da variavel de ambiente SOLAR_API_KEY."""
    token = os.environ.get("SOLAR_API_KEY")
    if not token:
        raise RuntimeError(
            "Variavel de ambiente SOLAR_API_KEY nao definida. "
            "Gere uma chave gratuita em "
            "https://api.le-systeme-solaire.net/en/generatekey.html "
            "e rode: export SOLAR_API_KEY='seu-token-aqui'"
        )
    return token


def buscar_corpos_da_api(timeout: int = 15) -> List[CorpoCeleste]:
    """Faz a requisicao HTTP real (Nivel 1) e retorna a lista de CorpoCeleste."""
    token = obter_token()
    headers = {"Authorization": f"Bearer {token}"}

    resposta = requests.get(BASE_URL, headers=headers, timeout=timeout)
    resposta.raise_for_status()  # lanca excecao se a API retornar erro

    dados_json = resposta.json()
    corpos_brutos = dados_json.get("bodies", [])

    return [CorpoCeleste.api_dict(item) for item in corpos_brutos]


def carregar_corpos_de_arquivo(caminho_json: str) -> List[CorpoCeleste]:
    """Carrega corpos a partir de um arquivo JSON local"""
    with open(caminho_json, "r", encoding="utf-8") as f:
        dados_json = json.load(f)

    corpos_brutos = dados_json.get("bodies", [])
    return [CorpoCeleste.api_dict(item) for item in corpos_brutos]

