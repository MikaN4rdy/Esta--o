import random

OPCOES = {"1": "Pedra", "2": "Papel", "3": "Tesoura"}
VENCE = {"Pedra": "Tesoura", "Papel": "Pedra", "Tesoura": "Papel"}


def jogar():
    sequencia = 0
    print("\nQuantas vitórias seguidas você consegue? Perdeu, acabou!")

    while True:
        print("\n[1] Pedra  [2] Papel  [3] Tesoura")
        escolha = input("Sua jogada: ").strip()
        if escolha not in OPCOES:
            print("Opção inválida.")
            continue

        jogador = OPCOES[escolha]
        computador = random.choice(list(OPCOES.values()))
        print(f"Você: {jogador} | Computador: {computador}")

        if jogador == computador:
            print("Empate!")
        elif VENCE[jogador] == computador:
            sequencia += 1
            print(f"Você venceu! Sequência: {sequencia}")
        else:
            print("Você perdeu!")
            return sequencia