"""Rich terminal UI for the bedtime story agent."""

from __future__ import annotations

from rich.console import Console
from rich.panel import Panel
from rich.prompt import Prompt
from rich.text import Text

from story_agent.judge import format_judge_line, screen_request
from story_agent.orchestrator import generate_with_judge_loop

console = Console()


def _show_request_rejected(request: str, judgement: dict) -> None:
    console.print()
    console.print(
        Panel(
            Text(
                "We can't tell that as a bedtime story — it asks for things "
                "that aren't gentle or safe for ages 5–10.\n\n"
                f"{judgement.get('feedback') or ''}"
            ),
            title="[bold red]Request blocked[/]",
            border_style="red",
            padding=(1, 2),
        )
    )
    console.print(
        Panel(
            format_judge_line(judgement),
            title="[bold magenta]Judge[/]",
            border_style="magenta",
            padding=(0, 2),
        )
    )
    console.print()


def main() -> None:
    console.print()
    request = Prompt.ask("[bold blue]Ask for your story[/]").strip()
    if not request:
        console.print("[yellow]No request given — ending. Goodnight![/]")
        return

    console.print()
    console.print(
        Panel(
            request,
            title="[bold blue]Your ask[/]",
            border_style="blue",
            padding=(1, 2),
        )
    )

    with console.status("[bold magenta]Checking ask…[/]", spinner="moon"):
        gate = screen_request(request)
    if not gate.get("overall_pass"):
        _show_request_rejected(request, gate)
        return

    feedback = None
    while True:
        console.print()
        # Revisions can re-introduce unsafe asks — screen those too.
        if feedback:
            with console.status(
                "[bold magenta]Checking revision…[/]", spinner="moon"
            ):
                rev_gate = screen_request(f"{request}\nRevision: {feedback}")
            if not rev_gate.get("overall_pass"):
                _show_request_rejected(feedback, rev_gate)
                feedback = Prompt.ask(
                    "[bold yellow]Want any changes?[/] "
                    "[dim](describe them, or press Enter to finish)[/]",
                    default="",
                ).strip()
                if not feedback:
                    console.print()
                    console.print(
                        Panel.fit(
                            "[bold]Enjoy your story! Goodnight.[/] 🌙",
                            border_style="cyan",
                        )
                    )
                    console.print()
                    return
                console.print()
                console.print(
                    Panel(
                        feedback,
                        title="[bold yellow]Your revision[/]",
                        border_style="yellow",
                        padding=(1, 2),
                    )
                )
                continue

        story, judgement = generate_with_judge_loop(request, feedback=feedback)

        console.print()
        console.print(
            Panel(
                Text(story),
                title="[bold green]Bedtime story[/]",
                border_style="green",
                padding=(1, 2),
            )
        )
        console.print(
            Panel(
                format_judge_line(judgement),
                title="[bold magenta]Judge[/]",
                border_style="magenta",
                padding=(0, 2),
            )
        )
        console.print()

        feedback = Prompt.ask(
            "[bold yellow]Want any changes?[/] "
            "[dim](describe them, or press Enter to finish)[/]",
            default="",
        ).strip()
        if not feedback:
            console.print()
            console.print(
                Panel.fit(
                    "[bold]Enjoy your story! Goodnight.[/] 🌙",
                    border_style="cyan",
                )
            )
            console.print()
            break

        console.print()
        console.print(
            Panel(
                feedback,
                title="[bold yellow]Your revision[/]",
                border_style="yellow",
                padding=(1, 2),
            )
        )
