# project-tree

A small, dependency-free Python CLI util that prints a recursive tree structure of a project – like a lightweight **tree** with sensible Python-flavoerd defaults.

## Features

* Recursively prints tree of any given directory.
* Ignores `__pycache__`, `.venv*`, `.idea*`, `.env`, `.env.*`, `.env-*`, `.git`, `*.pyc`, `*.pyo`, `*.pyd` by default.
* `-i / --ignore` to add extra ignored files/folders (space- or comma-separated).
* `-e / --excludefile [FILE]` to load a `.gitignore`-like file with extra patterns.
* `-s / --size` to include human-readable file sizes.
* `-o / --output [FILE]` to write the output to custom path (`project-tree.txt` by default). 

## Installation

### From PyPi (once published):
```pip install project-tree```
### From GitHub
```pip install git+https://github.com/VanirSama/project-tree.git```

## Usage

| CLI-command usage example                                                                        | Description                                                                                    |
|--------------------------------------------------------------------------------------------------|------------------------------------------------------------------------------------------------|
| `project-tree`                                                                                   | Tree of current directory.                                                                     |
| `project-tree .\my-project`                                                                      | Tree of `.\my-project`                                                                         |
| `project-tree -s`                                                                                | Tree with files size displayed                                                                 |
| `project-tree -i dist`<br>`project-tree -i dist docs *.tmp`<br>`project-tree -i dist,docs,*.tmp` | Add ignored files/folders<br>*(either space- or comma- separated sequences work equally fine)* |
| `project-tree -e exclude.txt`                                                                    | Load patterns from `.gitignore`-like file.                                                     |
| `project-tree -o`<br>`project-tree -o .\tree\output.txt`                                         | Write output tree into custom file or into `project-tree.txt` by default.                      |

## Example output

`project-tree -s -i tests -o`

```txt
src/
└── project_tree/
    ├── __init__.py  (86B)
    ├── __main__.py  (132B)
    ├── cli.py  (3.5KB)
    ├── core.py  (4.6KB)
    └── utils.py  (665B)
```

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

