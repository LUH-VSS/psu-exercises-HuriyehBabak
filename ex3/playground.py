#!/usr/bin/env python3

from parserll1.generator import load_parser

try:
    parser = load_parser("L")
except:
    print("Parser for L0 cannot be loaded. Is your parser generator working?")
    exit(-1)

program = """
func fib(n : int) : int {
    a - b - c - d;
}
"""

parser.pprint(program, parse_tree=True)
