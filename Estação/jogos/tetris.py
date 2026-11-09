import pygame
import random
import json
import os
import sys

pygame.init()

# CONFIGURAÇÕES
WIDTH, HEIGHT = 800, 650
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("tetris")

clock = pygame.time.Clock()
FPS = 60

# CORES
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
GRAY = (90, 90, 90)

COLORS = [
    (0, 200, 255),    # Azul claro
    (0, 80, 255),     # Azul
    (255, 140, 0),    # Laranja
    (255, 230, 0),    # Amarelo
    (0, 200, 0),      # Verde
    (160, 0, 200),    # Roxo
    (255, 0, 0)       # Vermelho
]

FONT_BIG = pygame.font.SysFont("arial", 45, bold=True)
FONT_MED = pygame.font.SysFont("arial", 25, bold=True)
FONT_SMALL = pygame.font.SysFont("arial", 18)

# TABULEIRO
COLS = 10
ROWS = 20
CELL = 27

BOARD_X = 265
BOARD_Y = 55

# DIFICULDADES
DIFFICULTIES = {
    "FÁCIL": 800,
    "MÉDIO": 500,
    "DIFÍCIL": 250
}

# RECORDES
RECORD_FILE = os.path.join(
    os.path.dirname(os.path.abspath(__file__)),
    "record.json"
)


def load_record():
    try:
        with open(RECORD_FILE, "r") as f:
            return json.load(f).get("record", 0)
    except (FileNotFoundError, json.JSONDecodeError):
        return 0


def save_record(value):
    try:
        with open(RECORD_FILE, "w") as f:
            json.dump({"record": value}, f)
    except OSError:
        pass


record = load_record()

# FORMATOS DAS PEÇAS
SHAPES = [
    [[1, 1, 1, 1]],
    [[1, 1], [1, 1]],
    [[0, 1, 0], [1, 1, 1]],
    [[1, 0, 0], [1, 1, 1]],
    [[0, 0, 1], [1, 1, 1]],
    [[0, 1, 1], [1, 1, 0]],
    [[1, 1, 0], [0, 1, 1]]
]


class Piece:
    def __init__(self):
        index = random.randrange(len(SHAPES))
        self.shape = [row[:] for row in SHAPES[index]]
        self.color = COLORS[index]
        self.x = 3
        self.y = 0

    def rotate(self):
        self.shape = [
            list(row) for row in zip(*self.shape[::-1])
        ]


class Board:
    def __init__(self):
        self.grid = [
            [None for _ in range(COLS)]
            for _ in range(ROWS)
        ]

    def valid(self, piece, dx=0, dy=0, shape=None):
        shape = shape if shape is not None else piece.shape

        for y, row in enumerate(shape):
            for x, cell in enumerate(row):
                if not cell:
                    continue

                nx = piece.x + x + dx
                ny = piece.y + y + dy

                if nx < 0 or nx >= COLS or ny >= ROWS:
                    return False

                if ny >= 0 and self.grid[ny][nx] is not None:
                    return False

        return True

    def lock(self, piece):
        for y, row in enumerate(piece.shape):
            for x, cell in enumerate(row):
                if cell:
                    ny = piece.y + y
                    nx = piece.x + x
                    if ny >= 0:
                        self.grid[ny][nx] = piece.color

    def clear_lines(self):
        new_grid = [
            row for row in self.grid
            if not all(cell is not None for cell in row)
        ]

        removed = ROWS - len(new_grid)

        for _ in range(removed):
            new_grid.insert(0, [None] * COLS)

        self.grid = new_grid
        return removed

    def draw(self):
        pygame.draw.rect(
            screen, BLACK,
            (BOARD_X, BOARD_Y, COLS * CELL, ROWS * CELL)
        )

        for y in range(ROWS):
            for x in range(COLS):
                rect = pygame.Rect(
                    BOARD_X + x * CELL,
                    BOARD_Y + y * CELL,
                    CELL, CELL
                )

                color = self.grid[y][x]

                if color is not None:
                    pygame.draw.rect(
                        screen, color, rect.inflate(-2, -2)
                    )

                pygame.draw.rect(screen, GRAY, rect, 1)


# VARIÁVEIS
state = "MENU"
difficulty = "MÉDIO"

board = Board()
current = Piece()
next_piece = Piece()

