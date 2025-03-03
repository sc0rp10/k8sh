#!/usr/bin/env python3
"""
Terminal utilities for K8sh
"""
import os
import shutil
from enum import Enum
from typing import List

# Global flag to disable colors
# Check for NO_COLOR environment variable (https://no-color.org/)
COLORS_ENABLED = os.environ.get("NO_COLOR") is None


def disable_colors():
    """Disable terminal colors globally"""
    global COLORS_ENABLED
    COLORS_ENABLED = False


def enable_colors():
    """Enable terminal colors globally"""
    global COLORS_ENABLED
    COLORS_ENABLED = True


class Color(Enum):
    """Terminal colors"""
    RESET = "\033[0m"
    BOLD = "\033[1m"
    UNDERLINE = "\033[4m"

    # Foreground colors
    BLACK = "\033[30m"
    RED = "\033[31m"
    GREEN = "\033[32m"
    YELLOW = "\033[33m"
    BLUE = "\033[34m"
    MAGENTA = "\033[35m"
    CYAN = "\033[36m"
    WHITE = "\033[37m"

    # Bright foreground colors
    BRIGHT_BLACK = "\033[90m"
    BRIGHT_RED = "\033[91m"
    BRIGHT_GREEN = "\033[92m"
    BRIGHT_YELLOW = "\033[93m"
    BRIGHT_BLUE = "\033[94m"
    BRIGHT_MAGENTA = "\033[95m"
    BRIGHT_CYAN = "\033[96m"
    BRIGHT_WHITE = "\033[97m"


def colorize(text: str, color: Color) -> str:
    """Colorize text with the specified color"""
    if not COLORS_ENABLED:
        return text
    return f"{color.value}{text}{Color.RESET.value}"


def format_columns(items: List[str], is_dir_func=None) -> str:
    """Format items in columns like the GNU ls command"""
    if not items:
        return ""

    # Get terminal width
    terminal_width = shutil.get_terminal_size().columns

    # Sort the items
    sorted_items = sorted(items)

    # Colorize items based on whether they are directories
    colorized_items = []
    for item in sorted_items:
        if is_dir_func and is_dir_func(item):
            # All directories are blue
            colorized_items.append(colorize(item, Color.BRIGHT_BLUE))
        else:
            # All files are white
            colorized_items.append(colorize(item, Color.BRIGHT_WHITE))

    # Calculate the maximum visible length (excluding color codes)
    max_visible_length = 0
    for item in colorized_items:
        visible_length = len(item.replace("\033[", "").replace("m", ""))
        max_visible_length = max(max_visible_length, visible_length)

    # Add spacing between columns
    column_width = max_visible_length + 2

    # Calculate the number of columns that can fit in the terminal
    num_columns = max(1, terminal_width // column_width)

    # Create the output in GNU ls style (items ordered by column)
    result = []
    row = []
    for i, item in enumerate(colorized_items):
        row.append(item)
        if (i + 1) % num_columns == 0 or i == len(colorized_items) - 1:
            # Pad all items except the last one in the row
            padded_row = []
            for j, col_item in enumerate(row):
                if j < len(row) - 1 or (i + 1) % num_columns == 0:
                    # Calculate visible length (excluding color codes)
                    visible_length = len(col_item.replace("\033[", "").replace("m", ""))
                    padding = " " * (column_width - visible_length)
                    padded_row.append(f"{col_item}{padding}")
                else:
                    padded_row.append(col_item)
            result.append("".join(padded_row))
            row = []

    return "\n".join(result)


def format_long_listing(items: List[str], is_dir_func=None) -> str:
    """Format items in simplified long listing format with only type, date, and name"""
    if not items:
        return ""

    # Sort the items
    sorted_items = sorted(items)

    # Format each item
    formatted_items = []
    for item in sorted_items:
        is_dir = is_dir_func and is_dir_func(item)

        # File type indicator (d for directory, - for file)
        file_type = "d" if is_dir else "-"

        # Date (current date as placeholder)
        from datetime import datetime
        date = datetime.now().strftime("%b %d %H:%M")

        # Colorize the name based on whether it's a directory or file
        if is_dir:
            # All directories are blue
            name = colorize(item, Color.BRIGHT_BLUE)
        else:
            # All files are white
            name = colorize(item, Color.BRIGHT_WHITE)

        # Format the line with only type, date, and name
        line = f"{file_type} {date}  {name}"
        formatted_items.append(line)

    return "\n".join(formatted_items)
