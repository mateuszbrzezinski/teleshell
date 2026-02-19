import pytest
from click.testing import CliRunner
from unittest.mock import patch, AsyncMock
from teleshell.main import cli
from datetime import datetime


@pytest.fixture
def mock_infrastructure():
    """Fixture to mock both Telegram and AI components."""
    with (
        patch("teleshell.main.ConfigManager") as mock_config_cls,
        patch("teleshell.main.TelegramClientWrapper") as mock_tg_cls,
        patch("teleshell.main.Summarizer") as mock_sum_cls,
    ):

        # Mock Config
        mock_config = mock_config_cls.return_value
        mock_config.load.return_value = {
            "default_channels": ["@default"],
            "summary_config": {"length": "medium"},
            "prompt_templates": {"default_summary": "Template {{messages}}"},
            "checkpoints": {},
        }

        # Mock Telegram
        mock_tg = mock_tg_cls.return_value
        mock_msg_data = {
            "id": 123,
            "text": "Hello from Telegram",
            "date": datetime.now(),
        }

        # New reliable counting: we must return messages if limit check happens
        mock_tg.fetch_messages = AsyncMock(return_value=[mock_msg_data])
        mock_tg.start = AsyncMock()

        # Mock Summarizer returns dict
        mock_sum = mock_sum_cls.return_value
        mock_sum.summarize = AsyncMock(
            return_value={
                "content": "AI Summary Result",
                "metadata": {
                    "model": "test-model",
                    "latency": 1.0,
                    "input_tokens": 10,
                    "output_tokens": 5,
                },
            }
        )

        yield {"config": mock_config, "telegram": mock_tg, "summarizer": mock_sum}


def test_full_summarize_flow(mock_infrastructure):
    """Test the complete flow of the summarize command."""
    runner = CliRunner()

    with patch.dict(
        "os.environ",
        {
            "TELEGRAM_API_ID": "123",
            "TELEGRAM_API_HASH": "hash",
            "GEMINI_API_KEY": "key",
        },
    ):
        result = runner.invoke(cli, ["summarize", "-c", "@test", "-t", "today"])

        assert result.exit_code == 0
        # We check for the new Panel title or content
        assert "TeleShell Summary: @test" in result.output
        assert "AI Summary Result" in result.output
        assert "Tokens: 10in/5out" in result.output

        mock_infrastructure["telegram"].start.assert_called_once()
        mock_infrastructure["summarizer"].summarize.assert_called_once()
        mock_infrastructure["config"].update_checkpoint.assert_called_once()
