import argparse
import dataclasses
import json
import os
import sys
import time
from pathlib import Path

from logseq_converter.blinko import BlinkoClient, BlinkoConverter
from logseq_converter.logseq.parser import BlockReferenceScanner, LogSeqParser
from logseq_converter.obsidian.converter import ObsidianConverter
from logseq_converter.stats import ConversionStats
from logseq_converter.tana.converter import TanaConverter
from logseq_converter.utils import (
    copy_assets,
    is_markdown_empty,
    log_progress,
    log_warning,
    trim_empty_bullets,
    validate_logseq_source,
    validate_output_directory,
)


def convert_vault(
    source: Path,
    destination: Path,
    verbose: bool,
    dry_run: bool = False,
    clear_llm_cache: bool = False,
) -> int:
    try:
        validate_logseq_source(source)
    except (FileNotFoundError, NotADirectoryError, ValueError) as e:
        log_warning(str(e))
        return 1

    # Validate LogSeq directory structure
    pages_dir = source / "pages"
    journals_dir = source / "journals"

    try:
        validate_output_directory(destination)
    except FileExistsError as e:
        log_warning(str(e))
        return 1

    if dry_run:
        log_progress("Dry run enabled. No changes will be written.")

    log_progress(f"Converting '{source}' to '{destination}'...")

    # Pass 1: Scan for block IDs
    log_progress("Scanning for block IDs...")
    scanner = BlockReferenceScanner()

    # Walk source to scan
    for root, _, files in os.walk(source):
        for file in files:
            if file.endswith(".md"):
                scanner.scan_file(Path(root) / file)

    # Initialize stats
    stats = ConversionStats()

    converter = ObsidianConverter(scanner, stats, env=os.environ)
    if clear_llm_cache:
        converter.llm_generator.clear_cache()

    # Create destination directory
    if not destination.exists() and not dry_run:
        destination.mkdir(parents=True)

    # Copy assets
    assets_src = source / "assets"
    assets_dest = destination / "assets"
    if assets_src.exists():
        log_progress("Copying assets...")
        if not dry_run:
            copy_assets(assets_src, assets_dest)

        # Count assets
        stats.assets = sum(1 for _ in assets_src.glob("*") if _.is_file())

    # Process files
    log_progress("Processing files...")

    # Process journals
    _process_journals(journals_dir, destination, converter, verbose, dry_run)

    # Process pages
    _process_pages(pages_dir, destination, converter, verbose, dry_run)

    # Configure vault core settings and plugins
    if not dry_run:
        from logseq_converter.obsidian.configurator import configure_community_plugins, configure_core_vault
        configure_core_vault(destination)
        configure_community_plugins(destination)

    log_progress("Conversion complete.")

    # Output statistics
    print("\nConversion Statistics:")
    print(f"  Journals: {stats.journals}")
    print(f"  Pages: {stats.pages}")
    print(f"  Assets: {stats.assets}")
    print(f"  Block References: {stats.block_refs}")
    print(f"  Links: {stats.links}")
    print(f"  Learnings: {stats.learnings}")
    print(f"  Achievements: {stats.achievements}")
    print(f"  Highlights: {stats.highlights}")

    return 0


