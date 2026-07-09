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


def enable_community_plugin(destination: Path, plugin_id: str) -> None:
    """
    Enables a community plugin by adding its ID to community-plugins.json.
    """
    obsidian_dir = destination / ".obsidian"
    obsidian_dir.mkdir(parents=True, exist_ok=True)

    community_plugins_path = obsidian_dir / "community-plugins.json"

    enabled_plugins = []
    if community_plugins_path.exists():
        try:
            with open(community_plugins_path, "r", encoding="utf-8") as f:
                enabled_plugins = json.load(f)
                if not isinstance(enabled_plugins, list):
                    enabled_plugins = []
        except Exception as e:
            log_warning(f"Failed to read existing community-plugins.json: {e}")

    if plugin_id not in enabled_plugins:
        enabled_plugins.append(plugin_id)

    try:
        with open(community_plugins_path, "w", encoding="utf-8") as f:
            json.dump(enabled_plugins, f, indent=2)
    except Exception as e:
        log_warning(f"Failed to write community-plugins.json: {e}")


def install_community_plugin(destination: Path, plugin_id: str, repo: str) -> None:
    """
    Downloads the latest release of an Obsidian community plugin from GitHub
    and places the main.js, manifest.json, and styles.css into the vault.
    """
    import ssl
    import urllib.error
    import urllib.request

    plugin_dir = destination / ".obsidian" / "plugins" / plugin_id
    plugin_dir.mkdir(parents=True, exist_ok=True)

    api_url = f"https://api.github.com/repos/{repo}/releases/latest"
    req = urllib.request.Request(
        api_url,
        headers={"User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36"}
    )

    ctx = ssl.create_default_context()
    ctx.check_hostname = False
    ctx.verify_mode = ssl.CERT_NONE

    try:
        log_progress(f"Fetching latest release metadata for '{plugin_id}' from GitHub...")
        with urllib.request.urlopen(req, context=ctx) as response:
            release_info = json.loads(response.read().decode("utf-8"))

        assets = release_info.get("assets", [])

        # Download files
        downloaded_count = 0
        for asset in assets:
            name = asset.get("name")
            download_url = asset.get("browser_download_url")

            # We only care about main.js, manifest.json, and styles.css
            if name in {"main.js", "manifest.json", "styles.css"}:
                asset_req = urllib.request.Request(
                    download_url,
                    headers={"User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36"}
                )
                log_progress(f"Downloading {name} for {plugin_id}...")
                with urllib.request.urlopen(asset_req, context=ctx) as asset_response:
                    content = asset_response.read()
                    with open(plugin_dir / name, "wb") as f:
                        f.write(content)
                downloaded_count += 1

        if downloaded_count == 0:
            log_warning(f"No valid assets found to download for plugin '{plugin_id}' in {api_url}")
            return

        # Create/update data.json with defaults
        data_json_path = plugin_dir / "data.json"
        if not data_json_path.exists():
            with open(data_json_path, "w", encoding="utf-8") as f:
                json.dump({}, f)

        # Enable plugin
        enable_community_plugin(destination, plugin_id)
        log_progress(f"Plugin '{plugin_id}' installed and enabled successfully.")

    except urllib.error.URLError as e:
        log_warning(f"Network error downloading plugin '{plugin_id}': {e}")
    except Exception as e:
        log_warning(f"Error installing plugin '{plugin_id}': {e}")


def configure_community_plugins(destination: Path) -> None:
    """
    Configures community plugins for the Obsidian vault.
    Installs Notebook Navigator as required.
    """
    # Install notebook-navigator
    install_community_plugin(destination, "notebook-navigator", "johansan/notebook-navigator")

