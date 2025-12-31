import argparse
import dataclasses
import json
import os
import sys
from pathlib import Path

from logseq_converter.logseq.parser import BlockReferenceScanner, LogSeqParser
from logseq_converter.obsidian.converter import ObsidianConverter
from logseq_converter.stats import ConversionStats
from logseq_converter.tana.converter import TanaConverter
from logseq_converter.utils import (
    copy_assets,
    is_markdown_empty,
    log_progress,
    log_warning,
    validate_logseq_source,
    validate_output_directory,
)


def convert_vault(source: Path, destination: Path, verbose: bool, dry_run: bool = False) -> int:
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

    converter = ObsidianConverter(scanner, stats)

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

                # Extract sections (US3)
                content, extracted_files = converter.extract_sections(content, file_path.name)

                # Save extracted files (empty files already filtered by converter)
                for filename, file_content in extracted_files:
                    extracted_path = destination / filename
                    if not dry_run:
                        extracted_path.parent.mkdir(parents=True, exist_ok=True)
                        with open(extracted_path, "w", encoding="utf-8") as f:
                            f.write(file_content)

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


def main() -> int:
    parser = argparse.ArgumentParser(description="Convert LogSeq graph to other formats")
    subparsers = parser.add_subparsers(dest="command", help="Conversion target format")

    # Obsidian command (default/legacy)
    obsidian_parser = subparsers.add_parser("obsidian", help="Convert to Obsidian vault")
    obsidian_parser.add_argument("source", type=Path, help="Source LogSeq graph directory")
    obsidian_parser.add_argument("destination", type=Path, help="Destination Obsidian vault directory")
    obsidian_parser.add_argument("-v", "--verbose", action="store_true", help="Enable verbose logging")
    obsidian_parser.add_argument("--dry-run", action="store_true", help="Perform a dry run without writing changes")

    # Tana command
    tana_parser = subparsers.add_parser("tana", help="Convert to Tana Intermediate Format")
    tana_parser.add_argument("source", type=Path, help="Source LogSeq graph directory")
    tana_parser.add_argument("destination", type=Path, help="Destination file path for Tana JSON output")
    tana_parser.add_argument("-v", "--verbose", action="store_true", help="Enable verbose logging")
    tana_parser.add_argument("--dry-run", action="store_true", help="Perform a dry run without writing changes")
    tana_parser.add_argument("-f", "--force", action="store_true", help="Force overwrite of destination file")

    args = parser.parse_args()

    if args.command == "tana":
        return convert_to_tana(args.source, args.destination, args.verbose, args.force, args.dry_run)
    elif args.command == "obsidian":
        return convert_vault(args.source, args.destination, args.verbose, args.dry_run)
    else:
        # Default to obsidian if no subcommand provided (backward compatibility)
        # However, argparse might require subcommand if configured.
        # Let's check if we can support implicit obsidian command or just print help.
        # For now, let's just print help if no command.
        parser.print_help()
        return 1


if __name__ == "__main__":
    sys.exit(main())