def _process_journals(
    journals_dir: Path,
    destination: Path,
    converter: ObsidianConverter,
    verbose: bool,
    dry_run: bool,
) -> None:
    if not journals_dir.exists():
        return

    all_extracted_files = []

    for file_path in journals_dir.glob("*.md"):
        try:
            if verbose:
                log_progress(f"Processing journal: {file_path.name}")
            dest_rel_path = converter.transform_journal_filename(file_path.name)
            if dest_rel_path:
                dest_path = destination / dest_rel_path
                if not dry_run:
                    dest_path.parent.mkdir(parents=True, exist_ok=True)

                with open(file_path, "r", encoding="utf-8") as f:
                    content = f.read()

                content = trim_empty_bullets(content)

                # Extract sections (US3)
                content, extracted_files = converter.extract_sections(content, file_path.name)

                # Collect extracted files for batch processing later
                all_extracted_files.extend(extracted_files)

                converted_content = converter.convert_content(content)

                # Skip writing journal file if it's empty after extraction
                if not is_markdown_empty(converted_content):
                    if not dry_run:
                        with open(dest_path, "w", encoding="utf-8") as f:
                            f.write(converted_content)
                    converter.stats.journals += 1
                elif verbose:
                    log_progress(f"Skipping empty journal after extraction: {file_path.name}")
            else:
                log_warning(f"Skipping unrecognized journal file: {file_path.name}")
        except Exception as e:
            log_warning(f"Error processing journal {file_path.name}: {e}")
            continue

    # Resolve all placeholder filenames in batch
    resolved_files = converter.llm_generator.resolve_placeholders(all_extracted_files)

    from logseq_converter.utils import handle_filename_collision

    # Save resolved files
    for filename, file_content in resolved_files:
        extracted_path = destination / filename
        extracted_path = handle_filename_collision(extracted_path)
        if not dry_run:
            extracted_path.parent.mkdir(parents=True, exist_ok=True)
            with open(extracted_path, "w", encoding="utf-8") as f:
                f.write(file_content)



def _process_pages(
    pages_dir: Path,
    destination: Path,
    converter: ObsidianConverter,
    verbose: bool,
    dry_run: bool,
) -> None:
    if not pages_dir.exists():
        return

    for file_path in pages_dir.glob("*.md"):
        try:
            if verbose:
                log_progress(f"Processing page: {file_path.name}")
            dest_rel_path = converter.transform_page_filename(file_path.name)
            dest_path = destination / dest_rel_path
            if not dry_run:
                dest_path.parent.mkdir(parents=True, exist_ok=True)

            with open(file_path, "r", encoding="utf-8") as f:
                content = f.read()

            content = trim_empty_bullets(content)

            converted_content = converter.convert_content(content)

            if not dry_run:
                with open(dest_path, "w", encoding="utf-8") as f:
                    f.write(converted_content)
            converter.stats.pages += 1
        except Exception as e:
            log_warning(f"Error processing page {file_path.name}: {e}")
            continue


def convert_to_tana(source: Path, destination: Path, verbose: bool, force: bool, dry_run: bool = False) -> int:
    try:
        validate_logseq_source(source)
    except (FileNotFoundError, NotADirectoryError, ValueError) as e:
        log_warning(str(e))
        return 1

    # Validate destination file
    if destination.exists() and not force:
        log_warning(f"Destination file '{destination}' already exists. Use --force to overwrite.")
        return 1

    if dry_run:
        log_progress("Dry run enabled. No changes will be written.")

    log_progress(f"Converting '{source}' to '{destination}' (Tana format)...")

    # Ensure parent directory exists
    if not dry_run:
        destination.parent.mkdir(parents=True, exist_ok=True)

    parser = LogSeqParser()
    converter = TanaConverter()
    all_nodes = []

    # Process pages
    pages_dir = source / "pages"
    if pages_dir.exists():
        for file_path in pages_dir.glob("*.md"):
            try:
                if verbose:
                    log_progress(f"Processing page: {file_path.name}")

                page = parser.parse(file_path)
                if not page:
                    continue

                tana_node = converter.convert_page(page)
                all_nodes.append(tana_node)

            except Exception as e:
                log_warning(f"Error processing page {file_path.name}: {e}")

    # Process journals
    journals_dir = source / "journals"
    if journals_dir.exists():
        for file_path in journals_dir.glob("*.md"):
            try:
                if verbose:
                    log_progress(f"Processing journal: {file_path.name}")

                journal = parser.parse(file_path)
                if not journal:
                    continue

                tana_node = converter.convert_page(journal)
                all_nodes.append(tana_node)

            except Exception as e:
                log_warning(f"Error processing journal {file_path.name}: {e}")

    # Create single Tana file
    if all_nodes:
        tana_file = converter.create_tana_file_from_nodes(all_nodes)

        if not dry_run:
            log_progress(f"Writing output to {destination}...")
            with open(destination, "w", encoding="utf-8") as f:
                json.dump(dataclasses.asdict(tana_file), f, indent=2)
    else:
        log_warning("No content found to convert.")

    log_progress("Conversion complete.")
    return 0


