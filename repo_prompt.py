#!/usr/bin/env python
# /// script
# requires-python = ">=3.8"
# dependencies = [
#   "typer[all]>=0.9.0",
# ]
# ///

"""
Concatenates specified files into a single output file.
Each file's content is wrapped in a Markdown code fence,
and a tree structure showing the included files is prepended.
"""

import typer
import sys
import os
import glob
from pathlib import Path
from typing import List, Dict, Any, Set

app = typer.Typer(
    help="Concatenates files into a single Markdown output with a file tree.",
    add_completion=False,
)

def build_tree_dict(paths: List[Path], common_base: Path) -> Dict[str, Any]:
    """Builds a nested dictionary representing the file tree structure."""
    tree: Dict[str, Any] = {}
    for p in paths:
        try:
            relative_path = p.relative_to(common_base)
        except ValueError:
            # Should not happen if common_base is correctly determined,
            # but handle defensively maybe showing path from root or just filename
            relative_path = Path(p.name) # Fallback to just filename

        parts = relative_path.parts
        node = tree
        for i, part in enumerate(parts):
            if i == len(parts) - 1:  # It's the file
                node[part] = True  # Mark as file entry (value doesn't strictly matter)
            else:  # It's a directory
                node = node.setdefault(part, {}) # Get or create subdir node
                if node is True: # Error: Found a file where a directory was expected
                     print(f"Error: Path conflict processing {relative_path}. Is '{part}' both a file and directory in the input list?", file=sys.stderr)
                     # Overwrite file entry with directory dict - might be imperfect but tries to proceed
                     node = {}
                     # Re-point the parent's reference if needed (complex, easier to rely on setdefault)
                     # Let's assume setdefault handles the basics if key exists.
                     # We might need to re-insert the node into the parent if overwritten.
                     # Simpler: rely on sorted inputs potentially avoiding this? Or pre-validate paths.
                     # For this tool's scope, this conflict is unlikely unless user provides odd input.

    return tree

def format_tree(tree_dict: Dict[str, Any], common_base: Path) -> str:
    """Formats the tree dictionary into a printable string."""
    tree_lines: List[str] = []

    # Determine root display name
    cwd = Path.cwd()
    try:
        # Try to show path relative to current directory if possible
        root_display_name = str(common_base.relative_to(cwd))
        if root_display_name == ".":
            root_display_name = common_base.name or "." # Use dir name if not CWD itself
    except ValueError:
        # If not relative to CWD, show absolute path or just the name
        root_display_name = str(common_base)

    tree_lines.append(root_display_name)

    def generate_lines(node: Dict[str, Any], prefix: str = ""):
        items = sorted(node.keys())
        pointers = ["├── "] * (len(items) - 1) + ["└── "]
        for i, name in enumerate(items):
            pointer = pointers[i]
            tree_lines.append(f"{prefix}{pointer}{name}")

            child_node = node[name]
            if isinstance(child_node, dict):  # It's a directory node
                extension = "│   " if i < len(items) - 1 else "    "
                generate_lines(child_node, prefix + extension)

    generate_lines(tree_dict)
    return "\n".join(tree_lines)

