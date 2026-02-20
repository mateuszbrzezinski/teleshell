import pytest
from teleshell.main import prepare_channel_choices
from InquirerPy.base.control import Choice

def test_prepare_choices_empty():
    """Verify that empty dialogs return an empty list (preventing ZeroDivisionError)."""
    choices = prepare_channel_choices([], {}, [])
    assert choices == []

def test_prepare_choices_grouping_and_sorting():
    """Verify that dialogs are correctly grouped by folder and sorted."""
    dialogs = [
        {"title": "B", "handle": "b", "folder_id": 1, "id": 1},
        {"title": "A", "handle": "a", "folder_id": 1, "id": 2},
        {"title": "C", "handle": "c", "folder_id": 0, "id": 3},
        {"title": "D", "handle": "d", "folder_id": None, "id": 4}, 
    ]
    folders = {0: "Main", 1: "Work"}
    tracked = ["@a", 3] # Note: 3 is an int, but channel C has id 3
    
    choices = prepare_channel_choices(dialogs, folders, tracked)
    
    assert len(choices) == 6 # 2 folders (separators) + 4 dialogs
    
    # Sort order by folder, then by title: 
    # Separator(Main), C (Main), D (Main), Separator(Work), A (Work), B (Work)
    assert "--- Main ---" in str(choices[0])
    assert "C" in choices[1].name
    assert choices[1].enabled is True
    assert "D" in choices[2].name
    assert "--- Work ---" in str(choices[3])
    assert "A" in choices[4].name
    assert choices[4].enabled is True

def test_prepare_choices_handle_logic():
    """Verify @ handle prefixing and ID fallback."""
    dialogs = [
        {"title": "User", "handle": "username", "folder_id": 0, "id": 123},
        {"title": "NoHandle", "handle": None, "folder_id": 0, "id": 456},
    ]
    choices = prepare_channel_choices(dialogs, {0: "Main"}, [])
    
    # Index 0 is Separator(Main)
    # Sort order: NoHandle (N), User (U)
    assert choices[1].value == "456"
    assert choices[2].value == "@username"
