"""
Tabela Hash implementada do zero (encadeamento externo),
com instrumentacao obrigatoria: contagem de colisoes e fator de carga.

"""

from typing import Any, List, Optional, Tuple

from src.estruturas.interfaces import IEstruturaBusca


class TabelaHash(IEstruturaBusca):

    def __init__(self, capacidade_inicial: int = 8, fator_carga_maximo: float = 0.7):
        self._capacidade = capacidade_inicial
        self._buckets: List[List[Tuple[str, Any]]] = [[] for _ in range(capacidade_inicial)]
        self._quantidade_elementos = 0
        self._fator_carga_maximo = fator_carga_maximo

        # --- metricas de instrumentacao (exigidas pelo enunciado) ---
        self._total_colisoes = 0
        self._total_redimensionamentos = 0

    # ------------------------------------------------------------------
    # Funcao de hash propria:
    #     h = h*31 + valor_do_caractere, aplicando modulo a cada passo.
    # ------------------------------------------------------------------
    def _hash(self, chave: str) -> int:
        h = 0
        for caractere in chave:
            h = (h * 31 + ord(caractere)) % self._capacidade
        return h

    # ---------------------------------------------------------------
    # DADOS da Hash
    # ---------------------------------------------------------------
    @property
    def capacidade(self) -> int:    
        return self._capacidade
    @property
    def fator_carga(self) -> float:
        return self._quantidade_elementos / self._capacidade
    @property
    def total_colisoes(self) -> int:
        return self._total_colisoes
    @property
    def total_redimensionamentos(self) -> int:
        return self._total_redimensionamentos
    # ------------------------------------------------------------------
    # Operações da interface
    # ------------------------------------------------------------------
    def inserir(self, chave: str, valor: Any) -> None:
        indice = self._hash(chave)
        bucket = self._buckets[indice]

        # se a chave ja existe, apenas atualiza (nao conta como colisao nem
        # aumenta a quantidade de elementos)
        for i, (k, _) in enumerate(bucket):
            if k == chave:
                bucket[i] = (chave, valor)
                return

        # se o bucket ja tinha algo, isso e uma colisao de hash de verdade
        if len(bucket) > 0:
            self._total_colisoes += 1

        bucket.append((chave, valor))
        self._quantidade_elementos += 1

        if self.fator_carga > self._fator_carga_maximo:
            self._redimensionar()

    def buscar(self, chave: str) -> Optional[Any]:
        indice = self._hash(chave)
        bucket = self._buckets[indice]
        for k, v in bucket:
            if k == chave:
                return v
        return None

    def existe(self, chave: str) -> bool:
        return self.buscar(chave) is not None

    def remover(self, chave: str) -> bool:
        indice = self._hash(chave)
        bucket = self._buckets[indice]
        for i, (k, _) in enumerate(bucket):
            if k == chave:
                del bucket[i]
                self._quantidade_elementos -= 1
                return True
        return False

    def todos_valores(self) -> List[Any]:
        return [valor for bucket in self._buckets for (_, valor) in bucket]

    def __len__(self) -> int:
        return self._quantidade_elementos

    # ------------------------------------------------------------------
    # Redimensionamento dinamico (rehashing)
    # ------------------------------------------------------------------
    def _redimensionar(self) -> None:
        """Dobra a capacidade da tabela e reinsere todos os elementos."""
        buckets_antigos = self._buckets

        self._capacidade *= 2
        self._buckets = [[] for _ in range(self._capacidade)]
        self._quantidade_elementos = 0
        self._total_redimensionamentos += 1

        for bucket in buckets_antigos:
            for chave, valor in bucket:
                indice = self._hash(chave)
                novo_bucket = self._buckets[indice]
                if len(novo_bucket) > 0:
                    self._total_colisoes += 1
                novo_bucket.append((chave, valor))
                self._quantidade_elementos += 1

    # ------------------------------------------------------------------
    # Instrumentacao: impressao das metricas exigidas pelo enunciado
    # ------------------------------------------------------------------
    def imprimir_estatisticas(self) -> None:
        print("--- Estatisticas da Tabela Hash ---")
        print(f"Capacidade atual:            {self._capacidade}")
        print(f"Elementos armazenados:       {self._quantidade_elementos}")
        print(f"Fator de carga atual:        {self.fator_carga:.3f}")
        print(f"Total de colisoes:           {self._total_colisoes}")
        print(f"Total de redimensionamentos: {self._total_redimensionamentos}")

