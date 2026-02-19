import click
from click.testing import CliRunner
from teleshell.main import cli
def test_cli_summarize_basic():
    runner = CliRunner()
    result = runner.invoke(cli, ['summarize', '--help'])
    assert result.exit_code == 0
def test_cli_summarize_options():
    runner = CliRunner()
    result = runner.invoke(cli, ['summarize', '--help'])
    assert '--channels' in result.output