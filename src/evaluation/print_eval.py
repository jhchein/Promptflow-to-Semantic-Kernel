from rich.console import Console
from rich.panel import Panel
from rich.table import Table


def shorten_text(text: str, max_length: int = 300) -> str:
    if not text:
        return ""
    if len(text) > max_length:
        return text[:max_length] + "..."
    return text


def print_metrics(metrics, console: Console):
    table = Table(
        title="Evaluation Metrics",
        show_header=True,
        header_style="bold magenta",
    )
    table.add_column("Metric", style="cyan")
    table.add_column("Value", style="green")
    for key, value in metrics.items():
        table.add_row(key, str(value))
    console.print(table)


def print_row(row, console: Console):
    question = row.get("inputs.question", "")
    response = row.get("outputs.response", "")
    context = row.get("outputs.context", "")
    ground_truth = row.get("inputs.ground_truth_answer", "")
    rel = row.get("outputs.relevance.relevance", "")
    rel_result = row.get("outputs.relevance.relevance_result", "")
    rel_reason = row.get("outputs.relevance.relevance_reason", "")
    ret = row.get("outputs.retrieval.retrieval", "")
    ret_result = row.get("outputs.retrieval.retrieval_result", "")
    ret_reason = row.get("outputs.retrieval.retrieval_reason", "")

    # New: Groundedness
    groundedness = row.get("outputs.groundedness.groundedness", "")
    groundedness_result = row.get("outputs.groundedness.groundedness_result", "")
    groundedness_reason = row.get("outputs.groundedness.groundedness_reason", "")

    # # New: Response Completeness
    # resp_compl = row.get("outputs.response_completeness.response_completeness", "")
    # resp_compl_result = row.get(
    #     "outputs.response_completeness.response_completeness_result", ""
    # )
    # resp_compl_reason = row.get(
    #     "outputs.response_completeness.response_completeness_reason", ""
    # )

    table = Table(show_header=False, box=None)
    table.add_row("[bold red]QUESTION[/bold red]", shorten_text(question))
    table.add_row("[bold green]RESPONSE[/bold green]", shorten_text(response))
    table.add_row("[bold blue]CONTEXT[/bold blue]", shorten_text(context))
    table.add_row("[bold blue]GROUND TRUTH[/bold blue]", shorten_text(ground_truth))
    table.add_row(
        "[bold yellow]RELEVANCE[/bold yellow]",
        f"{'✅ Pass' if rel_result == 'pass' else '❌ Fail'} ({rel})",
    )
    table.add_row("[dim]Relevance Reason[/dim]", shorten_text(rel_reason))
    table.add_row(
        "[bold yellow]RETRIEVAL[/bold yellow]",
        f"{'✅ Pass' if ret_result == 'pass' else '❌ Fail'} ({ret})",
    )
    table.add_row("[dim]Retrieval Reason[/dim]", shorten_text(ret_reason))
    table.add_row(
        "[bold yellow]GROUNDEDNESS[/bold yellow]",
        f"{'✅ Pass' if groundedness_result == 'pass' else '❌ Fail'} ({groundedness})",
    )
    table.add_row("[dim]Groundedness Reason[/dim]", shorten_text(groundedness_reason))
    # table.add_row(
    #     "[bold yellow]RESPONSE COMPLETENESS[/bold yellow]",
    #     f"{'✅ Pass' if resp_compl_result == 'pass' else '❌ Fail'} ({resp_compl})",
    # )
    # table.add_row(
    #     "[dim]Response Completeness Reason[/dim]", shorten_text(resp_compl_reason)
    # )

    panel = Panel(table, title="Result", expand=False, border_style="magenta")
    console.print(panel)
