import os

from assistente import Assistente
from base_conhecimento import BaseConhecimento

PASTA = os.path.dirname(os.path.abspath(__file__))
CAMINHO_BASE = os.path.join(PASTA, "data", "base_conhecimento.json")
CAMINHO_HISTORICO = os.path.join(PASTA, "data", "historico.json")
CAMINHO_CSV = os.path.join(PASTA, "data", "atendimentos.csv")


def mostrar_menu():
    print("\n=== Menu principal ===")
    print("  1. Fazer uma pergunta")
    print("  2. Navegar por categorias")
    print("  3. Ver indicadores")
    print("  4. Exportar atendimentos para CSV")
    print("  0. Sair")


def main():
    print("=" * 60)
    print(" Citizen Assist AI - Transporte público para pessoas idosas")
    print("=" * 60)
    print("Eu respondo dúvidas sobre ônibus, trem, metrô e viagens de ônibus")
    print("entre cidades. Não peço nome, CPF, telefone nem e-mail.")
    print("Aviso: este assistente NÃO é um canal oficial.")

    base = BaseConhecimento(CAMINHO_BASE)
    if not base.carregar():
        print("Não foi possível iniciar o assistente sem a base de conhecimento.")
        return

    assistente = Assistente("Citizen Assist AI", base, CAMINHO_HISTORICO, CAMINHO_CSV)
    try:
        while True:
            mostrar_menu()
            opcao = input("Escolha uma opção: ").strip()
            if opcao == "1":
                assistente.perguntar()
            elif opcao == "2":
                assistente.navegar()
            elif opcao == "3":
                assistente.mostrar_indicadores()
            elif opcao == "4":
                assistente.exportar_csv()
            elif opcao == "0":
                assistente.encerrar()
                return
            else:
                print("Opção inválida. Digite 1, 2, 3, 4 ou 0.")
    except (KeyboardInterrupt, EOFError):
        print("\n\nEncerrando o assistente.")
        assistente.exportar_csv()


if __name__ == "__main__":
    main()
