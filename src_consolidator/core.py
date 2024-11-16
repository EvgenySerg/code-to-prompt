"""
Core functionality for source code consolidation.
"""
import os
import fnmatch
from typing import List, Optional, Set
from pathlib import Path
from datetime import datetime
from dataclasses import dataclass
from logging import Logger, getLogger

logger = getLogger(__name__)


@dataclass
class ConsolidationConfig:
    """Configuration for the consolidation process."""
    root_dir: Path
    file_patterns: Set[str]
    name_patterns: Optional[Set[str]] = None
    exclude_patterns: Optional[Set[str]] = None
    output_file: Path = Path("consolidated_source.txt")


class SourceConsolidator:
    """Main class for handling source code consolidation."""

    def __init__(self, config: ConsolidationConfig):
        """Initialize consolidator with configuration."""
        self.config = config
        self.logger = getLogger(__name__)

    def should_skip_folder(self, folder_path: Path) -> bool:
        """
        Determine if a folder should be skipped based on exclude patterns.

        Args:
            folder_path: Path to the folder to check

        Returns:
            bool: True if folder should be skipped, False otherwise
        """
        if not self.config.exclude_patterns:
            return False

        # Convert path to string for pattern matching
        path_str = str(folder_path)
        path_parts = folder_path.parts

        for pattern in self.config.exclude_patterns:
            pattern_lower = pattern.lower()
            path_lower = path_str.lower()

            # Handle exact directory matches
            if pattern_lower in [part.lower() for part in path_parts]:
                return True

            # Handle wildcard patterns
            if any(p in pattern_lower for p in ['*', '?', '[', ']']):
                # For wildcard patterns, check the full path
                if fnmatch.fnmatch(path_lower, pattern_lower):
                    return True
                if fnmatch.fnmatch(path_lower, f"**/{pattern_lower}"):
                    return True
                if fnmatch.fnmatch(path_lower, f"**/{pattern_lower}/**"):
                    return True

            # Don't match partial strings for non-wildcard patterns
            # This prevents 'vendor' from matching 'vendor_valid'
            else:
                for part in path_parts:
                    if part.lower() == pattern_lower:
                        return True

        return False

    def collect_source_files(self) -> List[Path]:
        """
        Collect all matching source files based on configuration.

        Returns:
            List[Path]: List of paths to matching source files
        """
        source_files = []
        root = Path(self.config.root_dir)

        self.logger.debug(f"Starting search in: {root}")
        self.logger.debug(f"Exclude patterns: {self.config.exclude_patterns}")
        self.logger.debug(f"Name patterns: {self.config.name_patterns}")
        self.logger.debug(f"File patterns: {self.config.file_patterns}")

        for path in root.rglob("*"):
            if path.is_file():
                # Check if file is in excluded directory
                if any(self.should_skip_folder(parent)
                       for parent in path.parents):
                    self.logger.debug(f"Skipping file (in excluded directory): {path}")
                    continue

                # Check file extension
                if not any(path.name.endswith(ext) for ext in self.config.file_patterns):
                    self.logger.debug(f"Skipping file (wrong extension): {path}")
                    continue

                # Check name pattern if specified
                if self.config.name_patterns:
                    if not any(fnmatch.fnmatch(path.name.lower(), pattern.lower())
                               for pattern in self.config.name_patterns):
                        self.logger.debug(f"Skipping file (name doesn't match): {path}")
                        continue

                source_files.append(path)
                self.logger.debug(f"Added matching file: {path}")

        return sorted(source_files)

    def create_consolidated_file(self, source_files: List[Path]) -> None:
        """
        Create a consolidated file from the source files.

        Args:
            source_files: List of paths to source files to consolidate
        """
        with open(self.config.output_file, 'w', encoding='utf-8') as outfile:
            self._write_header(outfile)

            for file_path in source_files:
                try:
                    self._process_file(file_path, outfile)
                except Exception as e:
                    self.logger.error(f"Error processing {file_path}: {e}")
                    outfile.write(f"### ERROR reading file {file_path}: {str(e)}\n\n")

    def _write_header(self, outfile) -> None:
        """Write the header of the consolidated file."""
        outfile.write("# Consolidated Source Code File\n")
        outfile.write(f"# Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        outfile.write("#" + "=" * 80 + "\n\n")

    def _process_file(self, file_path: Path, outfile) -> None:
        """Process a single source file."""
        with open(file_path, 'r', encoding='utf-8') as infile:
            relative_path = file_path.relative_to(self.config.root_dir)
            outfile.write(f"### File: {relative_path}\n")
            outfile.write("#" + "-" * 80 + "\n\n")
            outfile.write(infile.read())
            outfile.write("\n\n")
            outfile.write("#" + "=" * 80 + "\n\n")
