# widgets.py

from pathlib import Path

from rich.text import Text
from textual.widget import Widget
from textual.widgets import Static, Label, ListItem

from utils import make_file_display, GIT_STATUS_ICONS

class DirectoryItem(ListItem):
    """A ListItem that displays a file or directory."""

    def __init__(self, path: Path, repo):
        super().__init__(Label(make_file_display(path, repo)))
        self.path = path

class GitDiffLine(Widget):
    """A widget to display a single line of a git diff."""
    
    def __init__(self, line: str):
        super().__init__()
        self.line = line

    def render(self) -> Text:
        if self.line.startswith('+'):
            return Text.assemble(GIT_STATUS_ICONS["GIT_DIFF_ADD"], " ", self.line[1:], style="green")
        elif self.line.startswith('-'):
            return Text.assemble(GIT_STATUS_ICONS["GIT_DIFF_REMOVE"], " ", self.line[1:], style="red")
        elif self.line.startswith('@@'):
            return Text(self.line, style="cyan")
        else:
            return Text(f"  {self.line}", style="dim")