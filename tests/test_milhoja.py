import pytest
from click.testing import CliRunner
from milhoja.cli import main


def test_cli():
    runner = CliRunner()
    result = runner.invoke(main)
    assert result.exit_code == 0
    assert 'milhoja.cli.main' in result.output
    help_result = runner.invoke(main, ['--help'])
    assert help_result.exit_code == 0
    assert '--help  Show this message and exit.' in help_result.output
