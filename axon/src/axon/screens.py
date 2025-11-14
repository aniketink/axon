# screens.py

from typing import Callable, Dict, Any, Tuple

from textual.app import ComposeResult
from textual.screen import ModalScreen
from textual.widgets import Static, Button, Input, ListView, ListItem, Label
from textual.containers import Vertical, Horizontal
from rich.text import Text
from rich.panel import Panel

class HelpScreen(ModalScreen):
    def compose(self) -> ComposeResult:
        content = """
Axon v2.0 - A Miller Column File Navigator
(Press any key to close)

[bold]Navigation[/]
  [yellow]j / ↓[/]      - Move down
  [yellow]k / ↑[/]      - Move up
  [yellow]l / →[/]      - Go to child directory / Focus next column
  [yellow]h / ←[/]      - Go to parent directory / Focus previous column
  [yellow]Backspace[/] - Go back in history
  [yellow]g[/]          - Go to top
  [yellow]G[/]          - Go to bottom

[bold]File Operations[/]
  [yellow]space[/]      - Toggle selection on current item
  [yellow]c[/]          - Create new file
  [yellow]d[/]          - Create new directory
  [yellow]r[/]          - Rename selected item
  [yellow]x[/]          - Delete selected item(s)

[bold]Application[/]
  [yellow]b[/]          - Show bookmarks
  [yellow].[/]          - Toggle hidden files
  [yellow]t[/]          - Cycle syntax theme
  [yellow]Ctrl+P[/]    - Open command palette
  [yellow]q / Ctrl+C[/] - Quit Axon
        """
        yield Vertical(
            Static(Panel(content, title="Keybindings", border_style="green")),
            id="help-container"
        )
    def on_key(self, event) -> None: self.app.pop_screen()

class ConfirmationScreen(ModalScreen[bool]):
    def __init__(self, prompt: str) -> None:
        super().__init__()
        self.prompt = prompt
    def compose(self) -> ComposeResult:
        yield Vertical(Label(self.prompt, id="confirmation-prompt"), Horizontal(Button("Yes", variant="error", id="confirm-yes"), Button("No", variant="primary", id="confirm-no"), id="confirmation-buttons"), id="confirmation-dialog")
    def on_button_pressed(self, event: Button.Pressed) -> None: self.dismiss(event.button.id == "confirm-yes")

class InputScreen(ModalScreen[str]):
    def __init__(self, prompt: str, initial_value: str = "") -> None:
        super().__init__()
        self.prompt = prompt
        self.initial_value = initial_value
    def compose(self) -> ComposeResult:
        yield Vertical(Label(self.prompt), Input(value=self.initial_value, id="text-input-field"), id="input-dialog")
    def on_mount(self) -> None: self.query_one(Input).focus()
    def on_input_submitted(self, event: Input.Submitted) -> None: self.dismiss(event.value)

class BookmarksScreen(ModalScreen[str]):
    def __init__(self, bookmarks: Dict[str, str]) -> None:
        super().__init__()
        self.bookmarks = bookmarks
    def compose(self) -> ComposeResult:
        items = [ListItem(Label(f"{name}: {path}")) for name, path in self.bookmarks.items()]
        yield Vertical(Label("Bookmarks"), ListView(*items, id="bookmark-list"), id="bookmarks-dialog")
    
    # vvv FIX: Correctly access the Label's content by casting its .renderable property vvv
    def on_list_view_selected(self, event: ListView.Selected) -> None:
        selected_text = str(event.item.query_one(Label).renderable)
        name = selected_text.split(":")[0]
        path = self.bookmarks.get(name)
        if path:
            self.dismiss(path)
        else:
            self.app.pop_screen()

class CommandPalette(ModalScreen[str]):
    # ... (This class is unchanged and correct) ...
    def __init__(self, commands: Dict[str, Tuple[str, str, Callable]]) -> None:
        super().__init__()
        self.commands = commands; self.command_list = [(k, d[0], d[1]) for k, d in commands.items()]
    def compose(self) -> ComposeResult:
        yield Vertical(Input(placeholder="Type a command...", id="command-input"), ListView(id="command-list"), id="command-palette")
    def on_mount(self) -> None: self.query_one("#command-input").focus(); self.update_list("")
    def on_input_changed(self, event: Input.Changed) -> None: self.update_list(event.value)
    def on_list_view_selected(self, event: ListView.Selected) -> None: 
        if event.item and event.item.id: self.dismiss(event.item.id)
    def on_input_submitted(self, event: Input.Submitted) -> None:
        if (children := self.query_one(ListView).children) and children and children[0].id: self.dismiss(children[0].id)
    def update_list(self, term: str) -> None:
        lv = self.query_one(ListView); lv.clear(); term = term.lower()
        for k, l, d in self.command_list:
            if term in l.lower() or term in d.lower():
                lv.append(ListItem(Label(Text.assemble((f"{l}", "bold"), (f" - {d}", "dim"))), id=k))