import sys
from lox import Lox


def main():
    lox_interp = Lox()
    args = sys.argv[1:]
    lox_interp.main(args)


if __name__ == "__main__":
    main()
