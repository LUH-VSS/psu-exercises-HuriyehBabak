#!/usr/bin/env python3
# coding: utf-8

from parserll1.generator import *

from AST.visitor import ASTDumper
from AST.analysis import SemanticAnalysis
from CFG.codegen import CodeGeneration
from CFG.interpreter import Interpreter
from CFG.optimizer import Optimizer

import os
import subprocess
import logging
import tempfile

try:
    import coloredlogs

    coloredlogs.install(fmt="%(levelname)s %(name)s  %(message)s")
except:
    pass


def main():
    import argparse

    parser = argparse.ArgumentParser(description="PSÜ Übungsübersetzer für L0")
    parser.add_argument("source", metavar="FILE", help="Source file to compile")

    parser.add_argument("-v", "--verbose", action="store_true", help="More debug output")

    frontend = parser.add_argument_group("Parser and Semantic Analysis")
    frontend.add_argument("--dump-ast", action="store_true", help="Dump AST to standard out")

    codegen = parser.add_argument_group("IR-Code Generation")
    codegen.add_argument("--dump-ir", action="store_true", help="Dump IR Code to standard out")
    codegen.add_argument("--dump-cfg", action="store_true", help="Dump CFGs as DOT and PNG")

    optimizer = parser.add_argument_group("IR-Code Optimizer")
    optimizer.add_argument("--opt", action="store_true", help="Run the IR-optimize fixpoint iteration")

    interpreter = parser.add_argument_group("IR-Code Interpreter")
    interpreter.add_argument("--execute", "-x", action="store_true", help="Execute program in interpreter")
    interpreter.add_argument("--trace-instr", "-t", action="store_true", help="... trace executed instructions")
    interpreter.add_argument("--trace-calls", "-c", action="store_true", help="... trace invoked functions")
    interpreter.add_argument("--trace-verbose", action="store_true", help="... dump call frames")
    interpreter.add_argument("--execute-dump", action="store_true", help="Dump interpreter state after execution")

    args = parser.parse_args()

    # Initialize Logging
    if args.verbose:
        logging.basicConfig(level=logging.DEBUG)
    else:
        logging.basicConfig(level=logging.INFO)

    ################################################################
    # Load File, Parse to AST, and perform Semantic Analysis
    logging.info("Read source file `%s'", args.source)
    with open(args.source) as fd:
        parser = load_parser("L")
        tree = parser.parse(fd.read())
        SemanticAnalysis().traversal(tree)

    if args.dump_ast:
        ASTDumper().traversal(tree)
        return

    ir = CodeGeneration().compile(tree)
    logging.info("Compiled Functions: %s", ir.functions)

    if args.opt:
        Optimizer().optimize(ir)

    if args.dump_cfg:
        base, _ = os.path.splitext(args.source)
        dot_fn = base + ".dot"
        png_fn = base + ".png"
        ir.dump_as_dot(dot_fn)
        try:
            with open(png_fn, "w+") as fd:
                subprocess.call(["dot", "-Tpng", dot_fn], stdout=fd)
            logging.info("Transforming to png: %s", png_fn)
        except:
            logging.error("Program `dot' not available. Install `graphviz' to get CFGs as PNG")

    if args.dump_ir:
        ir.dump()
        return

    if args.execute:
        machine = Interpreter(ir)
        ret = machine.exec(trace=args.trace_instr, calls=args.trace_calls, frames=args.trace_verbose)
        logging.info("Interpreter executed for %s steps", machine.step_count)
        logging.info("Program returned: %s", ret)

        if args.execute_dump:
            machine.dump()

        return


if __name__ == "__main__":
    main()
