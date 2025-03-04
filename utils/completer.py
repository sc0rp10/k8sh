#!/usr/bin/env python3
"""
Autocomplete functionality for K8sh with fuzzy matching
"""
import os
from typing import Iterable

from fuzzyfinder import fuzzyfinder
from prompt_toolkit.completion import Completer, Completion
from prompt_toolkit.document import Document

from command.registry import CommandRegistry
from state.state import State


class K8shCompleter(Completer):
    """
    Completer for K8sh that provides fuzzy-matching for commands and paths
    """

    def __init__(self, registry: CommandRegistry, state: State) -> None:
        self.registry = registry
        self.state = state

    def _get_path_completions(self, typed_path: str) -> Iterable[Completion]:
        """
        Get completions for a path
        """
        current_path = self.state.get_current_path()

        # If no path is typed, return all available items at current path
        if not typed_path:
            try:
                available_items = self.state.get_available_items()

                if isinstance(available_items, list):
                    for item in available_items:
                        is_dir = self.state.is_directory(item)
                        yield Completion(
                            item,
                            start_position=0,
                            display_meta="Directory" if is_dir else "File"
                        )
                return
            except Exception:
                return

        # For absolute paths, start from root
        if typed_path.startswith("/"):
            base_path = ""
        # For relative paths, start from current path
        else:
            base_path = current_path if current_path != "/" else ""

        # Split the path into segments
        segments = typed_path.strip("/").split("/")

        # Special handling for nested fuzzy path completion
        # This handles cases like "cd dflt/dploy" -> "/default/deployments/"
        if len(segments) > 1:
            try:
                # For two-segment paths (namespace/resource_type)
                if len(segments) == 2:
                    # Get all available namespaces
                    temp_state = State()
                    namespaces = temp_state.get_available_items()

                    # Find fuzzy matches for the first segment
                    namespace_matches = list(fuzzyfinder(segments[0], namespaces))

                    for namespace in namespace_matches:
                        # Navigate to the namespace
                        temp_state.set_path(namespace)

                        # Get available items in the namespace
                        resource_types = temp_state.get_available_items()

                        # Find fuzzy matches for the second segment
                        resource_matches = list(fuzzyfinder(segments[1], resource_types))

                        for resource_type in resource_matches:
                            # Build the full path without leading slash
                            full_path = namespace + "/" + resource_type

                            # Don't add trailing slashes
                            # if temp_state.is_directory(resource_type):
                            #     full_path += "/"

                            yield Completion(
                                full_path,
                                start_position=-len(typed_path),
                                display_meta="Directory" if temp_state.is_directory(resource_type) else "File"
                            )

                # For three-segment paths (namespace/resource_type/resource)
                elif len(segments) == 3:
                    # Get all available namespaces
                    temp_state = State()
                    namespaces = temp_state.get_available_items()

                    # Find fuzzy matches for the first segment
                    namespace_matches = list(fuzzyfinder(segments[0], namespaces))

                    for namespace in namespace_matches:
                        # Navigate to the namespace
                        temp_state.set_path(namespace)

                        # Get available items in the namespace
                        resource_types = temp_state.get_available_items()

                        # Find fuzzy matches for the second segment
                        resource_type_matches = list(fuzzyfinder(segments[1], resource_types))

                        for resource_type in resource_type_matches:
                            # Navigate to the resource type
                            resource_type_path = namespace + "/" + resource_type
                            temp_state.set_path(resource_type_path)

                            # Get available resources
                            resources = temp_state.get_available_items()

                            # Find fuzzy matches for the third segment
                            resource_matches = list(fuzzyfinder(segments[2], resources))

                            for resource in resource_matches:
                                # Build the full path - ensure no double slashes
                                if resource_type_path.endswith('/'):
                                    full_path = resource_type_path + resource
                                else:
                                    full_path = resource_type_path + "/" + resource

                                # Don't add trailing slashes
                                # if temp_state.is_directory(resource):
                                #     full_path += "/"

                                yield Completion(
                                    full_path,
                                    start_position=-len(typed_path),
                                    display_meta="Directory" if temp_state.is_directory(resource) else "File"
                                )
            except Exception:
                # If there's an error, don't provide completions
                pass

            # If we've yielded any completions, return
            # Otherwise, fall through to the standard approach

        # Standard approach for single segment or fallback
        try:
            # Get the segment we're trying to complete
            segment_to_complete = segments[-1] if segments else ""

            # Get the path prefix (everything before the segment we're completing)
            path_prefix = "/".join(segments[:-1]) if len(segments) > 1 else ""

            # Build the full prefix path
            if path_prefix:
                if base_path:
                    full_prefix = base_path + "/" + path_prefix
                else:
                    full_prefix = path_prefix
            else:
                full_prefix = base_path

            # Create a temporary state to navigate to the path prefix
            temp_state = State()

            # Set the path to the prefix - avoid double slashes
            if full_prefix:
                temp_state.set_path(full_prefix)

            # Get available items at this path
            available_items = temp_state.get_available_items()

            if available_items and isinstance(available_items, list):
                # Get fuzzy matches for the segment we're completing
                matches = list(fuzzyfinder(segment_to_complete, available_items))

                # Generate completions for each match
                for item in matches:
                    # Determine if we should use relative or absolute path

                    # For relative paths, just use the segment we're completing
                    if path_prefix or base_path:
                        # We're completing a path with segments, use the last segment + item
                        if path_prefix:
                            relative_path = path_prefix + "/" + item
                        else:
                            # We're completing from base_path, just use item
                            relative_path = item

                        # Don't add trailing slashes
                        # if temp_state.is_directory(item):
                        #     relative_path += "/"

                        # Yield the completion with relative path
                        yield Completion(
                            relative_path,
                            start_position=-len(typed_path),
                            display_meta="Directory" if temp_state.is_directory(item) else "File"
                        )
                    else:
                        # We're at root, just use the item
                        completion_path = item

                        # Don't add trailing slashes
                        # if temp_state.is_directory(item):
                        #     completion_path += "/"

                        # Yield the completion
                        yield Completion(
                            completion_path,
                            start_position=-len(typed_path),
                            display_meta="Directory" if temp_state.is_directory(item) else "File"
                        )
        except Exception:
            # If there's an error, don't provide completions
            pass

    def get_completions(self, document: Document, complete_event=None) -> Iterable[Completion]:
        """
        Get completions for the current document
        """
        text = document.text_before_cursor

        # If the text is empty, return all commands
        if not text:
            for command in self.registry.get_command_names():
                yield Completion(command, start_position=0)
            return

        # Split the text into parts
        parts = text.split()
        matches = None

        # If we only have one part or the cursor is still in the first part,
        # we're completing a command
        if len(parts) <= 1 or len(text) <= len(parts[0]):
            word = parts[0] if parts else ""

            # Get all command names
            command_names = self.registry.get_command_names()

            # Check for exact matches first
            exact_matches = [cmd for cmd in command_names if cmd == word]
            starts_with_matches = [cmd for cmd in command_names if cmd.startswith(word) and cmd != word]

            # If there's an exact match AND the word is followed by space, don't provide completion
            if exact_matches and text.endswith(' '):
                return

            # If we have an exact match for a command like 'cd', prioritize it first
            # This ensures 'cd' is always the first suggestion when typing 'cd'
            if exact_matches and not text.endswith(' '):
                for command in exact_matches:
                    yield Completion(
                        command,
                        start_position=-len(word),
                        display_meta="Command"
                    )

            # If there are commands that start with the typed text, prioritize those
            if starts_with_matches:
                for command in starts_with_matches:
                    yield Completion(
                        command,
                        start_position=-len(word),
                        display_meta="Command"
                    )
            else:
                # Only use fuzzy matching if there are no exact prefix matches
                # This prevents showing commands like "ccd" when typing "cd"
                matches = list(fuzzyfinder(word, command_names))

                # Don't include exact matches in fuzzy results to avoid duplication
                fuzzy_matches = [cmd for cmd in matches if cmd not in exact_matches and cmd not in starts_with_matches]

                for command in fuzzy_matches:
                    yield Completion(
                        command,
                        start_position=-len(word),
                        display_meta="Command"
                    )

            # If we haven't matched anything and the word is not empty,
            # show all command names as a fallback
            if word and not exact_matches and not starts_with_matches and not matches:
                for command in sorted(command_names):
                    yield Completion(
                        command,
                        start_position=-len(word),
                        display_meta="Command"
                    )

            return

        command = parts[0]

        # For navigation commands, complete paths
        if command in self.registry.get_for_autocomplete():
            # Get the path being typed - find the last part that doesn't start with a dash
            # This handles commands like 'tail -f pods/' where 'pods/' is the path
            typed_path = ""
            for i, part in enumerate(parts[1:], 1):
                if not part.startswith('-'):
                    typed_path = part
                    break

            # If we're at the end of the command and the cursor is at the end,
            # and we didn't find a path, we should offer completions for the current directory
            if not typed_path and len(parts) > 1 and document.cursor_position == len(document.text):
                # Check if the last part is a flag (like -f)
                if parts[-1].startswith('-'):
                    typed_path = ""  # Offer completions for current directory

            # Special handling for paths ending with a slash but no additional text
            # This ensures we show content within a directory when user types "dir/" and hits tab
            if typed_path.endswith("/") and not typed_path.endswith("//"):
                try:
                    # Create a temporary state for safe navigation
                    temp_state = State()

                    # Get the current path as a base
                    base_path = self.state.get_current_path()

                    # Debug output
                    if os.environ.get("DEBUG") == "1":
                        print(f"Debug - typed_path: {typed_path}, base_path: {base_path}")

                    # Combine with the typed path (without the trailing slash)
                    full_path = typed_path[:-1]

                    # Fix the path if we're at root
                    if base_path == "" and not typed_path.startswith("/"):
                        # We're at root, so we don't need to add a slash
                        full_path = typed_path[:-1]
                    elif base_path and not typed_path.startswith("/"):
                        # For relative paths, combine with current path
                        full_path = base_path + "/" + full_path
                    elif typed_path.startswith("/"):
                        # For absolute paths, just use the typed path
                        full_path = typed_path[1:-1]  # Remove leading and trailing slashes

                    # Navigate to this path to get contents
                    try:
                        # Try to set path directly first
                        temp_state.set_path(full_path)
                    except Exception:
                        # If that fails, try a more cautious approach by navigating segment by segment
                        try:
                            temp_state = State()  # Fresh state
                            segments = full_path.split('/')

                            # Navigate segment by segment
                            current_path = ""
                            for i, segment in enumerate(segments):
                                if not segment:
                                    continue

                                if current_path:
                                    current_path += "/" + segment
                                else:
                                    current_path = segment

                                try:
                                    temp_state.set_path(current_path)
                                except Exception:
                                    # If we can't navigate further, use what we have so far
                                    break
                        except Exception:
                            # If all else fails, we'll have an empty available_items list
                            pass

                    # Get available items at this path
                    available_items = temp_state.get_available_items()

                    if available_items and isinstance(available_items, list):
                        for item in available_items:
                            is_dir = temp_state.is_directory(item)
                            # Add the item to the path with the trailing slash
                            complete_path = typed_path + item
                            yield Completion(
                                complete_path,
                                start_position=-len(typed_path),
                                display_meta="Directory" if is_dir else "File"
                            )
                        return
                except Exception:
                    # If there's any error, fall back to the regular completion
                    pass

            # Use the internal path completion method for all other cases
            yield from self._get_path_completions(typed_path)