score = 0
level = 1
lines = 0

fall_timer = 0
fall_speed = DIFFICULTIES[difficulty]


# FUNÇÕES DO JOGO
def reset_game():
    global board, current, next_piece
    global score, level, lines, fall_timer
    global fall_speed, state

    board = Board()
    current = Piece()
    next_piece = Piece()

    score = 0
    level = 1
    lines = 0

    fall_timer = 0
    fall_speed = DIFFICULTIES[difficulty]

    state = "PLAYING" if board.valid(current) else "GAME_OVER"


def spawn():
    global current, next_piece, state

    current = next_piece
    next_piece = Piece()

    if not board.valid(current):
        state = "GAME_OVER"


def lock_piece():
    global score, lines, level, fall_speed, record

    board.lock(current)
    removed = board.clear_lines()

    points = {1: 100, 2: 300, 3: 500, 4: 800}

    score += points.get(removed, 0) * level
    lines += removed
    level = lines // 10 + 1

    fall_speed = max(
        70,
        DIFFICULTIES[difficulty] - (level - 1) * 45
    )

    if score > record:
        record = score
        save_record(record)

    spawn()


def move(dx, dy):
    if board.valid(current, dx, dy):
        current.x += dx
        current.y += dy
        return True
    return False


def rotate():
    old_shape = [row[:] for row in current.shape]

    current.rotate()

    if board.valid(current):
        return

    for offset in [-1, 1, -2, 2]:
        if board.valid(current, dx=offset):
            current.x += offset
            return

    current.shape = old_shape


def hard_drop():
    global score

    distance = 0

    while move(0, 1):
        distance += 1

    score += distance * 2
    lock_piece()


# DESENHO
def draw_text(value, font, color, x, y):
    image = font.render(str(value), True, color)
    screen.blit(image, (x, y))


def draw_button(rect, label):
    pygame.draw.rect(screen, GRAY, rect, 2)

    image = FONT_MED.render(label, True, WHITE)

    screen.blit(
        image,
        image.get_rect(center=rect.center)
    )


def draw_buttons(labels, start_y):
    buttons = []

    for i, label in enumerate(labels):
        rect = pygame.Rect(
            270, start_y + i * 70, 260, 50
        )

        draw_button(rect, label)
        buttons.append((rect, label))

    return buttons


def draw_piece(piece):
    for y, row in enumerate(piece.shape):
        for x, cell in enumerate(row):
            if cell:
                rect = pygame.Rect(
                    BOARD_X + (piece.x + x) * CELL + 1,
                    BOARD_Y + (piece.y + y) * CELL + 1,
                    CELL - 2,
                    CELL - 2
                )

                pygame.draw.rect(screen, piece.color, rect)


def draw_next():
    draw_text("PRÓXIMA PEÇA", FONT_SMALL, WHITE, 590, 110)

    for y, row in enumerate(next_piece.shape):
        for x, cell in enumerate(row):
            if cell:
                rect = pygame.Rect(
                    630 + x * 23,
                    145 + y * 23,
                    21, 21
                )

                pygame.draw.rect(screen, next_piece.color, rect)


def draw_game():
    screen.fill(BLACK)

    draw_text("TETRIS", FONT_BIG, WHITE, 345, 5)

    board.draw()
    draw_piece(current)
    draw_next()

    draw_text("PONTOS", FONT_SMALL, WHITE, 590, 270)
    draw_text(score, FONT_MED, WHITE, 590, 295)

    draw_text("RECORDE", FONT_SMALL, WHITE, 590, 345)
    draw_text(record, FONT_MED, WHITE, 590, 370)

    draw_text("NÍVEL", FONT_SMALL, WHITE, 590, 420)
    draw_text(level, FONT_MED, WHITE, 590, 445)

    draw_text("LINHAS", FONT_SMALL, WHITE, 590, 495)
    draw_text(lines, FONT_MED, WHITE, 590, 520)

    controls = [
        "CONTROLES",
        "← → MOVER",
        "↑ GIRAR",
        "↓ DESCER",
        "ESPAÇO QUEDA",
        "P PAUSAR",
        "ESC MENU"
    ]

    for i, item in enumerate(controls):
        draw_text(item, FONT_SMALL, WHITE, 20, 190 + i * 35)