def convert_to_blinko(source: Path, endpoint: str, verbose: bool, dry_run: bool = False) -> int:
    try:
        validate_logseq_source(source)
    except (FileNotFoundError, NotADirectoryError, ValueError) as e:
        log_warning(str(e))
        return 1

    token = os.environ.get("BLINKO_TOKEN")
    if not token:
        log_warning("BLINKO_TOKEN environment variable is not set.")
        return 1

    try:
        client = BlinkoClient(endpoint, token)
    except ValueError as e:
        log_warning(f"Invalid configuration: {e}")
        return 1

    if dry_run:
        log_progress("Dry run enabled. No changes will be sent to Blinko.")

    log_progress(f"Converting '{source}' to Blinko at '{endpoint}'...")

    parser = LogSeqParser()
    converter = BlinkoConverter()

    # Process pages
    pages_dir = source / "pages"
    if pages_dir.exists():
        for file_path in pages_dir.glob("*.md"):
            try:
                if verbose:
                    log_progress(f"Processing page: {file_path.name}")

                page = parser.parse(file_path)
                if not page:
                    continue

                content = converter.convert_page(page)

                if not dry_run:
                    client.upsert_note(content)
                    time.sleep(0.1)  # rate limiting courtesy

            except Exception as e:
                log_warning(f"Error processing page {file_path.name}: {e}")

    # Process journals
    journals_dir = source / "journals"
    if journals_dir.exists():
        for file_path in journals_dir.glob("*.md"):
            try:
                if verbose:
                    log_progress(f"Processing journal: {file_path.name}")

                journal = parser.parse(file_path)
                if not journal:
                    continue

                content = converter.convert_page(journal)

                if not dry_run:
                    client.upsert_note(content)
                    time.sleep(0.1)

            except Exception as e:
                log_warning(f"Error processing journal {file_path.name}: {e}")

    log_progress("Conversion complete.")
    return 0


def convert_blinko_delete_all(endpoint: str, verbose: bool, dry_run: bool = False) -> int:
    token = os.environ.get("BLINKO_TOKEN")
    if not token:
        log_warning("BLINKO_TOKEN environment variable is not set.")
        return 1

    try:
        client = BlinkoClient(endpoint, token)
    except ValueError as e:
        log_warning(f"Invalid configuration: {e}")
        return 1

    if dry_run:
        log_progress("Dry run enabled. No changes will be sent to Blinko.")

    log_progress(f"Deleting ALL notes from Blinko at '{endpoint}'...")

    def progress_callback(deleted: int, total: int):
        log_progress(f"Deleted {deleted}/{total} notes...")

    total_deleted = client.delete_all(dry_run=dry_run, progress_callback=progress_callback)

    if dry_run:
        log_progress(f"Dry run complete. Would have deleted {total_deleted} notes.")
    else:
        log_progress(f"Successfully deleted {total_deleted} notes.")

    return 0


