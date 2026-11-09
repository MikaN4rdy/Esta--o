import mysql.connector
from mysql.connector import Error

CONFIG = {
    "host": "localhost",
    "user": "root",
    "password": "SUA_SENHA",
    "port": 3306
}

NOME_BANCO = "arcade"

JOGOS = ["Adivinhação", "Jokenpô", "Snake", "Pong", "Tetris"]
def conectar():
    return mysql.connector.connect(database=NOME_BANCO, **CONFIG)


def testar_conexao():
    try:
        conn = mysql.connector.connect(**CONFIG)
        conn.close()
        return True
    except Error as erro:
        print(f"Não foi possível conectar ao MySQL: {erro}")
        print("Verifique se o servidor está ligado e se usuário e senha estão corretos.")
        return False


def criar_estrutura():
    conn = mysql.connector.connect(**CONFIG)
    try:
        cur = conn.cursor()
        cur.execute(f"CREATE DATABASE IF NOT EXISTS {NOME_BANCO}")
        cur.execute(f"USE {NOME_BANCO}")
        cur.execute("""
            CREATE TABLE IF NOT EXISTS jogadores (
                id INT AUTO_INCREMENT PRIMARY KEY,
                nome VARCHAR(80) NOT NULL,
                escola VARCHAR(80) NOT NULL
            )""")
        cur.execute("""
            CREATE TABLE IF NOT EXISTS jogos (
                id INT AUTO_INCREMENT PRIMARY KEY,
                nome VARCHAR(40) NOT NULL UNIQUE
            )""")
        cur.execute("""
            CREATE TABLE IF NOT EXISTS pontuacoes (
                id INT AUTO_INCREMENT PRIMARY KEY,
                jogador_id INT NOT NULL,
                jogo_id INT NOT NULL,
                pontos INT NOT NULL,
                data TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (jogador_id) REFERENCES jogadores(id),
                FOREIGN KEY (jogo_id) REFERENCES jogos(id)
            )""")
        for j in JOGOS:
            cur.execute("INSERT IGNORE INTO jogos (nome) VALUES (%s)", (j,))
        conn.commit()
    finally:
        conn.close()


def cadastrar_jogador(nome, escola):
    conn = conectar()
    try:
        cur = conn.cursor()
        cur.execute("INSERT INTO jogadores (nome, escola) VALUES (%s, %s)", (nome, escola))
        conn.commit()
        return cur.lastrowid
    finally:
        conn.close()


def salvar_pontuacao(jogador_id, jogo, pontos):
    conn = conectar()
    try:
        cur = conn.cursor()
        cur.execute("""
            INSERT INTO pontuacoes (jogador_id, jogo_id, pontos)
            SELECT %s, id, %s FROM jogos WHERE nome = %s
        """, (jogador_id, pontos, jogo))
        conn.commit()
    finally:
        conn.close()


def top6(jogo):
    conn = conectar()
    try:
        cur = conn.cursor()
        cur.execute("""
            SELECT j.nome, j.escola, p.pontos
            FROM pontuacoes p
            JOIN jogadores j ON j.id = p.jogador_id
            JOIN jogos g ON g.id = p.jogo_id
            WHERE g.nome = %s
            ORDER BY p.pontos DESC, p.data ASC
            LIMIT 6
        """, (jogo,))
        return cur.fetchall()
    finally:
        conn.close()



