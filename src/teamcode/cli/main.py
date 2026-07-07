import typer

from teamcode.cli.commands import config, init, run

app = typer.Typer(
    name="teamcode",
    help="Terminal-first AI software engineering team.",
    no_args_is_help=True,
)

app.add_typer(run.app, name="run", help="Run a teamcode session.")
app.add_typer(init.app, name="init", help="Initialize a teamcode project.")
app.add_typer(config.app, name="config", help="View or edit configuration.")


def main() -> None:
    app()
