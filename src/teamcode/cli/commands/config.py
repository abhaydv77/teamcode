from __future__ import annotations

import typer

app = typer.Typer()


@app.command()
def show() -> None:
    """Show current configuration."""
    typer.echo("Configuration:")
    typer.echo("Not yet implemented.")
    raise typer.Exit(code=0)


@app.command()
def set(
    key: str = typer.Argument(..., help="Configuration key."),
    value: str = typer.Argument(..., help="Configuration value."),
) -> None:
    """Set a configuration value."""
    typer.echo(f"Setting {key} = {value}")
    typer.echo("Not yet implemented.")
    raise typer.Exit(code=0)
