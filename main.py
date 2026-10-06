"""
Ponto de entrada do Sistema de Gerenciamento e Planejamento de Missoes
Espaciais. Menu de linha de comando simples. toda a logica de verdade
fica em src/sistema.py (SistemaMissoes).
"""

from src.sistema import SistemaMissoes
from src.missao.planejador_rota import imprimir_resultado

CAMINHO_PADRAO_DADOS = "dados/exemplo_bodies.json"


def exibir_menu() -> None:
    print("\n" + "=" * 55)
    print("  SISTEMA DE PLANEJAMENTO DE MISSOES ESPACIAIS")
    print("=" * 55)
    print(" 1  - Carregar dados de arquivo local (.json)")
    print(" 2  - Carregar dados da API (requer SOLAR_API_KEY)")
    print(" 3  - Buscar corpo por ID")
    print(" 4  - Pesquisar por nome (trecho)")
    print(" 5  - Pesquisar por tipo (Planet, Moon, Dwarf Planet, ...)")
    print(" 6  - Listar todos os corpos carregados")
    print(" 7  - Filtrar por faixa de distancia (km)")
    print(" 8  - Listar ordenado por distancia")
    print(" 9  - Ver estatisticas da Tabela Hash (colisoes / fator de carga)")
    print(" 10 - Planejar missao (algoritmo guloso)")
    print(" 0  - Sair")
    print("=" * 55)


def imprimir_lista(corpos) -> None:
    if not corpos:
        print("Nenhum resultado encontrado.")
        return
    for corpo in corpos:
        print(f"  {corpo}")
    print(f"Total: {len(corpos)}")


def main() -> None:
    sistema = SistemaMissoes()

    while True:
        exibir_menu()
        opcao = input("Escolha uma opcao: ").strip()

        if opcao == "1":
            caminho = input(f"Caminho do arquivo [{CAMINHO_PADRAO_DADOS}]: ").strip()
            caminho = caminho or CAMINHO_PADRAO_DADOS
            try:
                qtd = sistema.carregar_de_arquivo(caminho)
                print(f"OK: {qtd} corpos carregados de '{caminho}'.")
            except FileNotFoundError:
                print(f"Erro: arquivo '{caminho}' nao encontrado.")

        elif opcao == "2":
            try:
                qtd = sistema.carregar_da_api()
                print(f"OK: {qtd} corpos carregados da API.")
            except RuntimeError as e:
                print(f"Erro: {e}")
            except Exception as e:
                print(f"Erro ao consultar a API: {e}")

        elif opcao == "3":
            id_corpo = input("ID do corpo (ex: terre, mars): ").strip()
            corpo = sistema.buscar_por_id(id_corpo)
            print(corpo if corpo else "Corpo nao encontrado.")

        elif opcao == "4":
            trecho = input("Trecho do nome: ").strip()
            imprimir_lista(sistema.pesquisar_por_nome_parcial(trecho))

        elif opcao == "5":
            tipo = input("Tipo: ").strip()
            imprimir_lista(sistema.pesquisar_por_tipo(tipo))

        elif opcao == "6":
            imprimir_lista(sistema.listar_todos())

        elif opcao == "7":
            try:
                minimo = float(input("Distancia minima (km): ").strip())
                maximo = float(input("Distancia maxima (km): ").strip())
                imprimir_lista(sistema.filtrar_por_faixa_distancia(minimo, maximo))
            except ValueError:
                print("Erro: informe numeros validos.")

        elif opcao == "8":
            imprimir_lista(sistema.listar_ordenado_por_distancia())

        elif opcao == "9":
            print(f"Quantidade de corpos carregados: {sistema.quantidade_corpos()}")
            sistema.imprimir_estatisticas_hash()

        elif opcao == "10":
            try:
                combustivel = float(input("Combustivel total da nave (em milhoes de km): ").strip())
                custo_parada = float(input("Custo fixo de combustivel por parada (em milhoes de km): ").strip())
                if combustivel <= 0 or custo_parada < 0:
                    print("Erro: combustivel deve ser > 0 e custo de parada >= 0.")
                    continue
                resultado = sistema.planejar_rota(combustivel, custo_parada)
                imprimir_resultado(resultado)
            except ValueError:
                print("Erro: informe um numero valido.")

        elif opcao == "0":
            print("Encerrando o sistema.")
            break

        else:
            print("Opcao invalida.")


if __name__ == "__main__":
    main()
