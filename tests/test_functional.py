"""Functional tests for studentify.py"""
import sys
import subprocess
from pathlib import Path
import pytest


@pytest.fixture
def repo_root():
    """Return the repository root directory."""
    return Path(__file__).resolve().parents[1]


@pytest.fixture
def studentify_script(repo_root):
    """Return the path to studentify.py script."""
    return repo_root / "studentify.py"


@pytest.fixture
def fixtures_dir(repo_root):
    """Return the fixtures directory."""
    return repo_root / "tests" / "fixtures"


def normalize_text(text: str) -> str:
    """Normalize line endings for cross-platform compatibility."""
    return text.replace("\r\n", "\n").strip()


def test_studentify_cpp_default_mode(tmp_path, studentify_script, fixtures_dir):
    """Test studentify on C++ file with default mode (student version).
    
    This test verifies that studentify correctly processes a C++ file with various
    markers (delete, comment, replace, student) and generates the appropriate
    student version where:
    - Lines marked with //!! are deleted
    - Lines marked with //?? are commented out
    - Lines marked with //:: (student markers) are uncommented
    - Lines marked with //++ are replaced with the text after the marker
    
    Args:
        tmp_path: Pytest fixture providing a temporary directory
        studentify_script: Path to the studentify.py script
        fixtures_dir: Path to the test fixtures directory
    """
    input_file = fixtures_dir / "cpp" / "input.cpp"
    expected_file = fixtures_dir / "cpp" / "expected.cpp"
    output_file = tmp_path / "result.cpp"

    # Run studentify in default mode
    result = subprocess.run(
        [
            sys.executable,
            str(studentify_script),
            "-o",
            str(output_file),
            str(input_file),
            "--noBackup",
        ],
        capture_output=True,
        text=True,
    )

    assert result.returncode == 0, f"studentify failed: {result.stderr or result.stdout}"
    assert output_file.exists(), "Output file was not created"

    actual = normalize_text(output_file.read_text(encoding="utf-8"))
    expected = normalize_text(expected_file.read_text(encoding="utf-8"))

    assert actual == expected, "Output doesn't match expected student version"


def test_studentify_cpp_clean_mode(tmp_path, studentify_script, fixtures_dir):
    """Test studentify on C++ file with --clean mode (clean version).
    
    This test verifies that studentify's --clean mode removes all studentify
    markers while preserving the original code. In clean mode:
    - Delete markers (//!!) are removed but the lines are kept
    - Comment markers (//??) are removed but the lines are kept
    - Student markers (//::) are removed
    - Replace markers (//++) are removed but original lines are kept
    
    This mode is useful for generating a "clean" version of the code without
    any studentify annotations.
    
    Args:
        tmp_path: Pytest fixture providing a temporary directory
        studentify_script: Path to the studentify.py script
        fixtures_dir: Path to the test fixtures directory
    """
    input_file = fixtures_dir / "cpp" / "input.cpp"
    expected_file = fixtures_dir / "cpp" / "expected_clean.cpp"
    output_file = tmp_path / "result.cpp"

    # Run studentify in clean mode
    result = subprocess.run(
        [
            sys.executable,
            str(studentify_script),
            "-o",
            str(output_file),
            str(input_file),
            "--noBackup",
            "--clean",
        ],
        capture_output=True,
        text=True,
    )

    assert result.returncode == 0, f"studentify failed: {result.stderr or result.stdout}"
    assert output_file.exists(), "Output file was not created"

    actual = normalize_text(output_file.read_text(encoding="utf-8"))
    expected = normalize_text(expected_file.read_text(encoding="utf-8"))

    assert actual == expected, "Output doesn't match expected clean version"


def test_studentify_in_place(tmp_path, studentify_script, fixtures_dir):
    """Test studentify modifying file in place.
    
    This test verifies that studentify can modify files in place (without
    specifying an output file) when the --noBackup flag is used. The input
    file should be transformed into the student version directly.
    
    This is useful for batch processing multiple files in a directory structure
    while preserving the original file locations.
    
    Args:
        tmp_path: Pytest fixture providing a temporary directory
        studentify_script: Path to the studentify.py script
        fixtures_dir: Path to the test fixtures directory
    """
    input_file = fixtures_dir / "cpp" / "input.cpp"
    expected_file = fixtures_dir / "cpp" / "expected.cpp"
    
    # Copy input to temp location
    test_file = tmp_path / "test.cpp"
    test_file.write_text(input_file.read_text(encoding="utf-8"), encoding="utf-8")

    # Run studentify in place with noBackup
    result = subprocess.run(
        [
            sys.executable,
            str(studentify_script),
            str(test_file),
            "--noBackup",
        ],
        capture_output=True,
        text=True,
    )

    assert result.returncode == 0, f"studentify failed: {result.stderr or result.stdout}"

    actual = normalize_text(test_file.read_text(encoding="utf-8"))
    expected = normalize_text(expected_file.read_text(encoding="utf-8"))

    assert actual == expected, "In-place modification doesn't match expected output"
