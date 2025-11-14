# Axon

A file navigator for the terminal, built on Miller Columns.

Axon is for fast, keyboard-driven file management. It combines a spatially-aware layout with deep Git integration and a contextual preview pane, all within a Textual interface. It's designed to be an extension of your workflow, not an interruption.

---

<p align="center">
  <a href="https://pypi.org/project/axon-tui/"><img src="https://img.shields.io/pypi/v/axon-tui.svg" alt="PyPI Version"></a>
  <a href="https://pypi.org/project/axon-tui/"><img src="https://img.shields.io/pypi/pyversions/axon-tui.svg" alt="Python Versions"></a>
  <a href="LICENSE"><img src="https://img.shields.io/badge/license-MIT-blue.svg" alt="License"></a>
</p>

---

### Core Workflow
<!-- Replace this placeholder with a GIF of Axon in use -->
![Axon Workflow](https://raw.githubusercontent.com/textualize/textual/main/docs/images/readme.gif)

### Features

*   **Miller Column Layout:** Navigate deep directory structures without losing context.
*   **Git-Aware:** See file statuses and view diffs directly in the preview pane.
*   **Contextual Preview Pane:** Renders syntax-highlighted code, file metadata, or live Git diffs automatically.
*   **Multi-File Selection:** Select items across columns with `space` for bulk operations.
*   **Command Palette:** A fuzzy-finder for every action. Press `Ctrl+P` to activate.
*   **Bookmarks:** Jump to aliased directories.

### Installation

**Prerequisites:**
*   Python 3.9+
*   A Nerd Font is required for icons.

Install from PyPI:
```bash
pip install axon-tui
```

### Usage

Run the command:
```bash
axon
```

#### Keybindings

| Key(s)               | Action                        |
| -------------------- | ----------------------------- |
| `j` / `↓`            | Move Down                     |
| `k` / `↑`            | Move Up                       |
| `l` / `→`            | Focus Next / Enter Dir        |
| `h` / `←`            | Focus Previous / Parent Dir   |
| `g`                  | Go to Top                     |
| `G`                  | Go to Bottom                  |
| `Backspace`          | History Back                  |
| `space`              | Toggle Selection              |
| `c`                  | Create File                   |
| `d`                  | Create Directory              |
| `r`                  | Rename                        |
| `x`                  | Delete                        |
| `?`                  | Help                          |
| `b`                  | Bookmarks                     |
| `.`                  | Toggle Hidden Files           |
| `t`                  | Cycle Syntax Theme            |
| `Ctrl`+`p`           | Command Palette               |
| `q` / `Ctrl`+`c`     | Quit                          |

### License

[MIT](LICENSE)
