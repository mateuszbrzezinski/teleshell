import pytest
from click.testing import CliRunner
from unittest.mock import patch, MagicMock
from teleshell.main import cli

@pytest.fixture
def mock_config_manager():
    """Fixture to mock the ConfigManager during CLI channel tests."""
    with patch("teleshell.main.ConfigManager") as mock_cls:
        mock_instance = mock_cls.return_value
        # Initial empty config
        mock_instance.load.return_value = {
            "default_channels": ["@existing"],
            "summary_config": {"length": "medium"}
        }
        yield mock_instance

def test_channels_list(mock_config_manager):
    """Test 'tshell channels list' command with titles."""
    mock_config_manager.load.return_value = {
        "default_channels": ["@existing"],
        "channel_titles": {"@existing": "Beautiful Channel Name"}
    }
    runner = CliRunner()
    result = runner.invoke(cli, ["channels", "list"])
    
    assert result.exit_code == 0
    assert "Beautiful Channel Name" in result.output
    assert "@existing" in result.output

def test_channels_add_with_title(mock_config_manager):
    """Test 'tshell channels add --title' command."""
    runner = CliRunner()
    result = runner.invoke(cli, ["channels", "add", "@new_channel", "--title", "A New Channel"])
    
    assert result.exit_code == 0
    assert "Added @new_channel" in result.output
    
    # Verify save was called with the updated list and title
    args, _ = mock_config_manager.save.call_args
    assert "@new_channel" in args[0]["default_channels"]
    assert args[0]["channel_titles"]["@new_channel"] == "A New Channel"

def test_channels_remove(mock_config_manager):
    """Test 'tshell channels remove' command."""
    runner = CliRunner()
    result = runner.invoke(cli, ["channels", "remove", "@existing"])
    
    assert result.exit_code == 0
    assert "Removed @existing" in result.output
    
    # Verify save was called with the empty list
    args, _ = mock_config_manager.save.call_args
    assert "@existing" not in args[0]["default_channels"]
    assert len(args[0]["default_channels"]) == 0
