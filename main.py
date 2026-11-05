from graph.debate_graph import debate_app
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich import box
import json

console = Console()

PERSONA_ICONS = {
    "pessimist":    "🔴 Pessimist",
    "lawyer":       "⚖️  Lawyer",
    "competitor":   "🏴‍☠️ Competitor",
    "user_voice":   "👤 User Voice",
    "data_skeptic": "📊 Data Skeptic"
}

def display_results(result: dict):
    console.print("\n")
    console.print(Panel("⚔️  DEVIL'S ADVOCATE — DEBATE COMPLETE", style="bold red"))
    for persona, data in result["attacks"].items():
        if not isinstance(data, dict):
            continue
        severity = data.get("severity", "?")
        color = "red" if severity >= 7 else "yellow" if severity >= 4 else "green"
        table = Table(
            title=f"{PERSONA_ICONS.get(persona, persona)}  |  Severity: {severity}/10",
            box=box.ROUNDED, border_style=color
        )
        table.add_column("Objection", style="white", no_wrap=False)
        for obj in data.get("objections", []):
            table.add_row(f"• {obj}")
        table.add_row(f"\n💀 Killer Blow: {data.get('killer_blow', 'N/A')}", style="bold red")
        console.print(table)
        console.print()

    verdict = result.get("final_verdict", {})
    if verdict:
        score = verdict.get("survivability_score", "?")
        score_color = "green" if score >= 60 else "yellow" if score >= 30 else "red"
        console.print(Panel(
            f"[bold]Survivability: [{score_color}]{score}/100[/{score_color}][/bold]\n\n"
            f"[italic]{verdict.get('verdict', '')}[/italic]",
            title="🏛️  CHIEF ADVOCATE'S VERDICT", border_style="bold magenta"
        ))
        console.print(Panel(
            "\n".join([f"✅ {c}" for c in verdict.get("counter_conditions", [])]),
            title="🔑 Counter-Conditions",
            border_style="bold green"
        ))
        console.print(Panel(
            "\n".join([f"💀 {k}" for k in verdict.get("top_3_killers", [])]),
            title="☠️  Top 3 Killer Blows",
            border_style="bold red"
        ))

def run():
    console.print(Panel(
        "Welcome to [bold red]Devil's Advocate Agent[/bold red]\n"
        "Powered by [bold]Claude[/bold] + [bold]Qdrant[/bold]\n\n"
        "Submit any idea, plan, or proposal — 5 AI critics will attack it.",
        title="⚔️  Devil's Advocate Agent", border_style="red"
    ))
    while True:
        console.print("\n[bold yellow]Enter your proposal (or 'quit' to exit):[/bold yellow]")
        user_input = input("> ").strip()
        if user_input.lower() in ("quit", "exit", "q"):
            console.print("[bold]Goodbye![/bold]")
            break
        if not user_input:
            continue
        console.print("\n[bold red]⚔️  Unleashing 5 critics...[/bold red]")
        console.print("[dim]Takes 30-60 seconds as Claude thinks deeply...[/dim]\n")
        result = debate_app.invoke({
            "user_input": user_input,
            "dimensions": [],
            "proposal_summary": "",
            "attacks": {},
            "final_verdict": {}
        })
        display_results(result)

if __name__ == "__main__":
    run()