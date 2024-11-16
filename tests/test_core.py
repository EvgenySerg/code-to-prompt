"""Tests for core functionality."""
import pytest
from pathlib import Path
from src_consolidator.core import SourceConsolidator, ConsolidationConfig


@pytest.fixture
def test_fixtures_dir():
    """Create and return test fixtures directory."""
    fixtures_dir = Path("tests/fixtures")
    fixtures_dir.mkdir(parents=True, exist_ok=True)
    return fixtures_dir


@pytest.fixture
def test_config(test_fixtures_dir):
    """Create basic test configuration."""
    return ConsolidationConfig(
        root_dir=test_fixtures_dir,
        file_patterns={".go"},
        name_patterns={"*model*"},
        exclude_patterns={"gen", "vendor"}
    )


def test_should_skip_folder_basic(test_config):
    """Test basic folder exclusion."""
    consolidator = SourceConsolidator(test_config)
    assert consolidator.should_skip_folder(Path("vendor"))
    assert consolidator.should_skip_folder(Path("gen"))
    assert not consolidator.should_skip_folder(Path("src"))


def test_should_skip_folder_nested_paths(test_config):
    """Test folder exclusion with nested paths."""
    consolidator = SourceConsolidator(test_config)
    assert consolidator.should_skip_folder(Path("src/vendor"))
    assert consolidator.should_skip_folder(Path("pkg/gen"))
    assert consolidator.should_skip_folder(Path("a/b/c/vendor"))
    assert not consolidator.should_skip_folder(Path("vendor_valid"))
    assert not consolidator.should_skip_folder(Path("generated"))


def test_should_skip_folder_case_sensitivity(test_config):
    """Test case-insensitive folder exclusion."""
    consolidator = SourceConsolidator(test_config)
    assert consolidator.should_skip_folder(Path("VENDOR"))
    assert consolidator.should_skip_folder(Path("Vendor"))
    assert consolidator.should_skip_folder(Path("GEN"))
    assert consolidator.should_skip_folder(Path("Gen"))


@pytest.fixture
def setup_test_files(test_fixtures_dir):
    """Create test file structure."""
    # Create test directory structure
    dirs = [
        "src/models",
        "src/gen/models",
        "vendor/models",
        "internal/models",
    ]

    files = [
        "src/models/user_model.go",
        "src/gen/models/generated_model.go",
        "src/regular_file.go",
        "vendor/models/vendor_model.go",
        "internal/models/data_model.go",
    ]

    # Create directories
    for d in dirs:
        Path(test_fixtures_dir / d).mkdir(parents=True, exist_ok=True)

    # Create files
    for f in files:
        file_path = test_fixtures_dir / f
        file_path.parent.mkdir(parents=True, exist_ok=True)
        file_path.touch()

    return test_fixtures_dir


def test_collect_source_files(test_config, setup_test_files):
    """Test file collection with exclusions."""
    consolidator = SourceConsolidator(test_config)
    files = consolidator.collect_source_files()

    # Convert to set of strings for easier comparison
    found_files = {str(f.relative_to(test_config.root_dir)) for f in files}

    # Should find
    assert "src/models/user_model.go" in found_files
    assert "internal/models/data_model.go" in found_files

    # Should NOT find
    assert "src/gen/models/generated_model.go" not in found_files
    assert "vendor/models/vendor_model.go" not in found_files
    assert "src/regular_file.go" not in found_files

    # Check total number of files
    assert len(files) == 2


def test_collect_source_files_with_different_patterns(test_fixtures_dir):
    """Test file collection with different exclusion patterns."""
    config = ConsolidationConfig(
        root_dir=test_fixtures_dir,
        file_patterns={".go"},
        name_patterns={"*model*"},
        exclude_patterns={"gen/*", "vendor/**"}
    )

    consolidator = SourceConsolidator(config)
    files = consolidator.collect_source_files()

    found_files = {str(f.relative_to(config.root_dir)) for f in files}
    assert len(found_files) == 2
    assert all("gen" not in str(f) for f in found_files)
    assert all("vendor" not in str(f) for f in found_files)


def test_empty_exclude_patterns(test_fixtures_dir):
    """Test behavior with no exclusion patterns."""
    config = ConsolidationConfig(
        root_dir=test_fixtures_dir,
        file_patterns={".go"},
        name_patterns={"*model*"},
        exclude_patterns=None
    )

    consolidator = SourceConsolidator(config)
    files = consolidator.collect_source_files()

    # Should find all model files, including those in gen and vendor
    found_files = {str(f.relative_to(config.root_dir)) for f in files}
    assert len(found_files) == 4  # All *model*.go files


def test_exclude_with_wildcards(test_fixtures_dir):
    """Test exclusion patterns with wildcards."""
    config = ConsolidationConfig(
        root_dir=test_fixtures_dir,
        file_patterns={".go"},
        name_patterns={"*model*"},
        exclude_patterns={"**/gen/**", "**/vendor/**"}
    )

    consolidator = SourceConsolidator(config)
    files = consolidator.collect_source_files()

    found_files = {str(f.relative_to(config.root_dir)) for f in files}
    assert len(found_files) == 2
    assert all("gen" not in str(f) for f in found_files)
    assert all("vendor" not in str(f) for f in found_files)