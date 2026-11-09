import random
import pygame

LARGURA, ALTURA, T = 600, 400, 20


def nova_comida(cobra):
    while True:
        pos = (random.randrange(0, LARGURA, T), random.randrange(0, ALTURA, T))
        if pos not in cobra:
            return pos


def jogar():
    pygame.init()
    tela = pygame.display.set_mode((LARGURA, ALTURA))
    pygame.display.set_caption("Snake")
    relogio = pygame.time.Clock()

    cobra = [(300, 200)]
    direcao = (T, 0)
    comida = nova_comida(cobra)
    pontos = 0

    while True:
        for e in pygame.event.get():
            if e.type == pygame.QUIT:
                pygame.quit()
                return pontos
            if e.type == pygame.KEYDOWN:
                if e.key == pygame.K_UP and direcao != (0, T):
                    direcao = (0, -T)
                elif e.key == pygame.K_DOWN and direcao != (0, -T):
                    direcao = (0, T)
                elif e.key == pygame.K_LEFT and direcao != (T, 0):
                    direcao = (-T, 0)
                elif e.key == pygame.K_RIGHT and direcao != (-T, 0):
                    direcao = (T, 0)

        cabeca = (cobra[0][0] + direcao[0], cobra[0][1] + direcao[1])
        bateu_parede = not (0 <= cabeca[0] < LARGURA and 0 <= cabeca[1] < ALTURA)
        if bateu_parede or cabeca in cobra:
            break

        cobra.insert(0, cabeca)
        if cabeca == comida:
            pontos += 10
            comida = nova_comida(cobra)
        else:
            cobra.pop()

        tela.fill((20, 20, 20))
        pygame.draw.rect(tela, (220, 50, 50), (*comida, T, T))
        for parte in cobra:
            pygame.draw.rect(tela, (50, 220, 90), (*parte, T - 2, T - 2))
        pygame.display.flip()
        relogio.tick(10 + pontos // 50)  # acelera aos poucos

    pygame.quit()
    return pontos