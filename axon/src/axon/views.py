# views.py

import base64
from pathlib import Path
from typing import Set, Optional

import git
from rich.panel import Panel
from rich.syntax import Syntax
from rich.table import Table
from rich.text import Text

from textual.containers import Horizontal, VerticalScroll
from textual.message import Message
from textual.reactive import reactive
from textual.widgets import Static, ListView, Label
from textual.widgets import TabbedContent, TabPane
from textual.widget import Widget

from utils import get_file_metadata, is_likely_text_file, get_file_git_status
from widgets import DirectoryItem, GitDiffLine

class DirectoryBrowser(ListView):
    """A column in the Miller Column layout."""
    
    class Selected(Message):
        def __init__(self, path: Path):
            self.path = path
            super().__init__()

    def __init__(self, path: Path, repo, *, id: str):
        super().__init__(id=id)
        self.path = path
        self.repo = repo
        self.selected_paths: Set[Path] = set()

    def on_mount(self) -> None:
        try:
            paths = sorted(
                self.path.iterdir(),
                key=lambda p: (not p.is_dir(), p.name.lower())
            )
            for path in paths:
                if not self.app.show_hidden and path.name.startswith('.'):
                    continue
                self.append(DirectoryItem(path, self.repo))
        except OSError:
            pass

    def on_list_view_selected(self, event: ListView.Selected) -> None:
        if isinstance(event.item, DirectoryItem):
            self.post_message(self.Selected(event.item.path))

    def toggle_selection(self, path: Path):
        if path in self.selected_paths:
            self.selected_paths.remove(path)
        else:
            self.selected_paths.add(path)
        
        for child in self.children:
            if isinstance(child, DirectoryItem):
                if child.path in self.selected_paths:
                    child.add_class("selected")
                else:
                    child.remove_class("selected")


class MillerColumns(Horizontal):
    """The main file browser view using Miller Columns."""
    path: reactive[Optional[Path]] = reactive(None)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.repo = None
        self._current_path_rendered: Optional[Path] = None

    def watch_path(self, new_path: Optional[Path]) -> None:
        """Called when the path reactive property changes."""
        # vvv FINAL FIX: This guardrail prevents re-rendering the same path, solving the race condition. vvv
        if new_path is None or new_path == self._current_path_rendered:
            return
        
        self._current_path_rendered = new_path
        
        self.repo = self.app.repo
        self.remove_children()

        paths_to_render = list(reversed(new_path.parents))
        paths_to_render.append(new_path)

        for i, path_part in enumerate(paths_to_render):
            if path_part.is_dir():
                self.mount(DirectoryBrowser(path_part, self.repo, id=f"browser-{i}"))

        if self.children:
            self.call_after_refresh(self.children[-1].focus)
            self.call_after_refresh(self.scroll_end, animate=False)

    def on_directory_browser_selected(self, message: DirectoryBrowser.Selected) -> None:
        self.app.selected_path = message.path
        if message.path.is_dir():
            if message.path != self.path:
                self.path = message.path
        else:
            self.app.update_preview()


class PreviewPane(Static):
    # ... The rest of the file is unchanged and correct ...
    def __init__(self):
        super().__init__(id="preview")
        self.current_theme = "monokai"
        self.repo: Optional[git.Repo] = None
    async def update_preview(self, path: Optional[Path]) -> None:
        self.repo = self.app.repo
        if path is None:
            await self.remove_children()
            self.update(Panel("Select a file to see details.", border_style="dim"))
            return
        await self.remove_children()
        status, _ = get_file_git_status(path, self.repo)
        with TabbedContent(id="preview-tabs") as tabs:
            with TabPane("Preview", id="tab-preview"):
                yield self._render_info_panel(path)
            if status == "M":
                with TabPane("Git Diff", id="tab-diff"):
                    yield self._render_diff_panel(path)
    def _render_info_panel(self, path: Path) -> Widget:
        try:
            if path.is_dir(): return self._show_metadata(path, "Directory Info")
            elif is_likely_text_file(path): return self._show_text_preview(path)
            else: return self._show_metadata(path, "Binary File Info")
        except Exception as e: return Panel(Text(f"Error previewing file:\n{e}", style="bold red"), title="Error")
    def _render_diff_panel(self, path: Path) -> Widget:
        if not self.repo: return Static("Not in a Git repository.")
        try:
            rel_path = path.relative_to(self.repo.working_dir)
            diff_text = self.repo.git.diff('HEAD', '--', str(rel_path))
            return VerticalScroll(*[GitDiffLine(line) for line in diff_text.splitlines()], id="diff-view")
        except Exception as e: return Static(f"Could not get diff: {e}")
    def _show_metadata(self, path: Path, title: str):
        metadata = get_file_metadata(path)
        table = Table(box=None, expand=True, show_header=False)
        table.add_column(style="bold cyan")
        table.add_column()
        for key, value in metadata.items(): table.add_row(key, value)
        return Panel(table, title=title, border_style="blue")
    def _show_text_preview(self, path: Path):
        try:
            content = path.read_text(encoding="utf-8")
            syntax = Syntax(content, path.name, theme=self.current_theme, line_numbers=True)
            return Panel(syntax, title=path.name, border_style="green")
        except Exception as e: return Panel(f"Error reading file: {e}", title="Error", border_style="red")