def create_tolaria_types(destination: Path, dry_run: bool = False) -> None:
    """
    Creates type documents in the destination Tolaria vault's root folder.
    This formally registers entity types (like journal, learning, etc.) in the UI.
    """
    if dry_run:
        return

    # Delete legacy type/ directory if it exists
    legacy_type_dir = destination / "type"
    if legacy_type_dir.exists():
        import shutil
        try:
            shutil.rmtree(legacy_type_dir)
        except Exception as e:
            log_warning(f"Failed to remove legacy type directory: {e}")

    types_config = {
        "journal": {
            "label": "Journal",
            "icon": "📓",
            "_color": "#4f46e5",
            "sort": "title:desc",
            "content": "# \n\n## Plan for the day\n\n- \n\n## Log\n\n- \n"
        },
        "learning": {
            "label": "Learning",
            "icon": "💡",
            "_color": "#eab308",
            "content": "## Summary\n\n- \n\n## Details\n\n- \n"
        },
        "link": {
            "label": "Link",
            "icon": "🔗",
            "_color": "#3b82f6",
            "content": ""
        },
        "achievement": {
            "label": "Achievement",
            "icon": "🏆",
            "_color": "#10b981",
            "content": "- \n"
        },
        "highlight": {
            "label": "Highlight",
            "icon": "✨",
            "_color": "#f43f5e",
            "content": "- \n"
        },
        "project": {
            "label": "Project",
            "icon": "📁",
            "_color": "#ec4899",
            "content": "## Overview\n\n- \n\n## Tasks\n\n- [ ] \n"
        },
        "work": {
            "label": "Work",
            "sidebar_label": "Work",
            "icon": "💼",
            "_color": "#f97316",
            "content": ""
        },
        "meeting": {
            "label": "Meeting",
            "icon": "👥",
            "_color": "#8b5cf6",
            "content": "## Agenda\n\n- \n\n## Notes\n\n- \n\n## Action Items\n\n- [ ] \n"
        },
        "device": {
            "label": "Device",
            "icon": "💻",
            "_color": "#64748b",
            "content": ""
        },
        "server": {
            "label": "Server",
            "icon": "🖥️",
            "_color": "#475569",
            "content": ""
        },
        "upkeep": {
            "label": "Upkeep",
            "sidebar_label": "Upkeep",
            "icon": "🛠️",
            "_color": "#06b6d4",
            "content": ""
        },
        "content-creation": {
            "label": "Content Creation",
            "icon": "🎥",
            "_color": "#d946ef",
            "content": ""
        },
        "restaurant": {
            "label": "Restaurant",
            "icon": "🍴",
            "_color": "#14b8a6",
            "content": ""
        },
        "prompt-template": {
            "label": "Prompt Template",
            "icon": "📝",
            "_color": "#a855f7",
            "content": ""
        },
        "book": {
            "label": "Book",
            "icon": "📖",
            "_color": "#84cc16",
            "content": ""
        },
        "list": {
            "label": "List",
            "icon": "📋",
            "_color": "#06b6d4",
            "content": ""
        }
    }

    for type_name, config in types_config.items():
        type_file = destination / f"type-{type_name}.md"
        # Only write if it does not exist, to avoid overwriting user edits
        if not type_file.exists():
            frontmatter = [
                "---",
                "type: Type",
                f"icon: {config['icon']}",
                f"_color: \"{config['_color']}\"",
            ]
            if "sidebar_label" in config:
                frontmatter.append(f"sidebar_label: {config['sidebar_label']}")
            if "sort" in config:
                frontmatter.append(f"sort: {config['sort']}")
            frontmatter.append("---")
            
            first_header = f"# {config['label']}"
            file_content = "\n".join(frontmatter) + "\n\n" + first_header + "\n\n" + config["content"]
            try:
                with open(type_file, "w", encoding="utf-8") as f:
                    f.write(file_content)
            except Exception as e:
                log_warning(f"Failed to write type note '{type_name}': {e}")


