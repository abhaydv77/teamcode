from __future__ import annotations

import typer

app = typer.Typer()


@app.command()
def project(
    name: str = typer.Argument("teamcode-project", help="Project name."),
) -> None:
    """Initialize a new teamcode project in the current directory."""
    typer.echo(f"Initializing project: {name}")
    typer.echo("Not yet implemented.")
    raise typer.Exit(code=0)
