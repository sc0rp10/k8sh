#!/usr/bin/env python3
import argparse
import os.path
from typing import List, Tuple

from prompt_toolkit import PromptSession, HTML
from prompt_toolkit.history import FileHistory

from utils.completer import K8shCompleter

from command.cat import CatCommand
from command.clear import ClearCommand
from command.edit import EditCommand
from command.cd import CdCommand
from command.exit import ExitCommand
from command.help import HelpCommand
from command.history import HistoryCommand
from command.logs import LogsCommand
from command.ls import LsCommand
from command.pwd import PwdCommand
from command.exec import ExecCommand
from command.restart import RestartCommand
from command.registry import CommandRegistry
from state.state import State
from utils.terminal import Color, colorize, disable_colors


def register_commands(registry: CommandRegistry) -> None:
    """Register all available commands"""
    # Navigation commands
    registry.register_command(LsCommand())
    registry.register_command(CdCommand())
    registry.register_command(PwdCommand())
    registry.register_command(CatCommand())
    registry.register_command(EditCommand())
    registry.register_command(ExecCommand())
    registry.register_command(LogsCommand())
    registry.register_command(ClearCommand())
    registry.register_command(HistoryCommand())
    registry.register_command(RestartCommand())

    # Help command (needs registry reference)
    registry.register_command(HelpCommand(registry))

    # Exit command
    registry.register_command(ExitCommand())


def parse_input(input_text: str) -> Tuple[str, List[str]]:
    """Parse input text into command and arguments"""
    parts = input_text.strip().split()
    command = parts[0] if parts else ""
    args = parts[1:] if len(parts) > 1 else []

    return command, args


def run_command(registry: CommandRegistry, state: State, command_name: str, args: List[str]) -> bool:
    """Run a command and return True if execution should continue, False otherwise"""
    if not command_name:
        return True

    command = registry.get_command(command_name)
    if command:
        try:
            state.set_current_command(command_name)
            command.execute(state, args)
            state.set_current_command(None)
        except SystemExit:
            state.set_current_command(None)
            return False
        except Exception as e:
            print(f"Error executing command: {str(e)}")
            state.set_current_command(None)
    else:
        print(f"Command not found: {command_name}")

    return True


def run_script(script_path: str, registry: CommandRegistry, state: State) -> None:
    """Run a script of commands from a file"""
    try:
        with open(script_path, 'r') as f:
            for line_number, line in enumerate(f, 1):
                line = line.strip()

                # Skip empty lines and comments
                if not line or line.startswith('#'):
                    continue

                print(f"$ {line}")
                command_name, args = parse_input(line)

                if not run_command(registry, state, command_name, args):
                    print(f"Script execution stopped at line {line_number}")
                    break
    except FileNotFoundError:
        print(f"Script file not found: {script_path}")
    except Exception as e:
        print(f"Error running script: {str(e)}")


def main() -> None:
    """Main entry point"""
    # Parse command line arguments
    parser = argparse.ArgumentParser(description="K8sh - Kubernetes Shell")
    parser.add_argument('script', nargs='?', help='Path to a script file to execute')
    parser.add_argument('--no-color', action='store_true', help='Disable colorized output')
    args = parser.parse_args()

    # Disable colors if requested
    if args.no_color:
        disable_colors()

    # Initialize state and command registry
    state = State()
    registry = CommandRegistry()
    register_commands(registry)

    # Run script if provided
    if args.script:
        run_script(args.script, registry, state)
        return

    # Create prompt session with history
    try:
        session: PromptSession = PromptSession(
            history=FileHistory(os.path.expanduser('~/.k8sh_history')),
            completer=K8shCompleter(registry, state)
        )
    except Exception:
        # Fallback if history file can't be created
        session = PromptSession(
            completer=K8shCompleter(registry, state)
        )

    # Store the session in the state for access by commands
    state.set_prompt_session(session)

    # Print welcome message
    print(colorize("Welcome to K8sh - Kubernetes Shell", Color.BRIGHT_GREEN))
    print(f"Type {colorize('help', Color.BRIGHT_YELLOW)} for a list of commands or {colorize('exit', Color.BRIGHT_YELLOW)} to quit")

    # Main loop
    while True:
        try:
            current_path = state.get_current_path()
            if current_path == "":
                current_path = "/"

            if args.no_color:
                promt = HTML(f"{current_path} $ ")
            else:
                promt = HTML(f"<ansigreen><b>{current_path}</b></ansigreen> <ansired>$</ansired> ")

            user_input: str = session.prompt(promt)
            command_name, command_args = parse_input(user_input)

            if not run_command(registry, state, command_name, command_args):
                break

        except KeyboardInterrupt:
            print("^C")
        except EOFError:
            print("^D")
            break
        except Exception as e:
            print(f"Error: {str(e)}")

    print("Goodbye!")


if __name__ == "__main__":
    main()
