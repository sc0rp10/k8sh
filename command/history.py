#!/usr/bin/env python3
"""
History command for K8sh
"""
from typing import List

from command.base import GenericCommand
from state.state import State
from utils.terminal import Color, colorize


class HistoryCommand(GenericCommand):
    """Command to display command history"""

    def get_name(self) -> str:
        """Get the name of the command"""
        return "history"

    def get_aliases(self) -> List[str]:
        """Get the aliases for the command"""
        return []

    def get_help(self) -> str:
        """Get the help text for the command"""
        return "Display command history"

    def get_usage(self) -> str:
        """Get the usage text for the command"""
        usage = [
            "Usage: history [n]",
            "",
            "Display the last n commands from history (default: 10)",
            "",
            "Examples:",
            f"  {colorize('history', Color.BRIGHT_YELLOW)}      # Show the last 10 commands",
            f"  {colorize('history 20', Color.BRIGHT_YELLOW)}   # Show the last 20 commands",
        ]
        return "\n".join(usage)

    def execute(self, state: State, args: List[str]) -> None:
        """Execute the history command"""
        # Default number of history entries to show
        num_entries = 10

        # Parse arguments
        if args and args[0].isdigit():
            num_entries = int(args[0])

        # Get the prompt session from state
        session = state.get_prompt_session()
        if not session:
            print(colorize("No active session found", Color.BRIGHT_YELLOW))
            return

        try:
            # Get history from the session
            history = session.history

            # Get all history entries
            history_entries = list(history.get_strings())

            if not history_entries:
                print(colorize("No history found", Color.BRIGHT_YELLOW))
                return

            # Get the last n entries
            entries_to_show = history_entries[-num_entries:] if len(history_entries) >= num_entries else history_entries

            # Print history entries with line numbers
            for i, entry in enumerate(entries_to_show):
                print(f"{colorize(entry, Color.BRIGHT_BLUE)}")

        except Exception as e:
            print(colorize(f"Error reading history: {str(e)}", Color.BRIGHT_RED))
