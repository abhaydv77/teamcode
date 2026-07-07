from __future__ import annotations

import typer

app = typer.Typer()


@app.command()
def session(
    task: str = typer.Argument("", help="Description of the task to complete."),
    config_file: str | None = typer.Option(
        None, "--config", "-c", help="Path to team config file."
    ),
) -> None:
    """Launch the TeamCode terminal UI."""
    from teamcode.ui.app import TeamCodeApp

    tui = TeamCodeApp()
    tui.run()
