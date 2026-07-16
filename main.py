from lia import Lia

if __name__ == "__main__":
    lia = Lia()

    goal = (
        "Pesquise sobre 'como criar agentes de IA autônomos em Python' "
        "e me dê um resumo curto em 3 linhas."
    )

    resultado = lia.run(goal)
    print(resultado)
