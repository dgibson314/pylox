import json
import os
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
    status, answer = run_program("1 + 2")
    assert status == InterpretResult.INTERPRET_OK
    assert answer == 3.0

def test_passing():
    with open("programs.json", "r") as f:
        progs = json.loads(f.read())
        for entry in progs["Passing"]:
            status, answer = run_program(entry[0])

            assert status == InterpretResult.INTERPRET_OK
            assert answer == entry[1]
