#!/usr/bin/env python3
"""TeamCode — Mission Control Terminal UI.

Convenience entry point. The canonical application is defined in the
``teamcode.ui.app`` package module.

Usage:
    python ui.py
"""

from teamcode.ui.app import TeamCodeApp


def main() -> None:
    TeamCodeApp().run()


if __name__ == "__main__":
    main()
