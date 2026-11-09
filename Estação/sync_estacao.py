import csv
import subprocess
import sys
import time
import db

ESTACAO = sys.argv[1] if len(sys.argv) > 1 else "1"
PASTA_REPO = "ranking-repo"
NOME_CSV = f"ranking_estacao{ESTACAO}.csv"
ARQUIVO = f"{PASTA_REPO}/{NOME_CSV}"
INTERVALO = 15  # segundos


def git(*args):
    return subprocess.run(
        ["git", "-C", PASTA_REPO, *args],
        capture_output=True, text=True, timeout=35,
    )


def exportar():
    conn = db.conectar()
    try:
        cur = conn.cursor()
        cur.execute("""
            SELECT j.nome, j.escola, g.nome, p.pontos
            FROM pontuacoes p
            JOIN jogadores j ON j.id = p.jogador_id
            JOIN jogos g ON g.id = p.jogo_id
            ORDER BY p.id
        """)
        dados = cur.fetchall()
    finally:
        conn.close()

    with open(ARQUIVO, "w", newline="", encoding="utf-8") as f:
        escritor = csv.writer(f)
        escritor.writerow(["nome", "escola", "jogo", "pontos"])
        escritor.writerows(dados)


def erro_git(resultado):
    return (resultado.stderr.strip() or resultado.stdout.strip())[:150]

def enviar():
    r = git("add", NOME_CSV)
    if r.returncode != 0:
        return "falha no add: " + erro_git(r)

    houve_commit = False
    if git("diff", "--cached", "--quiet").returncode != 0:
        r = git("commit", "-m", f"estacao {ESTACAO}")
        if r.returncode != 0:
            return "falha no commit: " + erro_git(r)
        houve_commit = True

    r = git("pull", "--rebase")
    if r.returncode != 0:
        git("rebase", "--abort")
        return "falha ao baixar novidades: " + erro_git(r)

    r = git("push")
    if r.returncode != 0:
        return "falha no envio: " + erro_git(r)

    return "enviado com novo commit" if houve_commit else "sem mudanças para enviar"


def main():
    print(f"Sincronizando a estação {ESTACAO} a cada {INTERVALO}s. Ctrl+C para parar.")
    while True:
        try:
            exportar()
            print(time.strftime("%H:%M:%S"), "-", enviar())
        except Exception as erro:
            print(time.strftime("%H:%M:%S"), "- erro:", erro)
        time.sleep(INTERVALO)


if __name__ == "__main__":
    main()