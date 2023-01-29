import json
import os
import pytest
import sys


THIS_DIR = os.path.dirname(os.path.abspath(__file__))
BASE_DIR = os.path.join(THIS_DIR, "..")
SRC_DIR = os.path.join(BASE_DIR, "src")
AST_DIR = os.path.join(BASE_DIR, "pylox_ast")

for path in [BASE_DIR, SRC_DIR, AST_DIR]:
    if path not in sys.path:
        sys.path.append(path)


from src.lox import Lox


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
