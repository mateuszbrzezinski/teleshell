from click.testing import CliRunner
from teleshell.main import cli

def test_cli_summarize_basic():
    """Test the basic tshell summarize command structure."""
    runner = CliRunner()
    # Testing with just the command to see if it responds
    result = runner.invoke(cli, ["summarize", "--help"])
    assert result.exit_code == 0
    assert "Summarize Telegram channels" in result.output

def test_cli_summarize_options():
    """Test if command accepts required options."""
    runner = CliRunner()
    # We use help to verify options are defined without needing full implementation
    result = runner.invoke(cli, ["summarize", "--help"])
    assert "--channels" in result.output
    assert "--time-window" in result.output
    assert "--verbose" in result.output