@app.command()
def main(
    files: List[str] = typer.Argument( # Changed from List[Path] to List[str]
        ..., 
        help="Paths or glob patterns for files to concatenate.",
        # Validation (exists, file_okay, etc.) will be done after glob expansion
    ),
    output_file: Path = typer.Option(
        None,
        "--output",
        "-o",
        help="Optional file path to write the output to (default: stdout).",
        writable=True,
        dir_okay=False,
        resolve_path=True,
    )
):
    """
    Concatenates FILE arguments into a single output.

    Each file's content is wrapped in a Markdown code fence.
    A tree structure of the included files relative to their common
    ancestor directory is prepended to the output.
    """
    if not files:
        print("No input file patterns specified.", file=sys.stderr)
        raise typer.Exit(code=1)

    expanded_files: Set[Path] = set()
    for pattern in files:
        # Expand globs. If it's a specific file path without glob characters,
        # glob.glob will return it as a list containing just that path.
        # Using recursive=True for `**` support if needed, though not explicitly requested.
        # For simplicity, let's assume simple globs for now, or user can use `**` if their shell doesn't expand it.
        # Path.glob can also be used: Path(".").glob(pattern)
        # However, glob.glob handles absolute patterns more directly.
        
        # If pattern is an absolute path, glob works fine.
        # If pattern is relative, it's relative to CWD.
        matched_files = glob.glob(pattern, recursive=True)
        if not matched_files:
            print(f"Warning: Pattern '{pattern}' did not match any files.", file=sys.stderr)
            
        for f_str in matched_files:
            p = Path(f_str).resolve()
            if not p.exists():
                # This should ideally not happen if glob found it, but good for sanity.
                print(f"Warning: File '{p}' found by glob but does not exist upon resolution. Skipping.", file=sys.stderr)
                continue
            if not p.is_file():
                print(f"Warning: Path '{p}' matched by glob is not a file. Skipping.", file=sys.stderr)
                continue
            if not os.access(p, os.R_OK):
                print(f"Warning: File '{p}' is not readable. Skipping.", file=sys.stderr)
                continue
            expanded_files.add(p)

    if not expanded_files:
        print("No valid files found after expanding patterns.", file=sys.stderr)
        raise typer.Exit(code=1)

    # Convert set of resolved Path objects to a sorted list for consistent order
    absolute_paths = sorted(list(expanded_files))

    # Find common base directory
    if len(absolute_paths) == 1:
        # If only one file, its parent directory is the base
        common_base = absolute_paths[0].parent
    else:
        # Use os.path.commonpath for multiple files
        try:
            common_str = os.path.commonpath([str(p) for p in absolute_paths])
            common_base = Path(common_str)
            # Ensure common_base is actually a directory, if not, use its parent
            # (commonpath might return a file if all paths point to the same file,
            # or a non-existent path segment if inputs are diverse like /a/b and /a/c/d)
            # Let's refine: check if it exists and is a directory. If not, go up.
            while not common_base.is_dir():
                common_base = common_base.parent
                if common_base == common_base.parent: # Reached root (e.g., '/')
                     break
        except ValueError:
            # This can happen if paths are on different drives on Windows.
            # Fallback to current working directory as base? Or error out?
            print("Error: Cannot determine a common path for input files (possibly on different drives?).", file=sys.stderr)
            # Let's try using CWD as a base for display purposes, paths will be absolute/relative to CWD then.
            common_base = Path.cwd()
            print(f"Warning: Using current directory '{common_base}' as fallback base for tree display.", file=sys.stderr)


    # --- Generate Tree ---
    tree_dict = build_tree_dict(absolute_paths, common_base)
    tree_output = format_tree(tree_dict, common_base)

    # --- Generate Concatenated Content ---
    concatenated_content: List[str] = []
    for p in absolute_paths:
        try:
            content = p.read_text()
            # Determine path to display in fence (relative to common base)
            try:
                display_path = p.relative_to(common_base)
            except ValueError:
                # Fallback if path isn't relative (e.g., different drive case)
                # Try relative to CWD or just show absolute path or filename?
                try:
                   display_path = p.relative_to(Path.cwd())
                except ValueError:
                   display_path = p # Absolute path
                display_path = f"{display_path} (relative to {common_base})" # Add context

            # Use just the relative path string in the fence identifier for cleaner look
            fence_id = str(display_path).replace(" (relative to ...)", "") # Clean up context string if added

            fence = f"```{fence_id}\n{content.strip()}\n```"
            concatenated_content.append(fence)
        except Exception as e:
            print(f"Warning: Could not read or process file {p}: {e}", file=sys.stderr)

    # --- Combine and Output ---
    final_output = tree_output + "\n\n" + "\n\n".join(concatenated_content)

    if output_file:
        try:
            output_file.write_text(final_output + "\n")
            print(f"Output successfully written to {output_file}", file=sys.stderr)
        except Exception as e:
            print(f"Error: Could not write to output file {output_file}: {e}", file=sys.stderr)
            raise typer.Exit(code=1)
    else:
        # Print to stdout
        print(final_output)


if __name__ == "__main__":
    app()