def convert_to_tolaria(
    source: Path,
    destination: Path,
    verbose: bool,
    dry_run: bool = False,
    clear_llm_cache: bool = False,
) -> int:
    try:
        validate_logseq_source(source)
    except (FileNotFoundError, NotADirectoryError, ValueError) as e:
        log_warning(str(e))
        return 1

    try:
        validate_output_directory(destination)
    except FileExistsError as e:
        log_warning(str(e))
        return 1

    if dry_run:
        log_progress("Dry run enabled. No changes will be written.")

    log_progress(f"Converting '{source}' to '{destination}' (Tolaria format)...")

    # Pass 1: Scan for block IDs
    log_progress("Scanning for block IDs...")
    scanner = BlockReferenceScanner()

    # Walk source to scan
    for root, _, files in os.walk(source):
        for file in files:
            if file.endswith(".md"):
                scanner.scan_file(Path(root) / file)

    # Create destination directory
    if not destination.exists() and not dry_run:
        destination.mkdir(parents=True)


    from logseq_converter.tolaria.converter import TolariaConverter
    
    converter = TolariaConverter(scanner=scanner, env=os.environ)
    if clear_llm_cache:
        converter.llm_generator.clear_cache()
    
    stats_pages = 0
    stats_journals = 0

    # Process pages
    pages_dir = source / "pages"
    if pages_dir.exists():
        for file_path in pages_dir.glob("*.md"):
            if converter.should_ignore(file_path.name):
                if verbose:
                    log_progress(f"Ignoring page: {file_path.name}")
                continue
                
            try:
                if verbose:
                    log_progress(f"Processing page: {file_path.name}")
                
                with open(file_path, "r", encoding="utf-8") as f:
                    content = f.read()

                content = trim_empty_bullets(content)

                final_name, final_content = converter.process_metadata(file_path.name, content)
                dest_path = destination / final_name
                
                if not dry_run:
                    with open(dest_path, "w", encoding="utf-8") as f:
                        f.write(final_content)
                stats_pages += 1
            except Exception as e:
                log_warning(f"Error processing page {file_path.name}: {e}")

    # Process journals
    journals_dir = source / "journals"
    if journals_dir.exists():
        # Tolaria expects journals in a 'journal' directory (lowercase, singular)
        journals_dest = destination / "journal"
        if not dry_run and not journals_dest.exists():
            journals_dest.mkdir(parents=True, exist_ok=True)

        all_extracted_files = []

        for file_path in journals_dir.glob("*.md"):
            try:
                if verbose:
                    log_progress(f"Processing journal: {file_path.name}")

                dest_name = converter.transform_journal_filename(file_path.name)

                with open(file_path, "r", encoding="utf-8") as f:
                    content = f.read()

                content = trim_empty_bullets(content)

                remaining_content, properties = converter.extract_and_remove_frontmatter(content)
                properties["type"] = "Journal"

                # Extract sections (learnings, achievements, highlights, links)
                remaining_content, extracted_files = converter.extract_sections(remaining_content, file_path.name)

                # Collect extracted files for batch processing later
                all_extracted_files.extend(extracted_files)

                # Skip writing journal file if it's empty after extraction
                if not is_markdown_empty(remaining_content):
                    transformed_body = converter.convert_content(remaining_content)

                    frontmatter = []
                    frontmatter.append("---")
                    for k, v in properties.items():
                        frontmatter.append(f"{k}: {v}")
                    frontmatter.append("---")

                    final_content = "\n".join(frontmatter) + "\n\n" + transformed_body.strip()
                    final_content = trim_empty_bullets(final_content)

                    dest_path = journals_dest / dest_name
                    if not dry_run:
                        with open(dest_path, "w", encoding="utf-8") as f:
                            f.write(final_content)
                    stats_journals += 1
                elif verbose:
                    log_progress(f"Skipping empty journal after extraction: {file_path.name}")

            except Exception as e:
                log_warning(f"Error processing journal {file_path.name}: {e}")

        # Resolve all placeholder filenames in batch
        resolved_files = converter.llm_generator.resolve_placeholders(all_extracted_files)

        from logseq_converter.utils import handle_filename_collision

        # Save resolved files directly in the root destination directory
        for filename, file_content in resolved_files:
            extracted_path = destination / filename
            extracted_path = handle_filename_collision(extracted_path)
            if not dry_run:
                with open(extracted_path, "w", encoding="utf-8") as f:
                    f.write(file_content)
            stats_pages += 1

    # Create Tolaria metadata types
    create_tolaria_types(destination, dry_run)

    log_progress("Conversion complete.")
    print("\nConversion Statistics:")
    print(f"  Journals: {stats_journals}")
    print(f"  Pages: {stats_pages}")
    print(f"  Block References: {converter.stats_block_refs}")
    print(f"  Links: {converter.stats_links}")
    print(f"  Learnings: {converter.stats_learnings}")
    print(f"  Achievements: {converter.stats_achievements}")
    print(f"  Highlights: {converter.stats_highlights}")
    
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description="Convert LogSeq graph to other formats")
    subparsers = parser.add_subparsers(dest="command", help="Conversion target format")

    # Obsidian command (default/legacy)
    obsidian_parser = subparsers.add_parser("obsidian", help="Convert to Obsidian vault")
    obsidian_parser.add_argument("source", type=Path, help="Source LogSeq graph directory")
    obsidian_parser.add_argument("destination", type=Path, help="Destination Obsidian vault directory")
    obsidian_parser.add_argument("-v", "--verbose", action="store_true", help="Enable verbose logging")
    obsidian_parser.add_argument("--dry-run", action="store_true", help="Perform a dry run without writing changes")
    obsidian_parser.add_argument(
        "--clear-llm-cache", action="store_true", help="Clear global LLM cache before conversion"
    )

    # Tana command
    tana_parser = subparsers.add_parser("tana", help="Convert to Tana Intermediate Format")
    tana_parser.add_argument("source", type=Path, help="Source LogSeq graph directory")
    tana_parser.add_argument("destination", type=Path, help="Destination file path for Tana JSON output")
    tana_parser.add_argument("-v", "--verbose", action="store_true", help="Enable verbose logging")
    tana_parser.add_argument("--dry-run", action="store_true", help="Perform a dry run without writing changes")
    tana_parser.add_argument("-f", "--force", action="store_true", help="Force overwrite of destination file")

    # Tolaria command
    tolaria_parser = subparsers.add_parser("tolaria", help="Convert to Tolaria Markdown Format")
    tolaria_parser.add_argument("source", type=Path, help="Source LogSeq graph directory")
    tolaria_parser.add_argument("destination", type=Path, help="Destination Tolaria vault directory")
    tolaria_parser.add_argument("-v", "--verbose", action="store_true", help="Enable verbose logging")
    tolaria_parser.add_argument("--dry-run", action="store_true", help="Perform a dry run without writing changes")
    tolaria_parser.add_argument(
        "--clear-llm-cache", action="store_true", help="Clear global LLM cache before conversion"
    )

    # Blinko command
    blinko_parser = subparsers.add_parser("blinko", help="Export to Blinko")
    blinko_parser.add_argument("source", type=Path, help="Source LogSeq graph directory")
    blinko_parser.add_argument("endpoint", type=str, help="Blinko API endpoint URL")
    blinko_parser.add_argument("-v", "--verbose", action="store_true", help="Enable verbose logging")
    blinko_parser.add_argument("--dry-run", action="store_true", help="Perform a dry run without sending data")

    # Blinko delete-all command
    blinko_delete_all_parser = subparsers.add_parser("blinko:delete-all", help="Delete ALL notes from Blinko")
    blinko_delete_all_parser.add_argument("endpoint", type=str, help="Blinko API endpoint URL")
    blinko_delete_all_parser.add_argument("-v", "--verbose", action="store_true", help="Enable verbose logging")
    blinko_delete_all_parser.add_argument("--dry-run", action="store_true", help="Perform a dry run without deletion")

    args = parser.parse_args()

    if args.command == "tolaria":
        return convert_to_tolaria(args.source, args.destination, args.verbose, args.dry_run, args.clear_llm_cache)
    elif args.command == "tana":
        return convert_to_tana(args.source, args.destination, args.verbose, args.force, args.dry_run)
    elif args.command == "obsidian":
        return convert_vault(args.source, args.destination, args.verbose, args.dry_run, args.clear_llm_cache)
    elif args.command == "blinko":
        return convert_to_blinko(args.source, args.endpoint, args.verbose, args.dry_run)
    elif args.command == "blinko:delete-all":
        return convert_blinko_delete_all(args.endpoint, args.verbose, args.dry_run)
    else:
        # Default to obsidian if no subcommand provided (backward compatibility)
        # However, argparse might require subcommand if configured.
        # Let's check if we can support implicit obsidian command or just print help.
        # For now, let's just print help if no command.
        parser.print_help()
        return 1


if __name__ == "__main__":
    sys.exit(main())
