import pytest
from textaicheck.minify_json_to_pairs import minify_json
from textaicheck.input_output_data_types import InputTextEntryMinimal


def test_minify_json_with_valid_input():
    """Test minify_json with valid input data"""
    input_data: list[InputTextEntryMinimal] = [
        {"text_id": "1", "text": "First text"},
        {"text_id": "2", "text": "Second text"},
        {"text_id": "3", "text": "Third text"}
    ]
    
    result = minify_json(input_data)
    
    assert len(result) == 3
    assert result[0] == ["1", "First text"]
    assert result[1] == ["2", "Second text"]
    assert result[2] == ["3", "Third text"]


def test_minify_json_with_empty_list():
    """Test minify_json with empty input list"""
    input_data: list[InputTextEntryMinimal] = []
    
    result = minify_json(input_data)
    
    assert result == []
    assert isinstance(result, list)


def test_minify_json_with_single_entry():
    """Test minify_json with single entry"""
    input_data: list[InputTextEntryMinimal] = [
        {"text_id": "123", "text": "Single entry text"}
    ]
    
    result = minify_json(input_data)
    
    assert len(result) == 1
    assert result[0] == ["123", "Single entry text"]


def test_minify_json_with_empty_strings():
    """Test minify_json skips entries where both text_id and text are empty"""
    input_data: list[InputTextEntryMinimal] = [
        {"text_id": "", "text": ""},
        {"text_id": "2", "text": ""}
    ]

    result = minify_json(input_data)

    # Entry with both empty strings should be skipped
    assert len(result) == 1
    assert result[0] == ["2", ""]


def test_minify_json_skips_multiple_empty_entries():
    """Test minify_json skips multiple entries where both fields are empty"""
    input_data: list[InputTextEntryMinimal] = [
        {"text_id": "1", "text": "Valid text"},
        {"text_id": "", "text": ""},  # Should be skipped
        {"text_id": "3", "text": "Another valid text"},
        {"text_id": "", "text": ""}  # Should be skipped
    ]

    result = minify_json(input_data)

    assert len(result) == 2
    assert result[0] == ["1", "Valid text"]
    assert result[1] == ["3", "Another valid text"]


def test_minify_json_keeps_partial_empty_strings():
    """Test minify_json keeps entries where only one field is empty"""
    input_data: list[InputTextEntryMinimal] = [
        {"text_id": "", "text": "Text without ID"},  # Should be kept
        {"text_id": "id_only", "text": ""}  # Should be kept
    ]

    result = minify_json(input_data)

    assert len(result) == 2
    assert result[0] == ["", "Text without ID"]
    assert result[1] == ["id_only", ""]


def test_minify_json_with_special_characters():
    """Test minify_json handles special characters in text"""
    input_data: list[InputTextEntryMinimal] = [
        {"text_id": "1", "text": "Text with\nnewlines\tand\ttabs"},
        {"text_id": "2", "text": "Special chars: @#$%^&*()"},
        {"text_id": "3", "text": "Unicode: café, naïve, 你好"}
    ]
    
    result = minify_json(input_data)
    
    assert len(result) == 3
    assert result[0] == ["1", "Text with\nnewlines\tand\ttabs"]
    assert result[1] == ["2", "Special chars: @#$%^&*()"]
    assert result[2] == ["3", "Unicode: café, naïve, 你好"]


def test_minify_json_with_long_text():
    """Test minify_json handles long text content"""
    long_text = "Lorem ipsum " * 1000
    input_data: list[InputTextEntryMinimal] = [
        {"text_id": "long_1", "text": long_text}
    ]
    
    result = minify_json(input_data)
    
    assert len(result) == 1
    assert result[0][0] == "long_1"
    assert result[0][1] == long_text
    assert len(result[0][1]) > 10000
