""" Test CLI Module """

from unittest.mock import patch

from click.testing import CliRunner

import cobalt_purestorage.cli as cli


#  https://github.com/pallets/click/issues/824#issuecomment-562581313
#  for caplog workaround
@patch("cobalt_purestorage.cli.rotator.main")
def test_rotate(mock, caplog):
    caplog.set_level(1000)

    runner = CliRunner()
    mock.return_value = None

    result = runner.invoke(cli.rotate_entrypoint)

    assert result.output == ""
    mock.assert_called_once()
    mock.assert_called_with()


@patch("cobalt_purestorage.cli.smoketest.main")
def test_smoketest(mock, caplog):
    caplog.set_level(1000)

    runner = CliRunner()
    mock.return_value = None

    result = runner.invoke(cli.smoketest_entrypoint)

    assert result.output == ""
    mock.assert_called_once()
    mock.assert_called_with()
