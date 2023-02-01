import json
import os
import pytest
import sys

from src.lox import Lox
from test.lox_test_cases import LOX_FUNCTIONS_EXPECTED_VALUES

THIS_DIR = os.path.dirname(os.path.abspath(__file__))


@pytest.mark.parametrize("lox_program_expected", LOX_FUNCTIONS_EXPECTED_VALUES)
def test_lox_program(capsys, lox_program_expected):
    lox = Lox()

    lox_program, expected_value = lox_program_expected
    lox.run(lox_program)

    assert not lox.had_error
    assert not lox.had_runtime_error

    output = capsys.readouterr().out.splitlines()
    assert output == expected_value

