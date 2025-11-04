"""Unit tests for studentify.py functions"""
import sys
from pathlib import Path
import pytest

# Add parent directory to path to import studentify
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import studentify


def test_generate_tokens():
    """Test token generation for different comment symbols."""
    comment_symbol = "//"
    token_types = {'delete': '!!', 'comment': '??', 'replace': '++', 'student': '::'}
    
    tokens = studentify.generate_tokens(comment_symbol, token_types)
    
    assert 'delete' in tokens
    assert 'comment' in tokens
    assert 'replace' in tokens
    assert 'student' in tokens
    
    # Check inline tokens
    assert tokens['delete'][0] == "//!!"
    assert tokens['comment'][0] == "//??"
    assert tokens['replace'][0] == "//++"
    assert tokens['student'][0] == "//::"
    
    # Check block start tokens
    assert tokens['delete'][1] == "//<!!"
    assert tokens['comment'][1] == "//<??"
    assert tokens['replace'][1] == "//<++"
    assert tokens['student'][1] == "//<::"
    
    # Check block end tokens
    assert tokens['delete'][2] == "//>!!"
    assert tokens['comment'][2] == "//>??"
    assert tokens['replace'][2] == "//>++"
    assert tokens['student'][2] == "//>::"


def test_indent_chars():
    """Test indent character detection."""
    assert studentify.indent_chars("    hello") == "    "
    assert studentify.indent_chars("\t\thello") == "\t\t"
    assert studentify.indent_chars("hello") == ""
    assert studentify.indent_chars("  \t  hello") == "  \t  "


def test_identity():
    """Test identity function."""
    assert studentify.identity("test") == "test"
    assert studentify.identity("") == ""
    assert studentify.identity("line\n") == "line\n"


def test_replace_by():
    """Test replace_by function."""
    assert studentify.replace_by("new", "old") == "new"
    assert studentify.replace_by("", "something") == ""


def test_add_start():
    """Test add_start function."""
    result = studentify.add_start("//", "code line\n")
    assert result == "// code line\n"  # Function adds a space
    
    result = studentify.add_start("#", "  indented\n")
    assert result == "#   indented\n"  # Adds space, keeps leading spaces


def test_remove_end():
    """Test remove_end function."""
    assert studentify.remove_end("//!!", "line //!!\n") == "line\n"  # Strips trailing space
    assert studentify.remove_end("//??", "code //??comment\n") == "code\n"
    assert studentify.remove_end("//++", "old //++ new\n") == "old\n"


def test_after_token():
    """Test after_token function."""
    # Keep everything after token (strips leading space after token)
    result = studentify.after_token(True, True, "//++", "old //++ new\n")
    assert result == "new\n"
    
    # Keep indentation
    result = studentify.after_token(True, True, "//++", "  old //++ new\n")
    assert result == "  new\n"


def test_add_start_and_remove_end():
    """Test add_start_and_remove_end function."""
    result = studentify.add_start_and_remove_end("//", "//??"," line //??\n")
    assert result == "//  line\n"  # Adds space after //, removes ??
    
    result = studentify.add_start_and_remove_end("#", "#??", "  code #??\n")
    assert result == "#   code\n"


def test_supported_languages():
    """Test that all supported languages have proper configuration."""
    assert len(studentify.SUPP_LANG) > 0
    
    for lang in studentify.SUPP_LANG:
        assert lang.name
        assert len(lang.extensions) > 0
        assert lang.comment_symbol
        assert 'delete' in lang.tokens
        assert 'comment' in lang.tokens
        assert 'replace' in lang.tokens
        assert 'student' in lang.tokens


def test_process_block_structure():
    """Test block structure processing."""
    tokens = ["//!!", "//<!!", "//>!!"]
    in_block = False
    
    # Test inline token
    processing_functions = {
        'f_inline': lambda x: "",
        'f_start_block': lambda x: x,
        'f_in_block': lambda x: x,
        'f_end_block': lambda x: x
    }
    
    new_line, in_block, modified = studentify.process_block_structure(
        "code //!!\n", in_block, tokens, processing_functions
    )
    assert modified is True
    assert in_block is False
    assert new_line == ""
    
    # Test block start
    new_line, in_block, modified = studentify.process_block_structure(
        "code //<!!\n", False, tokens, processing_functions
    )
    assert modified is True
    assert in_block is True
    
    # Test in block
    new_line, in_block, modified = studentify.process_block_structure(
        "code\n", True, tokens, processing_functions
    )
    assert modified is True
    assert in_block is True
    
    # Test block end
    new_line, in_block, modified = studentify.process_block_structure(
        "code //>!!\n", True, tokens, processing_functions
    )
    assert modified is True
    assert in_block is False


def test_language_detection():
    """Test language detection from file extension."""
    # C++ extensions
    assert any(lang.name == "c/c++" and ".cpp" in lang.extensions for lang in studentify.SUPP_LANG)
    assert any(lang.name == "c/c++" and ".h" in lang.extensions for lang in studentify.SUPP_LANG)
    
    # Python
    assert any(lang.name == "python" and ".py" in lang.extensions for lang in studentify.SUPP_LANG)
    
    # Java
    assert any(lang.name == "java" and ".java" in lang.extensions for lang in studentify.SUPP_LANG)
    
    # MATLAB
    assert any(lang.name == "matlab" and ".m" in lang.extensions for lang in studentify.SUPP_LANG)
    
    # JavaScript
    assert any(lang.name == "javascript" and ".js" in lang.extensions for lang in studentify.SUPP_LANG)
