""" Test CLI Module """

from unittest.mock import patch

from click.testing import CliRunner

import pkg.cli as cli

#  https://github.com/pallets/click/issues/824#issuecomment-562581313
#  for caplog workaround
@patch("pkg.cli.rotator.main")
def test_rotate(mock, caplog):

    caplog.set_level(1000)

    runner = CliRunner()
    mock.return_value = None

    result = runner.invoke(cli.rotate)

    assert result.output == ""
    mock.assert_called_once()
    mock.assert_called_with()
