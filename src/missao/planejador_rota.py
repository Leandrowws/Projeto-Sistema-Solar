"""
ESTRATEGIA GULOSA (rota): partindo da posicao atual, dentre os corpos
ainda nao visitados, A FRENTE (nunca voltamos, para nao gastar autonomia
em vao) e alcancaveis com um unico tanque cheio (distancia do trecho <=
autonomia), escolhe o proximo destino que maximiza a razao
potencial_cientifico / distancia_do_trecho. Viaja ate la, consome um
tanque, e repete a partir da nova posicao. Para quando nenhum destino
restante e alcancavel com um tanque ou quando os tanques acabam.
"""

import math
from dataclasses import dataclass, field
from typing import List, Optional, Tuple

from src.modelos.corpo_celeste import CorpoCeleste

DENSIDADE_REFERENCIA_KG_M3 = 5514.0   # densidade media da Terra

def calcular_densidade_kg_m3(corpo: CorpoCeleste) -> Optional[float]:
    """Densidade = massa / volume. Retorna None se faltar massa ou raio
    (dado insuficiente para calcular)."""
    if corpo.raio_medio_km <= 0 or corpo.massa_kg <= 0:
        return None
    raio_m = corpo.raio_medio_km * 1000
    volume_m3 = (4 / 3) * math.pi * (raio_m ** 3)
    return corpo.massa_kg / volume_m3

def calcular_potencial_cientifico(corpo: CorpoCeleste) -> Optional[float]:
    """Quanto mais a densidade do corpo se afasta da densidade de
    referencia (para mais ou para menos), maior o potencial cientifico."""
    densidade = calcular_densidade_kg_m3(corpo)
    if densidade is None:
        return None
    return abs(densidade - DENSIDADE_REFERENCIA_KG_M3)

@dataclass
class ParadaCandidata:
    corpo: CorpoCeleste
    densidade_kg_m3: float
    potencial_cientifico: float

@dataclass
class EtapaRota:
    corpo: CorpoCeleste
    distancia_percorrida_km: float   # tamanho deste trecho (desde a parada anterior)
    distancia_do_sol_km: float       # posicao da nave apos esta etapa
    potencial_cientifico: float

@dataclass
class ResultadoRota:
    rota: List[EtapaRota] = field(default_factory=list)
    nao_visitados: List[ParadaCandidata] = field(default_factory=list)
    descartados_sem_dados: List[CorpoCeleste] = field(default_factory=list)
    autonomia_km: float = 0.0
    quantidade_tanques: int = 0
    distancia_total_km: float = 0.0
    potencial_total: float = 0.0


def _construir_candidatos(corpos: List[CorpoCeleste]) -> Tuple[List[ParadaCandidata], List[CorpoCeleste]]:
    candidatos = []
    descartados_sem_dados = []

    for corpo in corpos:
        if corpo.tipo == "Moon":
            continue

        potencial = calcular_potencial_cientifico(corpo)
        if potencial is None:
            descartados_sem_dados.append(corpo)
            continue

        candidatos.append(ParadaCandidata(
            corpo=corpo,
            densidade_kg_m3=calcular_densidade_kg_m3(corpo),
            potencial_cientifico=potencial,
        ))

    # ordena por distancia ao Sol crescente (posicao ao longo da "rota")
    candidatos.sort(key=lambda p: p.corpo.distancia_km)
    return candidatos, descartados_sem_dados

def planejar_rota(corpos: List[CorpoCeleste], autonomia_km: float, quantidade_tanques: int) -> ResultadoRota:
    """ESTRATEGIA GULOSA por potencial cientifico: razao
    potencial_cientifico / distancia_do_trecho, respeitando:
      - autonomia_km: distancia MAXIMA que a nave percorre com um tanque
        cheio antes de ter que parar. Cada trecho e testado isoladamente
        contra esse teto - a autonomia "reseta" a cada parada, nao ha
        orcamento cumulativo.
      - quantidade_tanques: numero maximo de paradas.
    """
    autonomia_km *= 1000000
    candidatos, descartados_sem_dados = _construir_candidatos(corpos)

    posicao_atual_km = 0.0  # o Sol
    visitados = set()
    rota: List[EtapaRota] = []

    while len(rota) < quantidade_tanques:
        melhor_indice = None
        melhor_razao = -1.0
        melhor_distancia_trecho = 0.0

        for i, candidata in enumerate(candidatos):
            if i in visitados:
                continue
            if candidata.corpo.distancia_km <= posicao_atual_km:
                continue  # so avancamos para frente, nunca volta

            distancia_trecho = candidata.corpo.distancia_km - posicao_atual_km
            if distancia_trecho > autonomia_km:
                continue  # distancia maior que autonomia

            razao = candidata.potencial_cientifico / distancia_trecho
            if razao > melhor_razao:
                melhor_razao = razao
                melhor_indice = i
                melhor_distancia_trecho = distancia_trecho

        if melhor_indice is None:
            break  # nenhum candidato alcancavel com um tanque a partir daqui

        escolhida = candidatos[melhor_indice]
        visitados.add(melhor_indice)
        posicao_atual_km = escolhida.corpo.distancia_km

        rota.append(EtapaRota(corpo=escolhida.corpo, distancia_percorrida_km=melhor_distancia_trecho, distancia_do_sol_km=posicao_atual_km, potencial_cientifico=escolhida.potencial_cientifico))

    nao_visitados = [c for i, c in enumerate(candidatos) if i not in visitados]
    distancia_total_km = sum(e.distancia_percorrida_km for e in rota)
    potencial_total = sum(e.potencial_cientifico for e in rota)

    return ResultadoRota(rota=rota, nao_visitados=nao_visitados, descartados_sem_dados=descartados_sem_dados, autonomia_km=autonomia_km, quantidade_tanques=quantidade_tanques, distancia_total_km=distancia_total_km, potencial_total=potencial_total)


def imprimir_resultado(resultado: ResultadoRota) -> None:
    print("\n=== Rota de Missao (Estrategia Gulosa: potencial cientifico | tanques + autonomia) ===")
    print(f"Autonomia por tanque:        {resultado.autonomia_km:,.0f} km")
    print(f"Quantidade de tanques:       {resultado.quantidade_tanques}")
    print(f"Paradas realizadas:          {len(resultado.rota)}")
    print(f"Distancia total percorrida:  {resultado.distancia_total_km:,.0f} km")
    print(f"Potencial cientifico total:  {resultado.potencial_total:,.1f}")

    print("\n--- Rota (em ordem de visita, partindo do Sol) ---")
    if not resultado.rota:
        print("Nenhuma parada realizada.")
    for i, etapa in enumerate(resultado.rota, start=1):
        print(f"  {i}. {etapa.corpo.nome:10s} | trecho={etapa.distancia_percorrida_km:>14,.0f} km | "
              f"posicao={etapa.distancia_do_sol_km:>14,.0f} km | potencial={etapa.potencial_cientifico:8.1f}")

    print("\n--- Nao visitados ---")
    if not resultado.nao_visitados:
        print("Nenhum.")
    for c in resultado.nao_visitados:
        print(f"  {c.corpo.nome} (dist={c.corpo.distancia_km:,.0f} km, potencial={c.potencial_cientifico:.1f})")

    print("\n--- Descartados por falta de dados (sem massa ou raio suficientes) ---")
    if not resultado.descartados_sem_dados:
        print("Nenhum.")
    for c in resultado.descartados_sem_dados:
        print(f"  {c.nome}")