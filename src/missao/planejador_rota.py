"""
ESTRATEGIA GULOSA (rota): partindo da posicao atual, dentre os corpos
ainda nao visitados, A FRENTE (nunca voltamos, para nao gastar combustivel
em vao) e alcancaveis com o combustivel restante, escolhe o proximo destino que maximiza a razao
potencial_cientifico / custo_do_passo, onde
    custo_do_passo = distancia_do_trecho + custo_fixo_de_parada.
Viaja ate la, desconta o custo do passo do combustivel e repete a partir
da nova posicao. Como toda parada tem custo fixo, parar em corpos de baixo
potencial deixa de ser gratis. Para quando nenhum destino restante e
alcancavel (custo do passo > combustivel restante) ou o combustivel zera.
"""

import math
from dataclasses import dataclass, field
from typing import List, Optional, Tuple

from src.modelos.corpo_celeste import CorpoCeleste

DENSIDADE_REFERENCIA_KG_M3 = 5514.0   # densidade media da Terra
FATOR_MILHOES_KM = 1_000_000          # entrada do combustivel em milhoes de km

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
    custo_passo_km: float            # trecho + custo fixo de parada
    combustivel_restante_km: float   # combustivel que sobrou apos este passo

@dataclass
class ResultadoRota:
    rota: List[EtapaRota] = field(default_factory=list)
    nao_visitados: List[ParadaCandidata] = field(default_factory=list)
    descartados_sem_dados: List[CorpoCeleste] = field(default_factory=list)
    custo_parada_km: float = 0.0
    combustivel_inicial_km: float = 0.0
    combustivel_restante_km: float = 0.0
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

def planejar_rota(corpos: List[CorpoCeleste], combustivel_milhoes_km: float,
                  custo_parada_milhoes_km: float = 0.0) -> ResultadoRota:
    """ESTRATEGIA GULOSA por potencial cientifico: razao
    potencial_cientifico / custo_do_passo, respeitando:
      - combustivel_milhoes_km: orcamento TOTAL de combustivel, expresso
        como a distancia (em milhoes de km) que a nave consegue percorrer.
      - custo_parada_milhoes_km: combustivel fixo gasto a CADA parada
        (ex: entrar em orbita), na mesma unidade. Faz com que visitar um
        corpo de baixo potencial tenha um custo real.
    Cada passo consome: distancia_do_trecho + custo_parada. A missao termina
    quando o combustivel restante nao cobre o passo ate nenhum corpo.
    """
    combustivel_inicial_km = combustivel_milhoes_km * FATOR_MILHOES_KM
    custo_parada_km = custo_parada_milhoes_km * FATOR_MILHOES_KM
    combustivel_restante_km = combustivel_inicial_km

    candidatos, descartados_sem_dados = _construir_candidatos(corpos)

    posicao_atual_km = 0.0  # o Sol
    visitados = set()
    rota: List[EtapaRota] = []

    while combustivel_restante_km > 0:
        melhor_indice = None
        melhor_razao = -1.0
        melhor_distancia_trecho = 0.0
        melhor_custo_passo = 0.0

        for i, candidata in enumerate(candidatos):
            if i in visitados:
                continue
            if candidata.corpo.distancia_km <= posicao_atual_km:
                continue  # so avancamos para frente, nunca volta

            distancia_trecho = candidata.corpo.distancia_km - posicao_atual_km
            custo_passo = distancia_trecho + custo_parada_km
            if custo_passo > combustivel_restante_km:
                continue  # combustivel restante nao cobre trecho + parada

            razao = candidata.potencial_cientifico / custo_passo
            if razao > melhor_razao:
                melhor_razao = razao
                melhor_indice = i
                melhor_distancia_trecho = distancia_trecho
                melhor_custo_passo = custo_passo

        if melhor_indice is None:
            break  # nenhum candidato alcancavel com o combustivel restante

        escolhida = candidatos[melhor_indice]
        visitados.add(melhor_indice)
        posicao_atual_km = escolhida.corpo.distancia_km
        combustivel_restante_km -= melhor_custo_passo

        rota.append(EtapaRota(
            corpo=escolhida.corpo,
            distancia_percorrida_km=melhor_distancia_trecho,
            distancia_do_sol_km=posicao_atual_km,
            potencial_cientifico=escolhida.potencial_cientifico,
            custo_passo_km=melhor_custo_passo,
            combustivel_restante_km=combustivel_restante_km,
        ))

    nao_visitados = [c for i, c in enumerate(candidatos) if i not in visitados]
    distancia_total_km = sum(e.distancia_percorrida_km for e in rota)
    potencial_total = sum(e.potencial_cientifico for e in rota)

    return ResultadoRota(
        rota=rota,
        nao_visitados=nao_visitados,
        descartados_sem_dados=descartados_sem_dados,
        custo_parada_km=custo_parada_km,
        combustivel_inicial_km=combustivel_inicial_km,
        combustivel_restante_km=combustivel_restante_km,
        distancia_total_km=distancia_total_km,
        potencial_total=potencial_total,
    )


def imprimir_resultado(resultado: ResultadoRota) -> None:
    print("\n=== Rota de Missao (Estrategia Gulosa: potencial cientifico | combustivel) ===")
    print(f"Combustivel inicial:         {resultado.combustivel_inicial_km:,.0f} km")
    print(f"Custo fixo por parada:       {resultado.custo_parada_km:,.0f} km")
    print(f"Combustivel restante:        {resultado.combustivel_restante_km:,.0f} km")
    print(f"Paradas realizadas:          {len(resultado.rota)}")
    print(f"Distancia total percorrida:  {resultado.distancia_total_km:,.0f} km")
    print(f"Potencial cientifico total:  {resultado.potencial_total:,.1f}")

    print("\n--- Rota (em ordem de visita, partindo do Sol) ---")
    if not resultado.rota:
        print("Nenhuma parada realizada.")
    for i, etapa in enumerate(resultado.rota, start=1):
        print(f"  {i}. {etapa.corpo.nome:10s} | trecho={etapa.distancia_percorrida_km:>14,.0f} km | "
              f"posicao={etapa.distancia_do_sol_km:>14,.0f} km | potencial={etapa.potencial_cientifico:8.1f} | "
              f"custo passo={etapa.custo_passo_km:>14,.0f} km | "
              f"combustivel restante={etapa.combustivel_restante_km:>14,.0f} km")

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
