"""
Command line interface for the source consolidator.
"""
import sys
import logging
from pathlib import Path
from typing import Set
import argparse

from .core import SourceConsolidator, ConsolidationConfig  # Changed from 'from core import' to 'from .core import'
from .config import DEFAULT_EXCLUDES  # Changed from 'from config import' to 'from .config import'



def setup_logging(verbose: bool) -> None:
    """Configure logging based on verbosity."""
    level = logging.DEBUG if verbose else logging.INFO
    logging.basicConfig(
        level=level,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )


def parse_patterns(patterns: Set[str], add_wildcards: bool = False) -> Set[str]:
    """Parse and normalize patterns."""
    if not patterns:
        return set()

    result = set()
    for pattern in patterns:
        if add_wildcards and not any(c in pattern for c in '*?[]'):
            pattern = f'*{pattern}*'
        result.add(pattern)
    return result


def main() -> int:
    """Main entry point for the CLI."""
    parser = argparse.ArgumentParser(
        description='Consolidate source code files into a single file'
    )
    parser.add_argument('--root', '-r', required=True, type=Path,
                        help='Root directory of the project')
    parser.add_argument('--patterns', '-p', nargs='+', default={'.go'},
                        help='File extensions to match (default: .go)')
    parser.add_argument('--names', '-n', nargs='+',
                        help='Patterns to match in file names (e.g., "*model*")')
    parser.add_argument('--exclude', '-e', nargs='+',
                        help='Folders to exclude (e.g., "vendor" "test*")')
    parser.add_argument('--output', '-o', type=Path,
                        default=Path('consolidated_source.txt'),
                        help='Output file name (default: consolidated_source.txt)')
    parser.add_argument('--verbose', '-v', action='store_true',
                        help='Enable verbose output')

    args = parser.parse_args()
    setup_logging(args.verbose)
    logger = logging.getLogger(__name__)

    # Prepare patterns
    file_patterns = {p if p.startswith('.') else f'.{p}' for p in args.patterns}
    name_patterns = parse_patterns(set(args.names) if args.names else set(), add_wildcards=True)

    # Handle exclude patterns
    exclude_patterns = set(args.exclude or [])
    exclude_patterns.update(DEFAULT_EXCLUDES)

    logger.debug(f"File patterns: {file_patterns}")
    logger.debug(f"Name patterns: {name_patterns}")
    logger.debug(f"Exclude patterns: {exclude_patterns}")

    config = ConsolidationConfig(
        root_dir=args.root,
        file_patterns=file_patterns,
        name_patterns=name_patterns,
        exclude_patterns=exclude_patterns,
        output_file=args.output
    )

    consolidator = SourceConsolidator(config)

    try:
        source_files = consolidator.collect_source_files()
        if not source_files:
            logger.warning("No matching source files found!")
            return 1

        logger.info(f"Found {len(source_files)} matching files")
        consolidator.create_consolidated_file(source_files)
        logger.info(f"Created consolidated file: {args.output}")
        return 0

    except Exception as e:
        logger.error(f"Error during consolidation: {e}", exc_info=True)
        return 1


if __name__ == '__main__':
    sys.exit(main())
