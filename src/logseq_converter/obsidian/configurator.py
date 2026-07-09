import json
from pathlib import Path
from logseq_converter.utils import log_progress, log_warning


def configure_core_vault(destination: Path) -> None:
    """
    Bootstraps the core configuration of the Obsidian vault.
    Creates .obsidian folder, enables core plugins, and sets up Daily Notes configuration.
    """
    obsidian_dir = destination / ".obsidian"
    obsidian_dir.mkdir(parents=True, exist_ok=True)

    # 1. Setup core-plugins.json
    core_plugins_path = obsidian_dir / "core-plugins.json"
    default_core_plugins = {
        "file-explorer": True,
        "global-search": True,
        "switcher": True,
        "graph": True,
        "backlink": True,
        "canvas": True,
        "outgoing-link": True,
        "tag-pane": True,
        "properties": True,
        "page-preview": True,
        "daily-notes": True,
        "templates": True,
        "command-palette": True,
        "bookmarks": True,
        "outline": True,
        "word-count": True,
        "file-recovery": True
    }

    # If it exists, merge to preserve any user settings while ensuring daily-notes is True
    current_core_plugins = {}
    if core_plugins_path.exists():
        try:
            with open(core_plugins_path, "r", encoding="utf-8") as f:
                current_core_plugins = json.load(f)
        except Exception as e:
            log_warning(f"Failed to read existing core-plugins.json: {e}")

    # Merge: existing overrides defaults, but force daily-notes and key explorer features to True
    merged_core_plugins = {**default_core_plugins, **current_core_plugins}
    merged_core_plugins["daily-notes"] = True

    try:
        with open(core_plugins_path, "w", encoding="utf-8") as f:
            json.dump(merged_core_plugins, f, indent=2)
        log_progress("Configured Obsidian core plugins.")
    except Exception as e:
        log_warning(f"Failed to write core-plugins.json: {e}")

    # 2. Setup daily-notes.json (core plugin config)
    daily_notes_config_path = obsidian_dir / "daily-notes.json"
    default_daily_notes_config = {
        "format": "YYYY-MM-DD",
        "folder": "Daily",
        "autorun": False
    }

    current_daily_notes_config = {}
    if daily_notes_config_path.exists():
        try:
            with open(daily_notes_config_path, "r", encoding="utf-8") as f:
                current_daily_notes_config = json.load(f)
        except Exception as e:
            log_warning(f"Failed to read existing daily-notes.json: {e}")

    merged_daily_notes_config = {**default_daily_notes_config, **current_daily_notes_config}
    # Ensure folder and format match our conversion output
    merged_daily_notes_config["folder"] = "Daily"
    merged_daily_notes_config["format"] = "YYYY-MM-DD"

    try:
        with open(daily_notes_config_path, "w", encoding="utf-8") as f:
            json.dump(merged_daily_notes_config, f, indent=2)
        log_progress("Configured Obsidian Daily Notes plugin.")
    except Exception as e:
        log_warning(f"Failed to write daily-notes.json: {e}")
