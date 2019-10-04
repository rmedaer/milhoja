import pytest
from click.testing import CliRunner
from milhoja import cli


def test_cli():
    runner = CliRunner()
    result = runner.invoke(cli.main)
    assert result.exit_code == 0
    help_result = runner.invoke(cli.main, ['--help'])
    assert help_result.exit_code == 0
    assert '--help     Show this message and exit.' in help_result.output
