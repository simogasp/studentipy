"""Functional tests for studentify.py"""
import sys
import subprocess # nosec B404
from pathlib import Path
from typing import List, Optional
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


def run_studentify(
    studentify_script: Path,
    input_file: Path,
    output_file: Optional[Path] = None,
    extra_args: Optional[List[str]] = None
) -> subprocess.CompletedProcess:
    """Run the studentify script with given arguments.
    
    Args:
        studentify_script: Path to the studentify.py script
        input_file: Input file to process
        output_file: Optional output file (if None, modifies in place)
        extra_args: Additional command-line arguments (e.g., ['--clean'])
    
    Returns:
        CompletedProcess object with the result
    """
    cmd = [sys.executable, str(studentify_script)]

    if output_file:
        cmd.extend(["-o", str(output_file)])

    cmd.append(str(input_file))
    cmd.append("--noBackup")

    if extra_args:
        cmd.extend(extra_args)

    return subprocess.run(  # nosec B404
        cmd,
        capture_output=True,
        text=True,
        shell=False,  # nosec B404
    )


def assert_studentify_output(
    result: subprocess.CompletedProcess,
    actual_file: Path,
    expected_file: Path,
    error_message: str = "Output doesn't match expected"
) -> None:
    """Assert that studentify ran successfully and output matches expected.

    Args:
        result: The subprocess result from running studentify
        actual_file: Path to the actual output file
        expected_file: Path to the expected output file
        error_message: Custom error message for content mismatch
    """
    assert result.returncode == 0, f"studentify failed: {result.stderr or result.stdout}"
    assert actual_file.exists(), "Output file was not created"

    actual = normalize_text(actual_file.read_text(encoding="utf-8"))
    expected = normalize_text(expected_file.read_text(encoding="utf-8"))

    assert actual == expected, error_message


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

    result = run_studentify(studentify_script, input_file, output_file)
    assert_studentify_output(result, output_file, expected_file,
                            "Output doesn't match expected student version")


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

    result = run_studentify(studentify_script, input_file, output_file, ["--clean"])
    assert_studentify_output(result, output_file, expected_file,
                            "Output doesn't match expected clean version")


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

    # Copy input to temp location for in-place modification
    test_file = tmp_path / "test.cpp"
    test_file.write_text(input_file.read_text(encoding="utf-8"), encoding="utf-8")

    result = run_studentify(studentify_script, test_file)
    assert_studentify_output(result, test_file, expected_file,
                            "In-place modification doesn't match expected output")
