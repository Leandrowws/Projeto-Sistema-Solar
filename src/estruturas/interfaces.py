"""
Interface comum que TODAS as estruturas de busca do sistema devem seguir
"""

from abc import ABC, abstractmethod
from typing import Any, List, Optional


class IEstruturaBusca(ABC):
    """Interface (classe abstrata) para uma estrutura de busca por chave."""

    @abstractmethod
    def inserir(self, chave: str, valor: Any) -> None:
        """Insere ou atualiza o valor associado a uma chave."""
        raise NotImplementedError

    @abstractmethod
    def buscar(self, chave: str) -> Optional[Any]:
        """Retorna o valor associado a chave, ou None se nao existir."""
        raise NotImplementedError

    @abstractmethod
    def remover(self, chave: str) -> bool:
        """Remove a chave da estrutura. Retorna True se removeu, False se
        a chave nao existia."""
        raise NotImplementedError

    @abstractmethod
    def existe(self, chave: str) -> bool:
        """Verifica se uma chave esta presente na estrutura."""
        raise NotImplementedError

    @abstractmethod
    def todos_valores(self) -> List[Any]:
        """Retorna todos os valores armazenados (para listagens/filtragem)."""
        raise NotImplementedError

    @abstractmethod
    def __len__(self) -> int:
        """Quantidade de elementos armazenados."""
        raise NotImplementedError
