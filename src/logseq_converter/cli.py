import argparse
import os
import sys
from pathlib import Path

from logseq_converter.logseq.parser import BlockReferenceScanner
from logseq_converter.obsidian.converter import ObsidianConverter
from logseq_converter.utils import (
    copy_assets,
    log_progress,
    log_warning,
    validate_output_directory,
)


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Convert LogSeq graph to Obsidian vault"
    )
    parser.add_argument(
        "source", type=Path, help="Source LogSeq graph directory"
    )
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
    
    args = parser.parse_args()
    
    source: Path = args.source
    destination: Path = args.destination
    
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
        
    try:
        validate_output_directory(destination)
    except FileExistsError as e:
        log_warning(str(e))
        return 1
        
    log_progress(f"Converting '{source}' to '{destination}'...")
    
    # Pass 1: Scan for block IDs
    log_progress("Scanning for block IDs...")
    scanner = BlockReferenceScanner()
    
    # Walk source to scan
    for root, _, files in os.walk(source):
        for file in files:
            if file.endswith(".md"):
                scanner.scan_file(Path(root) / file)
    
    converter = ObsidianConverter(scanner)
    
    # Create destination directory
    if not destination.exists():
        destination.mkdir(parents=True)
        
    # Copy assets
    assets_src = source / "assets"
    assets_dest = destination / "assets"
    if assets_src.exists():
        log_progress("Copying assets...")
        copy_assets(assets_src, assets_dest)
        
    # Process files
    log_progress("Processing files...")
    
    # Walk through source directory
    # LogSeq structure:
    # /pages -> standard pages
    # /journals -> journals
    # /assets -> assets (handled)
    
    pages_dir = source / "pages"
    journals_dir = source / "journals"
    
    # Process journals
    if journals_dir.exists():
        for file_path in journals_dir.glob("*.md"):
            try:
                if args.verbose:
                    log_progress(f"Processing journal: {file_path.name}")
                dest_rel_path = converter.transform_journal_filename(file_path.name)
                if dest_rel_path:
                    dest_path = destination / dest_rel_path
                    dest_path.parent.mkdir(parents=True, exist_ok=True)
                    
                    with open(file_path, 'r', encoding='utf-8') as f:
                        content = f.read()
                    
                    # Extract sections (US3)
                    content, extracted_files = converter.extract_sections(
                        content, file_path.name
                    )
                    
                    # Save extracted files
                    for filename, file_content in extracted_files:
                        extracted_path = destination / filename
                        extracted_path.parent.mkdir(parents=True, exist_ok=True)
                        with open(extracted_path, 'w', encoding='utf-8') as f:
                            f.write(file_content)
                        
                    converted_content = converter.convert_content(content)
                    
                    with open(dest_path, 'w', encoding='utf-8') as f:
                        f.write(converted_content)
                else:
                    log_warning(f"Skipping unrecognized journal file: {file_path.name}")
            except Exception as e:
                log_warning(f"Error processing journal {file_path.name}: {e}")
                continue

    # Process pages
    if pages_dir.exists():
        for file_path in pages_dir.glob("*.md"):
            try:
                if args.verbose:
                    log_progress(f"Processing page: {file_path.name}")
                dest_rel_path = converter.transform_page_filename(file_path.name)
                dest_path = destination / dest_rel_path
                dest_path.parent.mkdir(parents=True, exist_ok=True)
                
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                    
                converted_content = converter.convert_content(content)
                
                with open(dest_path, 'w', encoding='utf-8') as f:
                    f.write(converted_content)
            except Exception as e:
                log_warning(f"Error processing page {file_path.name}: {e}")
                continue

    log_progress("Conversion complete.")
    return 0

if __name__ == "__main__":
    sys.exit(main())
