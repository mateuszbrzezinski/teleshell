import pytest
from click.testing import CliRunner
from unittest.mock import patch, MagicMock, AsyncMock, ANY
from teleshell.main import cli
from datetime import datetime

@pytest.fixture
def mock_infrastructure():
    """Fixture to mock both Telegram and AI components."""
    with patch("teleshell.main.ConfigManager") as mock_config_cls, \
         patch("teleshell.main.TelegramClientWrapper") as mock_tg_cls, \
         patch("teleshell.main.Summarizer") as mock_sum_cls:
        
        # Mock Config
        mock_config = mock_config_cls.return_value
        mock_config.load.return_value = {
            "default_channels": ["@default"],
            "summary_config": {"length": "medium"},
            "prompt_templates": {"default_summary": "Template {{messages}}"},
            "checkpoints": {}
        }
        
        # Mock Telegram
        mock_tg = mock_tg_cls.return_value
        mock_msg_data = {
            "id": 123,
            "text": "Hello from Telegram",
            "date": datetime.now()
        }
        
        mock_tg.fetch_messages = AsyncMock(return_value=[mock_msg_data])
        mock_tg.start = AsyncMock()
        
        # Mock Summarizer
        mock_sum = mock_sum_cls.return_value
        mock_sum.summarize = AsyncMock(return_value="AI Summary Result")
        
        yield {
            "config": mock_config,
            "telegram": mock_tg,
            "summarizer": mock_sum
        }

def test_full_summarize_flow(mock_infrastructure):
    """Test the complete flow of the summarize command."""
    runner = CliRunner()
    
    with patch.dict("os.environ", {
        "TELEGRAM_API_ID": "123",
        "TELEGRAM_API_HASH": "hash",
        "GEMINI_API_KEY": "key"
    }):
        result = runner.invoke(cli, ["summarize", "-c", "@test", "-t", "24h"])
        
        assert result.exit_code == 0
        assert "Summary for @test:" in result.output
        assert "AI Summary Result" in result.output
        
        mock_infrastructure["telegram"].start.assert_called_once()
        mock_infrastructure["telegram"].fetch_messages.assert_called_once()
        mock_infrastructure["summarizer"].summarize.assert_called_once()
        
        # Verify checkpoint update with ANY for the date string
        mock_infrastructure["config"].update_checkpoint.assert_called_once_with(
            "@test", 123, ANY
        )
