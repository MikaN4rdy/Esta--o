import random


def jogar():
    secreto = random.randint(1, 100)
    tentativas = 0
    print("\nPensei em um número de 1 a 100. Consegue acertar?")

    while True:
        try:
            palpite = int(input("Seu palpite: "))
        except ValueError:
            print("Digite um número válido.")
            continue

        tentativas += 1
        if palpite < secreto:
            print("Maior!")
        elif palpite > secreto:
            print("Menor!")
        else:
            print(f"Acertou em {tentativas} tentativas!")
            return max(0, 100 - tentativas * 8)