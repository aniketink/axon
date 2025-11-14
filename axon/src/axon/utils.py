# utils.py

import os
import stat
from pathlib import Path
from datetime import datetime
from typing import Optional, Dict, Union

import chardet
import git
import humanize
from rich.text import Text

# --- Constants: Icons and Colors ---

FILE_ICONS: Dict[str, Text] = {
    "dir": Text("", style="bold #FFB86C"),
    ".git": Text("", style="bold #F1502F"),
    ".gitignore": Text("", style="bold #F1502F"),
    ".py": Text("", style="bold #3776AB"),
    ".js": Text("", style="bold #F7DF1E"),
    ".html": Text("", style="bold #E34F26"),
    ".css": Text("", style="bold #1572B6"),
    ".md": Text("", style="bold #FFFFFF"),
    ".json": Text("ﬥ", style="bold #FBC02D"),
    ".yml": Text("ﬥ", style="bold #CB171E"),
    ".png": Text("", style="bold #89C4F4"),
    ".jpg": Text("", style="bold #89C4F4"),
    ".zip": Text("", style="bold #F4D03F"),
    "file": Text("", style="bold #F8F8F2"),
}

GIT_STATUS_ICONS: Dict[str, Text] = {
    "M": Text("M", style="bold yellow"),
    "A": Text("A", style="bold green"),
    "D": Text("D", style="bold red"),
    "R": Text("R", style="bold blue"),
    "C": Text("C", style="bold blue"),
    "U": Text("U", style="bold red"),
    "??": Text("?", style="bold #BD93F9"),
    "GIT_DIFF_ADD": Text("+", style="bold green"),
    "GIT_DIFF_REMOVE": Text("-", style="bold red"),
}

def get_git_repo(path: Path) -> Optional[git.Repo]:
    try:
        return git.Repo(str(path), search_parent_directories=True)
    except (git.exc.InvalidGitRepositoryError, git.exc.NoSuchPathError):
        return None

def get_file_git_status(path: Path, repo: Optional[git.Repo]) -> tuple[str, Text]:
    if not repo or not repo.working_dir:
        return "", Text("")

    try:
        rel_path = path.relative_to(repo.working_dir)
        str_rel_path = str(rel_path)

        if str_rel_path in repo.untracked_files:
            return "??", GIT_STATUS_ICONS["??"]

        if repo.is_dirty():
            diffs = repo.index.diff(None)
            for diff in diffs:
                if diff.a_path == str_rel_path:
                    return diff.change_type, GIT_STATUS_ICONS.get(diff.change_type, Text(""))
    except Exception:
        return "", Text("")
    return "", Text("")

def make_file_display(path: Path, repo: Optional[git.Repo]) -> Text:
    if path.is_dir():
        icon = FILE_ICONS["dir"]
    else:
        icon = FILE_ICONS.get(path.suffix.lower(), FILE_ICONS["file"])

    _, git_status_icon = get_file_git_status(path, repo)
    
    display_text = Text.assemble(icon, " ", path.name)
    if git_status_icon:
        display_text.append(" ").append(git_status_icon)
    
    return display_text

def is_likely_text_file(path: Path) -> bool:
    text_extensions = {'.txt', '.md', '.py', '.js', '.html', '.css', '.json', '.xml', '.yml', '.yaml', '.toml', '.ini', '.cfg', '.log', '.sh', '.bat', '.c', '.cpp', '.h', '.hpp', '.java', '.go', '.rs', '.rb', '.php'}
    if path.suffix.lower() in text_extensions:
        return True
    try:
        with open(path, "rb") as f:
            chunk = f.read(4096)
            if not chunk: return True
            if b'\0' in chunk: return False
        return True
    except (IOError, OSError):
        return False

def get_file_metadata(path: Path) -> Dict[str, Union[str, Text]]:
    try:
        st = path.stat()
        perms = stat.filemode(st.st_mode)
        return {
            "Size": humanize.naturalsize(st.st_size),
            "Permissions": colorize_permissions(perms),
            "Modified": datetime.fromtimestamp(st.st_mtime).strftime("%Y-%m-%d %H:%M:%S"),
            "Owner": path.owner(),
            "Group": path.group(),
        }
    except Exception:
        # Graceful degradation for systems that don't support owner/group
        st = path.stat()
        perms = stat.filemode(st.st_mode)
        return {
            "Size": humanize.naturalsize(st.st_size),
            "Permissions": colorize_permissions(perms),
            "Modified": datetime.fromtimestamp(st.st_mtime).strftime("%Y-%m-%d %H:%M:%S"),
        }


def colorize_permissions(perms_string: str) -> Text:
    text = Text()
    parts = [
        (perms_string[0], "dim"),
        (perms_string[1], "green" if perms_string[1] == 'r' else "dim"),
        (perms_string[2], "yellow" if perms_string[2] == 'w' else "dim"),
        (perms_string[3], "bold red" if perms_string[3] == 'x' else "dim"),
        (perms_string[4], "green" if perms_string[4] == 'r' else "dim"),
        (perms_string[5], "yellow" if perms_string[5] == 'w' else "dim"),
        (perms_string[6], "bold red" if perms_string[6] == 'x' else "dim"),
        (perms_string[7], "green" if perms_string[7] == 'r' else "dim"),
        (perms_string[8], "yellow" if perms_string[8] == 'w' else "dim"),
        (perms_string[9], "bold red" if perms_string[9] == 'x' else "dim"),
    ]
    for char, style in parts:
        text.append(char, style=style)
    return text