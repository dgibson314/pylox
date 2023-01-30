import json
import os
import pytest
import sys

from src.lox import Lox

THIS_DIR = os.path.dirname(os.path.abspath(__file__))
LOX_TEST_FILES = os.path.join(THIS_DIR, "lox_test_files")
PYLOX_FUNCTION_VALUES = os.path.join(THIS_DIR, "pylox_function_values.json")

@pytest.mark.parametrize("lox_program,expected", [("print 2 + 2; print 3 + 3;", ["4", "6"])])
def test_lox_file(capsys, lox_program, expected):
    lox = Lox()
    lox.run(lox_program)

    assert not lox.had_error
    assert not lox.had_runtime_error

    output = capsys.readouterr().out.splitlines()
    assert output == expected


with open(PYLOX_FUNCTION_VALUES, "r") as j:
    print(json.load(j))
