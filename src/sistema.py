"""
Fachada do sistema: junta aquisicao de dados + estrutura de busca + as
operacoes de consulta/filtragem exigidas pelo enunciado (Secao 6).

O main.py (interface de linha de comando) so deve falar com esta classe,
nunca diretamente com TabelaHash ou com o cliente da API.
"""

from typing import List, Optional

from src.missao.planejador_rota import (
    planejar_rota as _executar_planejamento_rota,
    ResultadoRota,
)

from src.api.solar_system_client import (
    buscar_corpos_da_api,
    carregar_corpos_de_arquivo,
)
from src.estruturas.tabela_hash import TabelaHash
from src.modelos.corpo_celeste import CorpoCeleste


class SistemaMissoes:

    def __init__(self, capacidade_inicial_hash: int = 16):
        self._tabela = TabelaHash(capacidade_inicial=capacidade_inicial_hash)

    # ------------------------------------------------------------------
    # Aquisicao de dados
    # ------------------------------------------------------------------
    def carregar_de_arquivo(self, caminho_json: str) -> int:
        corpos = carregar_corpos_de_arquivo(caminho_json)
        for corpo in corpos:
            self._tabela.inserir(corpo.id, corpo)
            #no futuro também vou inserir na Trie
            #no futuro também vou inserir na arvore-B
        return len(corpos)

    def carregar_da_api(self) -> int:
        corpos = buscar_corpos_da_api()
        for corpo in corpos:
            self._tabela.inserir(corpo.id, corpo)
            #no futuro também vou inserir na Trie
            #no futuro também vou inserir na arvore-B
        return len(corpos)

    # ------------------------------------------------------------------
    # Consulta de elementos (busca exata por id, via Tabela Hash)
    # ------------------------------------------------------------------
    def buscar_por_id(self, id_corpo: str) -> Optional[CorpoCeleste]:
        return self._tabela.buscar(id_corpo)

    # ------------------------------------------------------------------
    # Pesquisa por atributos
    # (Busca linear - a Tabela Hash so acelera
    # busca exata por chave, buscas por atributo vou deixar melhor pela Trie/
    # Arvore B na Parte 2)
    # ------------------------------------------------------------------
    def pesquisar_por_nome_parcial(self, trecho: str) -> List[CorpoCeleste]:
        trecho_lower = trecho.lower()
        return [c for c in self._tabela.todos_valores() if c.nome.lower().startswith(trecho_lower)]

    def pesquisar_por_tipo(self, tipo: str) -> List[CorpoCeleste]:
        tipo_lower = tipo.lower()
        return [c for c in self._tabela.todos_valores() if c.tipo.lower() == tipo_lower]

    # ------------------------------------------------------------------
    # Listagem e filtragem
    # ------------------------------------------------------------------
    def listar_todos(self) -> List[CorpoCeleste]:
        return self._tabela.todos_valores()

    def filtrar_por_faixa_distancia(self, minimo_km: float, maximo_km: float) -> List[CorpoCeleste]:
        return [c for c in self._tabela.todos_valores() if minimo_km <= c.distancia_km <= maximo_km]

    def listar_ordenado_por_distancia(self) -> List[CorpoCeleste]:
        return sorted(self._tabela.todos_valores(), key=lambda c: c.distancia_km)

    # ------------------------------------------------------------------
    # Instrumentacao
    # ------------------------------------------------------------------
    def quantidade_corpos(self) -> int:
        return len(self._tabela)

    def imprimir_estatisticas_hash(self) -> None:
        self._tabela.imprimir_estatisticas()

    # ------------------------------------------------------------------
    # Planejamento guloso de rota
    # ------------------------------------------------------------------
    def planejar_rota(self, tanques_combustivel: int, autonomia: float) -> ResultadoRota:
        return _executar_planejamento_rota(self._tabela.todos_valores(), autonomia, tanques_combustivel)