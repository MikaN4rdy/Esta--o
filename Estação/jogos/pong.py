import random
import pygame

LARGURA, ALTURA = 700, 450


def jogar():
    pygame.init()
    tela = pygame.display.set_mode((LARGURA, ALTURA))
    pygame.display.set_caption("Pong")
    relogio = pygame.time.Clock()
    fonte = pygame.font.SysFont(None, 36)

    jogador = pygame.Rect(20, ALTURA // 2 - 40, 10, 80)
    cpu = pygame.Rect(LARGURA - 30, ALTURA // 2 - 40, 10, 80)
    bola = pygame.Rect(LARGURA // 2 - 8, ALTURA // 2 - 8, 16, 16)
    vx, vy = 5, random.choice([-4, 4])
    pontos, vidas = 0, 3

    while vidas > 0:
        for e in pygame.event.get():
            if e.type == pygame.QUIT:
                pygame.quit()
                return pontos

        teclas = pygame.key.get_pressed()
        if teclas[pygame.K_UP]:
            jogador.y -= 7
        if teclas[pygame.K_DOWN]:
            jogador.y += 7
        jogador.clamp_ip(tela.get_rect())

        if cpu.centery < bola.centery:
            cpu.y += 4
        elif cpu.centery > bola.centery:
            cpu.y -= 4
        cpu.clamp_ip(tela.get_rect())

        bola.x += vx
        bola.y += vy
        if bola.top <= 0 or bola.bottom >= ALTURA:
            vy = -vy

        if bola.colliderect(jogador) and vx < 0:
            vx = min(abs(vx) + 1, 25)
            pontos += 1
        if bola.colliderect(cpu) and vx > 0:
            vx = -vx

        if bola.left <= 0:          # jogador errou
            vidas -= 1
            bola.center = (LARGURA // 2, ALTURA // 2)
            vx, vy = 5, random.choice([-4, 4])
        elif bola.right >= LARGURA:  # CPU errou
            pontos += 5
            bola.center = (LARGURA // 2, ALTURA // 2)
            vx, vy = -5, random.choice([-4, 4])

        tela.fill((15, 15, 30))
        pygame.draw.rect(tela, (255, 255, 255), jogador)
        pygame.draw.rect(tela, (255, 255, 255), cpu)
        pygame.draw.ellipse(tela, (255, 220, 0), bola)
        texto = fonte.render(f"Pontos: {pontos}   Vidas: {vidas}", True, (255, 255, 255))
        tela.blit(texto, (LARGURA // 2 - texto.get_width() // 2, 10))
        pygame.display.flip()
        relogio.tick(60)

    pygame.quit()
    return pontos