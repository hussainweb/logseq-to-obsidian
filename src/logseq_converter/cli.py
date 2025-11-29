import argparse
import os
import sys
from pathlib import Path

from logseq_converter.logseq.parser import BlockReferenceScanner
from logseq_converter.obsidian.converter import ObsidianConverter
from logseq_converter.stats import ConversionStats
from logseq_converter.utils import (
    copy_assets,
    is_markdown_empty,
    log_progress,
    log_warning,
    validate_output_directory,
)


def convert_vault(source: Path, destination: Path, verbose: bool, dry_run: bool = False) -> int:
    if not source.exists():
        log_warning(f"Source directory '{source}' does not exist.")
        return 1

    # Validate LogSeq directory structure
    pages_dir = source / "pages"
    journals_dir = source / "journals"

    if not pages_dir.exists() and not journals_dir.exists():
        log_warning(
            f"Source directory '{source}' does not appear to be a "
            "valid LogSeq graph. Missing 'pages' or 'journals' directories."
        )
        return 1

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


def convert_to_tana(
    input_dir: Path,
    target_node_id: str = "INBOX",
    verbose: bool = False,
    dry_run: bool = False,
) -> int:
    """Convert LogSeq graph to Tana workspace."""
    from logseq_converter.logseq.parser import LogSeqParser
    from logseq_converter.tana.client import TanaClient
    from logseq_converter.tana.converter import TanaConverter

    if not input_dir.exists():
        log_warning(f"Input directory '{input_dir}' does not exist.")
        return 1

    # Validate LogSeq directory structure
    pages_dir = input_dir / "pages"
    journals_dir = input_dir / "journals"

    if not pages_dir.exists() and not journals_dir.exists():
        log_warning(
            f"Input directory '{input_dir}' does not appear to be a "
            "valid LogSeq graph. Missing 'pages' or 'journals' directories."
        )
        return 1

    try:
        client = TanaClient()
    except ValueError as e:
        log_warning(str(e))
        return 1

    log_progress(f"Converting LogSeq graph '{input_dir}' to Tana...")

    converter = TanaConverter()
    parser = LogSeqParser()
    all_nodes = []

    # Process pages
    if pages_dir.exists():
        log_progress("Processing pages...")
        for file_path in pages_dir.glob("*.md"):
            try:
                if verbose:
                    log_progress(f"Processing page: {file_path.name}")

                parsed = parser.parse(file_path)
                if parsed and parsed.blocks:
                    for block in parsed.blocks:
                        node = converter.convert_block(block)
                        all_nodes.append(node)
            except Exception as e:
                log_warning(f"Error processing page {file_path.name}: {e}")
                continue

    # Process journals
    if journals_dir.exists():
        log_progress("Processing journals...")
        for file_path in journals_dir.glob("*.md"):
            try:
                if verbose:
                    log_progress(f"Processing journal: {file_path.name}")

                parsed = parser.parse(file_path)
                if parsed and parsed.blocks:
                    for block in parsed.blocks:
                        node = converter.convert_block(block)
                        all_nodes.append(node)
            except Exception as e:
                log_warning(f"Error processing journal {file_path.name}: {e}")
                continue

    if not all_nodes:
        log_warning("No content found to import.")
        return 1

    log_progress(f"Sending {len(all_nodes)} nodes to Tana (target: {target_node_id})...")

    if dry_run:
        log_progress("Dry run enabled. Skipping actual API calls.")
        return 0

    try:
        client.send_nodes(all_nodes, target_node_id=target_node_id)
        log_progress("Import complete!")
        return 0
    except Exception as e:
        log_warning(f"Error sending nodes to Tana: {e}")
        return 1


def main() -> int:
    # Check if we're being called with the old syntax (no subcommand)
    # This maintains backward compatibility
    if len(sys.argv) >= 3 and sys.argv[1] not in ["convert", "tana", "-h", "--help"]:
        # Old syntax: logseq-converter <source> <destination> [options]
        parser = argparse.ArgumentParser(description="Convert LogSeq graph to Obsidian vault")
        parser.add_argument("source", type=Path, help="Source LogSeq graph directory")
        parser.add_argument(
            "destination",
            type=Path,
            help="Destination Obsidian vault directory",
        )
        parser.add_argument(
            "-v",
            "--verbose",
            action="store_true",
            help="Enable verbose logging",
        )
        parser.add_argument(
            "--dry-run",
            action="store_true",
            help="Perform a dry run without writing changes",
        )
        args = parser.parse_args()
        return convert_vault(args.source, args.destination, args.verbose, args.dry_run)

    # New syntax with subcommands
    parser = argparse.ArgumentParser(description="Convert LogSeq graph to Obsidian vault or Tana workspace")
    subparsers = parser.add_subparsers(dest="command", help="Conversion target")

    # Convert subcommand (for Obsidian)
    convert_parser = subparsers.add_parser("convert", help="Convert LogSeq graph to Obsidian vault")
    convert_parser.add_argument("source", type=Path, help="Source LogSeq graph directory")
    convert_parser.add_argument(
        "destination",
        type=Path,
        help="Destination Obsidian vault directory",
    )
    convert_parser.add_argument(
        "-v",
        "--verbose",
        action="store_true",
        help="Enable verbose logging",
    )
    convert_parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Perform a dry run without writing changes",
    )

    # Tana subcommand
    tana_parser = subparsers.add_parser("tana", help="Convert LogSeq graph to Tana workspace")
    tana_parser.add_argument(
        "--input-dir",
        type=Path,
        required=True,
        help="Source LogSeq graph directory",
    )
    tana_parser.add_argument(
        "--target-node-id",
        type=str,
        default="INBOX",
        help="Target node ID in Tana (default: INBOX)",
    )
    tana_parser.add_argument(
        "-v",
        "--verbose",
        action="store_true",
        help="Enable verbose logging",
    )
    tana_parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Perform a dry run without writing changes",
    )

    args = parser.parse_args()

    if args.command == "convert":
        return convert_vault(args.source, args.destination, args.verbose, args.dry_run)
    elif args.command == "tana":
        return convert_to_tana(args.input_dir, args.target_node_id, args.verbose, args.dry_run)
    else:
        parser.print_help()
        return 1


if __name__ == "__main__":
    sys.exit(main())
