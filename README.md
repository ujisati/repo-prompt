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

