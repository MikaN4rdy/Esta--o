from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.align import Align

import db
from jogos import tetris, adivinhacao, jokenpo, snake, pong

console = Console()

JOGOS = {
    "1": ("Adivinhação", adivinhacao),
    "2": ("Jokenpô", jokenpo),
    "3": ("Snake", snake),
    "4": ("Pong", pong),
    "5": ("Tetris", tetris)
}


def novo_jogador():
    console.clear()
    console.print(Align.center(Panel("[bold cyan]ARCADE SENAI[/bold cyan]\nVamos começar!", expand=False)))
    nome = input("Seu nome: ").strip()
    escola = input("Sua escola: ").strip()
    return db.cadastrar_jogador(nome, escola), nome


def mostrar_ranking():
    for nome_jogo in db.JOGOS:
        tabela = Table(title=f"Top 5 - {nome_jogo}")
        tabela.add_column("#", justify="right")
        tabela.add_column("Jogador")
        tabela.add_column("Escola")
        tabela.add_column("Pontos", justify="right")
        for pos, (nome, escola, pontos) in enumerate(db.top5(nome_jogo), start=1):
            tabela.add_row(str(pos), nome, escola, str(pontos))
        console.print(tabela)
    input("\nEnter para voltar ao menu...")


def main():
    db.criar_estrutura()
    jogador_id, nome = novo_jogador()

    while True:
        console.clear()
        console.print(Panel(f"[bold]Jogador:[/bold] {nome}", expand=False))
        console.print("[1] Adivinhação\n[2] Jokenpô\n[3] Snake\n[4] Pong")
        console.print("[5] Ranking\n[6] Trocar de jogador\n[0] Sair do Programa\n")
        opcao = input("Escolha: ").strip()

        if opcao in JOGOS:
            nome_jogo, modulo = JOGOS[opcao]
            pontos = modulo.jogar()
            db.salvar_pontuacao(jogador_id, nome_jogo, pontos)
            console.print(f"\n[bold green]Você fez {pontos} pontos![/bold green]")
            input("Enter para continuar...")
        elif opcao == "5":
            mostrar_ranking()
        elif opcao == "6":
            jogador_id, nome = novo_jogador()
        elif opcao == "0":
            console.print("Obrigado por jogar!")
            break
        else:
            console.print("[red]Opção inválida. Tente novamente.[/red]")
            input("Enter para continuar...")


if __name__ == "__main__":
    main()