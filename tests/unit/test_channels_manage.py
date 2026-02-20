import pytest
from click.testing import CliRunner
from unittest.mock import patch, MagicMock, AsyncMock
from teleshell.main import cli
import os

@pytest.fixture
def mock_manage_infra():
    """Mock the infrastructure required for the manage command."""
    with (
        patch("teleshell.main.ConfigManager") as mock_config_cls,
        patch("teleshell.main.TelegramClientWrapper") as mock_tg_cls,
        patch("teleshell.main.inquirer") as mock_inquirer,
        patch.dict("os.environ", {"TELEGRAM_API_ID": "123", "TELEGRAM_API_HASH": "hash"})
    ):
        # Mock Config
        mock_config = mock_config_cls.return_value
        mock_config.load.return_value = {
            "default_channels": ["@old"],
            "summary_config": {}
        }

        # Mock Telegram
        mock_tg = mock_tg_cls.return_value
        mock_tg.start = AsyncMock()
        mock_tg.fetch_dialogs = AsyncMock(return_value=[
            {"title": "Channel A", "handle": "a", "folder_id": 0, "id": 1, "is_channel": True, "is_group": False}
        ])
        mock_tg.fetch_folders = AsyncMock(return_value={0: "Main"})

        # Mock InquirerPy Chain: inquirer.checkbox(...).execute_async()
        mock_checkbox_instance = MagicMock()
        mock_checkbox_instance.execute_async = AsyncMock(return_value=["@a"])
        mock_inquirer.checkbox.return_value = mock_checkbox_instance

        yield {
            "config": mock_config,
            "telegram": mock_tg,
            "inquirer": mock_inquirer
        }

def test_channels_manage_flow(mock_manage_infra):
    """
    Verify the complete interactive management flow:
    Fetching -> TUI Display -> Config Update.
    """
    runner = CliRunner()
    
    # Run the command
    result = runner.invoke(cli, ["channels", "manage"])
    
    assert result.exit_code == 0
    assert "Success" in result.output
    
    # 1. Verify Telegram was called
    mock_manage_infra["telegram"].start.assert_called_once()
    mock_manage_infra["telegram"].fetch_dialogs.assert_called_once()
    
    # 2. Verify TUI was initialized with correct parameters
    mock_manage_infra["inquirer"].checkbox.assert_called_once()
    args, kwargs = mock_manage_infra["inquirer"].checkbox.call_args
    assert "Select channels to track" in kwargs["message"]
    
    # 3. Verify Configuration was updated with the TUI selection and titles
    mock_manage_infra["config"].save.assert_called_once()
    saved_config = mock_manage_infra["config"].save.call_args[0][0]
    assert saved_config["default_channels"] == ["@a"]
    assert saved_config["channel_titles"]["@a"] == "Channel A"
