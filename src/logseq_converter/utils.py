import shutil
import sys
from pathlib import Path


def validate_output_directory(path: Path) -> None:
    """
    Validates that the output directory is empty if it exists.
    Raises FileExistsError if not empty.
    """
    if path.exists() and any(path.iterdir()):
        raise FileExistsError(f"Output directory '{path}' is not empty.")

def copy_assets(source_assets: Path, dest_assets: Path) -> None:
    """
    Copies assets from source to destination.
    """
    if not source_assets.exists():
        return
    
    if not dest_assets.exists():
        dest_assets.mkdir(parents=True)
        
    for item in source_assets.iterdir():
        if item.is_file():
            shutil.copy2(item, dest_assets / item.name)
        elif item.is_dir():
            shutil.copytree(item, dest_assets / item.name, dirs_exist_ok=True)

def log_progress(message: str) -> None:
    """
    Logs progress to stderr.
    """
    sys.stderr.write(f"{message}\n")
    sys.stderr.flush()

def log_warning(message: str) -> None:
    """
    Logs a warning to stderr.
    """
    sys.stderr.write(f"WARNING: {message}\n")
    sys.stderr.flush()

def sanitize_filename(filename: str) -> str:
    """
    Sanitizes a filename to be safe for file systems.
    """
    # Basic sanitization, can be improved
    return "".join(
        c for c in filename if c.isalnum() or c in (' ', '.', '_', '-')
    ).strip()

def handle_filename_collision(path: Path) -> Path:
    """
    Handles filename collisions by appending a unique suffix.
    """
    if not path.exists():
        return path
        
    stem = path.stem
    suffix = path.suffix
    parent = path.parent
    counter = 1
    
    while True:
        new_path = parent / f"{stem}_{counter}{suffix}"
        if not new_path.exists():
            return new_path
        counter += 1
