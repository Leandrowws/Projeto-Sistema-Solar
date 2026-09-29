"""
Modelo de dados para um corpo celeste do Sistema Solar.

Representa a forma JA PROCESSADA de um item vindo da API "The Solar System
OpenData" (https://api.le-systeme-solaire.net/rest/bodies). O papel desta
classe e isolar o resto do sistema do formato bruto retornado pela API --
se a API mudar um nome de campo amanha, so este arquivo precisa mudar.
"""

from dataclasses import dataclass, field
from typing import Optional


@dataclass
class CorpoCeleste:
    id: str                       # identificador usado pela API (ex: "terre", "mars")
    nome: str                     # nome em ingles (mais universal para o relatorio)
    tipo: str                     # bodyType: Star, Planet, Dwarf Planet, Asteroid, Comet, Moon
    e_planeta: bool               # isPlanet

    distancia_km: float           # semimajorAxis: distancia media ao corpo central (km)
    massa_kg: float                # massValue * 10^massExponent, ja calculado
    gravidade: float              # gravity: gravidade superficial (m/s^2)
    raio_medio_km: float          # meanRadius (km)
    temperatura_media_k: float    # avgTemp (Kelvin)
    quantidade_luas: int          # len(moons) se existir, senao 0

    descoberto_por: Optional[str] = None
    data_descoberta: Optional[str] = None

    @staticmethod
    def api_dict(dados: dict) -> "CorpoCeleste":
        """Constroi um CorpoCeleste a partir do dicionario bruto retornado
        pela API (ou pelo arquivo JSON salvo localmente, no caso do Nivel 2)."""

        massa_info = dados.get("mass") or {}
        massa_kg = 0.0
        if massa_info.get("massValue") is not None:
            massa_kg = massa_info["massValue"] * (10 ** massa_info.get("massExponent", 0))

        luas = dados.get("moons")
        quantidade_luas = len(luas) if luas else 0

        return CorpoCeleste(
            id=dados.get("id", ""),
            nome=dados.get("englishName") or dados.get("name", "Desconhecido"),
            tipo=dados.get("bodyType", "Desconhecido"),
            e_planeta=bool(dados.get("isPlanet", False)),
            distancia_km=float(dados.get("semimajorAxis") or 0),
            massa_kg=massa_kg,
            gravidade=float(dados.get("gravity") or 0),
            raio_medio_km=float(dados.get("meanRadius") or 0),
            temperatura_media_k=float(dados.get("avgTemp") or 0),
            quantidade_luas=quantidade_luas,
            descoberto_por=dados.get("discoveredBy") or None,
            data_descoberta=dados.get("discoveryDate") or None,
        )

    def __str__(self) -> str:
        return (f"{self.nome} ({self.tipo}) | dist={self.distancia_km:,.0f} km | "
                f"massa={self.massa_kg:.3e} kg | gravidade={self.gravidade} m/s^2 | "
                f"luas={self.quantidade_luas} | id={self.id}")
                