# MENUS
def draw_menu():
    screen.fill(BLACK)

    title = FONT_BIG.render("TETRIS", True, WHITE)
    screen.blit(title, title.get_rect(center=(400, 170)))

    return draw_buttons(
        ["JOGAR", "OPÇÕES", "SAIR"],
        280
    )


def draw_difficulty():
    screen.fill(BLACK)

    title = FONT_BIG.render("DIFICULDADE", True, WHITE)
    screen.blit(title, title.get_rect(center=(400, 150)))

    return draw_buttons(
        ["FÁCIL", "MÉDIO", "DIFÍCIL", "VOLTAR"],
        240
    )


def draw_pause():
    draw_game()

    overlay = pygame.Surface((WIDTH, HEIGHT))
    overlay.set_alpha(190)
    overlay.fill(BLACK)
    screen.blit(overlay, (0, 0))

    title = FONT_BIG.render("PAUSADO", True, WHITE)
    screen.blit(title, title.get_rect(center=(400, 230)))

    return draw_buttons(["CONTINUAR", "MENU"], 350)


def draw_game_over():
    draw_game()

    overlay = pygame.Surface((WIDTH, HEIGHT))
    overlay.set_alpha(190)
    overlay.fill(BLACK)
    screen.blit(overlay, (0, 0))

    title = FONT_BIG.render("GAME OVER", True, WHITE)
    screen.blit(title, title.get_rect(center=(400, 220)))

    draw_text(
        f"PONTUAÇÃO: {score}",
        FONT_MED, WHITE, 310, 285
    )

    return draw_buttons(
        ["JOGAR NOVAMENTE", "MENU"],
        370
    )


# LOOP PRINCIPAL
running = True

while running:
    dt = clock.tick(FPS)

    # Desenhar a tela e atualizar os botões ANTES dos eventos
    buttons = []

    if state == "MENU":
        buttons = draw_menu()

    elif state == "DIFFICULTY":
        buttons = draw_difficulty()

    elif state == "PLAYING":
        draw_game()

    elif state == "PAUSED":
        buttons = draw_pause()

    elif state == "GAME_OVER":
        buttons = draw_game_over()

    # EVENTOS
    for event in pygame.event.get():

        if event.type == pygame.QUIT:
            running = False

        if event.type == pygame.KEYDOWN:

            if state == "PLAYING":

                if event.key == pygame.K_LEFT:
                    move(-1, 0)

                elif event.key == pygame.K_RIGHT:
                    move(1, 0)

                elif event.key == pygame.K_DOWN:
                    if not move(0, 1):
                        lock_piece()

                elif event.key == pygame.K_UP:
                    rotate()

                elif event.key == pygame.K_SPACE:
                    hard_drop()

                elif event.key == pygame.K_p:
                    state = "PAUSED"

                elif event.key == pygame.K_ESCAPE:
                    state = "MENU"

            elif state == "PAUSED":

                if event.key in (pygame.K_p, pygame.K_ESCAPE):
                    state = "PLAYING"

            elif state == "GAME_OVER":

                if event.key == pygame.K_RETURN:
                    reset_game()

                elif event.key == pygame.K_ESCAPE:
                    state = "MENU"

            elif state == "DIFFICULTY":

                if event.key == pygame.K_ESCAPE:
                    state = "MENU"

        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:

            for rect, label in buttons:

                if rect.collidepoint(event.pos):

                    if state == "MENU":

                        if label == "JOGAR":
                            state = "DIFFICULTY"

                        elif label == "OPÇÕES":
                            state = "DIFFICULTY"

                        elif label == "SAIR":
                            running = False

                    elif state == "DIFFICULTY":

                        if label in DIFFICULTIES:
                            difficulty = label
                            reset_game()

                        elif label == "VOLTAR":
                            state = "MENU"

                    elif state == "PAUSED":

                        if label == "CONTINUAR":
                            state = "PLAYING"

                        elif label == "MENU":
                            state = "MENU"

                    elif state == "GAME_OVER":

                        if label == "JOGAR NOVAMENTE":
                            reset_game()

                        elif label == "MENU":
                            state = "MENU"

    # ATUALIZAR QUEDA
    if state == "PLAYING":

        fall_timer += dt

        if fall_timer >= fall_speed:

            fall_timer = 0

            if not move(0, 1):
                lock_piece()

    pygame.display.flip()


pygame.quit()
sys.exit()