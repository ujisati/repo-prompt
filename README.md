# Concatenate Files Script (`repo_prompt.py`)

This script concatenates specified files into a single output. Each file's content is wrapped in a Markdown code fence, and a tree structure showing the included files (relative to their common ancestor directory) is prepended to the output.

## Requirements

- Python 3.8+
- `uv` (or `pip`) for managing dependencies.

The script uses `typer`, which will be automatically handled if you run it via `uv run` or install dependencies from the script's header.

## Usage with `uv`

The script is designed to be run easily with `uv`. `uv` will create a temporary virtual environment, install dependencies specified in the script's header, and then execute the script.

```bash
uv run repo_prompt.py [OPTIONS] FILES...
```

**Arguments:**

*   `FILES...`: Paths or glob patterns for files to concatenate. This is a required argument.

**Options:**

*   `--output FILE, -o FILE`: Optional file path to write the output to. If not specified, output goes to stdout.
*   `--help`: Show help message and exit.

## Example

Suppose you have the following file structure:

```
my_project/
├── repo_prompt.py
├── notes.txt
└── src/
    └── main.py
```

And the files contain:

**`notes.txt`**:
```
This is a note.
```

**`src/main.py`**:
```python
def greet():
    print("Hello, world!")

greet()
```

You can concatenate these files by running the script from the `my_project` directory:

```bash
uv run repo_prompt.py notes.txt src/main.py
```

**Example Output:**

```markdown
my_project
├── notes.txt
└── src
    └── main.py

```notes.txt
This is a note.
```

```src/main.py
def greet():
    print("Hello, world!")

greet()
```
```

If you want to save the output to a file, for example `combined.md`:

```bash
uv run repo_prompt.py notes.txt src/main.py -o combined.md
```
This will create `combined.md` with the content shown above.

