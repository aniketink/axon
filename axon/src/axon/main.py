# main.py

import os
import shutil
from collections import deque
from pathlib import Path
from typing import Set

from textual.app import App, ComposeResult
from textual.binding import Binding
from textual.widgets import Header, Footer
from textual.containers import Horizontal

from screens import HelpScreen, ConfirmationScreen, InputScreen, BookmarksScreen, CommandPalette
from views import MillerColumns, PreviewPane, DirectoryBrowser
from widgets import DirectoryItem
from utils import get_git_repo

class Axon(App):
    CSS_PATH = "style.css"
    TITLE = "Axon v2.0"
    
    BINDINGS = [
        Binding("q", "quit", "Quit", priority=True),
        Binding("?", "show_help", "Help"),
        Binding("h,left", "nav_back", "Back/Parent"),
        Binding("l,right", "nav_forward", "Forward/Child"),
        Binding("backspace", "history_back", "History Back"),
        Binding(".", "toggle_hidden", "Toggle Hidden"),
        Binding("space", "toggle_selection", "Select Item"),
        Binding("b", "show_bookmarks", "Bookmarks"),
        Binding("t", "cycle_theme", "Cycle Theme"),
        Binding("c", "create_file", "New File"),
        Binding("d", "create_directory", "New Dir"),
        Binding("r", "rename_item", "Rename"),
        Binding("x", "delete_item", "Delete"),
        Binding("ctrl+p", "show_command_palette", "Commands"),
    ]

    def __init__(self):
        super().__init__()
        self.history = deque(maxlen=32)
        self.show_hidden = False
        self.syntax_themes = ["monokai", "solarized-dark", "dracula", "github-dark"]
        self.current_theme_index = 0
        self.bookmarks = {"Home": str(Path.home()), "Projects": str(Path.home() / "Projects")}
        self.repo = None
        self.selected_path: Path | None = None

    def compose(self) -> ComposeResult:
        yield Header()
        with Horizontal(id="main-container"):
            # vvv FIX: Compose an empty MillerColumns. It will be populated in on_mount. vvv
            yield MillerColumns(id="miller-columns")
            yield PreviewPane()
        yield Footer()

    def on_mount(self) -> None:
        """Called when the app is first mounted."""
        # vvv FIX: This now kicks off the initial render of the MillerColumns. vvv
        self.set_current_path(Path(os.getcwd()))

    def set_current_path(self, path: Path):
        resolved_path = path.resolve()
        if not resolved_path.is_dir():
            self.selected_path = resolved_path
            resolved_path = resolved_path.parent
        else:
            self.selected_path = None
        
        self.repo = get_git_repo(resolved_path)
        self.query_one(MillerColumns).path = resolved_path
        self.sub_title = str(resolved_path)
        self.update_preview()

    def update_preview(self):
        self.call_after_refresh(self.query_one(PreviewPane).update_preview, self.selected_path)

    # ... The rest of the actions are unchanged and correct ...
    def action_nav_back(self) -> None:
        focused = self.focused
        if isinstance(focused, DirectoryBrowser) and focused.id != "browser-0":
            prev_browser = self.query(DirectoryBrowser)[self.query(DirectoryBrowser).index(focused) - 1]
            prev_browser.focus()
        else:
            miller = self.query_one(MillerColumns)
            if miller.path != Path("/"):
                self.history.append(miller.path)
                self.set_current_path(miller.path.parent)

    def action_nav_forward(self) -> None:
        focused = self.focused
        if isinstance(focused, DirectoryBrowser):
            try:
                next_browser = self.query(DirectoryBrowser)[self.query(DirectoryBrowser).index(focused) + 1]
                next_browser.focus()
            except IndexError:
                if focused.highlighted_child and isinstance(focused.highlighted_child, DirectoryItem) and focused.highlighted_child.path.is_dir():
                     self.set_current_path(focused.highlighted_child.path)


    def action_history_back(self) -> None:
        if self.history: self.set_current_path(self.history.pop())

    def action_toggle_hidden(self) -> None:
        self.show_hidden = not self.show_hidden
        self.notify(f"Show hidden files: {'ON' if self.show_hidden else 'OFF'}")
        self.set_current_path(self.query_one(MillerColumns).path)

    def action_toggle_selection(self) -> None:
        focused = self.focused
        if isinstance(focused, DirectoryBrowser) and isinstance(focused.highlighted_child, DirectoryItem):
            focused.toggle_selection(focused.highlighted_child.path)
    
    def action_delete_item(self) -> None:
        to_delete: Set[Path] = set()
        for browser in self.query(DirectoryBrowser):
            to_delete.update(browser.selected_paths)
        
        if not to_delete and self.selected_path:
            to_delete.add(self.selected_path)

        if not to_delete:
            self.notify("No file selected for deletion.", severity="warning")
            return
        
        item_list = list(to_delete)
        prompt = f"Delete '{item_list[0].name}'?" if len(item_list) == 1 else f"Delete {len(item_list)} items?"

        def on_confirm(confirmed: bool):
            if confirmed:
                deleted_count = 0
                for path in item_list:
                    try:
                        if path.is_dir(): shutil.rmtree(path)
                        else: os.remove(path)
                        deleted_count +=1
                    except Exception as e:
                        self.notify(f"Error deleting {path.name}: {e}", severity="error")
                self.set_current_path(self.query_one(MillerColumns).path)
                self.notify(f"Deleted {deleted_count} items.")
        
        self.push_screen(ConfirmationScreen(prompt), on_confirm)

    def action_quit(self) -> None: self.exit()
    def action_show_help(self) -> None: self.push_screen(HelpScreen())
    def action_show_bookmarks(self) -> None: self.push_screen(BookmarksScreen(self.bookmarks), lambda p: self.set_current_path(Path(p)) if p else None)
    
    def action_cycle_theme(self) -> None:
        self.current_theme_index = (self.current_theme_index + 1) % len(self.syntax_themes)
        self.query_one(PreviewPane).current_theme = self.syntax_themes[self.current_theme_index]
        self.notify(f"Syntax theme: {self.syntax_themes[self.current_theme_index]}")
        self.update_preview()

def run_app():
    """Main entry point for the runnable script."""
    Axon().run()

if __name__ == "__main__":
    run_app()