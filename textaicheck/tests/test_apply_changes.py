import pytest
from textaicheck.apply_changes import apply_changes
from textaicheck.input_output_data_types import OutputChangedResult, InputTextEntry



# Example fixtures
@pytest.fixture
def data():
    """input data fixture"""
    return [
        InputTextEntry(text_id="1", text="Hello", correction_type=["orthography"]),
        InputTextEntry(text_id="2", text="Il faut tous tester", correction_type=["orthography", "syntax"]),
        InputTextEntry(text_id="3", text="L'IA générative crée du contenu.", correction_type=["reformulation"])
    ]

@pytest.fixture
def modified_list():
    """output modified list fixture"""
    return [
        ["1", "Hello"],
        ["2", "Il faut tout tester"],
        ["3", "L'IA générative produit du contenu."]
    ]


def test_changes_matching_ids(data, modified_list):
    """test that it matches the ids in both inputs and changes text field appropriately"""
    changes_applied = apply_changes(data, modified_list)
    # text_id=1 --> unchanged
    assert changes_applied[0].modified_text == "Hello"
    # text_id=2 replaced
    assert changes_applied[1].modified_text == "Il faut tout tester"
    # text_id=3 replaced
    assert changes_applied[2].modified_text == "L'IA générative produit du contenu."

def test_empty_modified_list_does_nothing(data):
    """If modified list is empty, the function should return an empty list"""
    changes_applied = apply_changes(data, [])
    assert changes_applied == []

def test_empty_data_returns_empty(modified_list):
    """If data is empty, the function should return an empty list"""
    changes_applied = apply_changes([], modified_list)
    assert changes_applied == []

def test_incorrect_inputs_raise_type_errors():
    """If inputs are not of correct type, a TypeError should be raised"""
    with pytest.raises(TypeError):
        apply_changes("not a list", [])

    with pytest.raises(TypeError):
        apply_changes([], "not a list")

def test_wrong_entry_in_data_returns_correct_result():
    """Entry is of wrong type and should not be processed, it will be skipped"""
    changes_applied = apply_changes(["not a dict"], [["1", "Hello"]])
    assert changes_applied == []


