import json
import os
import pytest
import sys

TEST_DIR = os.path.dirname(os.path.abspath(__file__))
TOP_DIR = os.path.join(TEST_DIR, "..")
SRC_DIR = os.path.join(TOP_DIR, "src")

sys.path.append(SRC_DIR)

from pylox import PyLox
from vm import InterpretResult

def run_program(prog_string):
    return PyLox().run(prog_string)

def test_add():
    status = run_program("print 1 + 2;")
    assert status == InterpretResult.INTERPRET_OK

def test_passing(capsys):
    with open("programs.json", "r") as f:
        progs = json.loads(f.read())
        for entry in progs["Passing"]:
            status = run_program(entry[0])
            captured = capsys.readouterr()

            assert status == InterpretResult.INTERPRET_OK
            assert captured.out == entry[1]
