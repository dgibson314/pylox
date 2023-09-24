import sys

from pylox import PyLox

if __name__ == "__main__":
    pylox = PyLox()

    if len(sys.argv) > 2:
        print("Usage: pylox [script]")
        sys.exit(64)
    elif len(sys.argv) == 2:
        pylox.run_file(sys.argv[1])
    else:
        pylox.run_prompt()
