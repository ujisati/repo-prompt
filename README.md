# Concatenate Files Script (`repo_prompt.py`)

This script concatenates specified files into a single output. Each file's content is wrapped in a Markdown code fence, and a tree structure showing the included files (relative to their common ancestor directory) is prepended to the output. If a file is detected as non-UTF-8 encoded (e.g., a binary file), its content will be replaced with `[non-text content]`.

## Requirements

- Python 3.8+
- `uv`


## Usage with `uv`

```bash
uv run repo_prompt.py [OPTIONS] FILES...
```

## Example Usage

```bash
# Concatenate specific files into stdout
uv run repo_prompt.py file1.py file2.md

# Use glob patterns to include multiple files from different directories
uv run repo_prompt.py src/*.py tests/*.py

# Output to a specific file instead of stdout
uv run repo_prompt.py --output prompt.md src/**/*.py README.md
```
