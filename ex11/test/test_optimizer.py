# Unit testing framework
import unittest
from pathlib import Path
from AST.analysis import SemanticAnalysis
from CFG.codegen import CodeGeneration
from CFG.interpreter import Interpreter
from CFG.optimizer import Optimizer
from CFG.types import Goto


def make_compile_run_test(filename, expected, max_steps=10000):
    filename = Path("programs") / filename

    def func(self):
        ir = self._compile(filename, optimize=False)
        return_value, machine = self._run(ir, max_steps=max_steps)

        self.assertNotEqual(
            machine.step_count, max_steps, f"{filename}: (unoptimized) Execution ran into timeout. Endless loop?"
        )
        self.assertIsNotNone(return_value, f"{filename}: (unoptimized) Execution did not yield any result")
        self.assertEqual(return_value, expected, f"{filename}: (unoptimized) Execution yielded incorrect result")

        ir = self._compile(filename, optimize=True)
        return_value_opt, machine_opt = self._run(ir, max_steps=max_steps)

        self.assertEqual(
            return_value_opt,
            return_value,
            f"{filename}: Optimized program did not yield same result as the original version.",
        )

        self.assertLessEqual(
            machine_opt.step_count,
            machine.step_count,
            f"{filename}: Optimized program executed longer than original program.",
        )

    func.__doc__ = f"Compile and run: {filename}"
    return func


class TestOptimizer(unittest.TestCase):
    """Test the IR Code Generator."""

    def setUp(self):
        """Load the L0 Grammar."""
        from parserll1.generator import load_parser

        self.parser = load_parser("L", silent=True)

    def _compile(self, filename, optimize=True):
        with open(filename) as fd:
            tree = self.parser.parse(fd.read())
        SemanticAnalysis().traversal(tree)
        ir = CodeGeneration().compile(tree)
        if optimize:
            Optimizer().optimize(ir)
        return ir

    def _run(self, ir, **kwargs):
        machine = Interpreter(ir)
        ret = machine.exec(**kwargs)
        return (ret, machine)

    test_fibonacci = make_compile_run_test("fib.src", 2 * 55)
    test_opt_merge = make_compile_run_test("opt-merge.src", 42)
    test_opt_dead_var = make_compile_run_test("opt-dead-variables.src", 0)
    test_opt_dead_var_2 = make_compile_run_test("opt-dead-variables2.src", 5)

    def test_opt_merge_f1(self):
        ir = self._compile("programs/opt-merge.src")
        f1 = ir.find_function("f1")
        self.assertEqual(len(f1.basic_blocks), 1, "opt-merge.src/f1(): All blocks should be merged into one block")
        for instr in f1.basic_blocks[0].instructions[:-1]:
            self.assertNotIsInstance(
                instr, Goto, "opt-merge.src/f1(): No gotos should be in the middle of a basic block"
            )
        self.assertEqual(
            len(f1.basic_blocks[0].instructions), 7, "opt-merge.src/f1(): Number of instructions is not correct"
        )

    def test_opt_merge_f2(self):
        ir = self._compile("programs/opt-merge.src")
        f2 = ir.find_function("f2")
        self.assertEqual(len(f2.basic_blocks), 4, "opt-merge.src/f2(): No merging should happen")

    def test_dead_var_f1(self):
        ir = self._compile("programs/opt-dead-variables.src")
        f1 = ir.find_function("f1")
        self.assertEqual(len(f1.basic_blocks), 1, "opt-dead-variables.src/f1(): Invalid number of blocks")
        bb = f1.basic_blocks[0]
        self.assertEqual(
            len(bb.instructions),
            1,
            "opt-dead-variables.src/f1(): After dead variable elimination, only one instruction remains",
        )

        self.assertEqual(len(f1.variables), 0, "opt-dead-variables.src/f1(): Invalid number of variables")

    def test_fibonacci_compile(self):
        ir = self._compile("programs/fib.src")
        fib_iter = ir.find_function("fib_iter")
        self.assertEqual(len(fib_iter.basic_blocks), 4, "fib.src/fib_iter_iter(): Invalid number of blocks")

        self.assertLessEqual(len(fib_iter.variables), 7, "fib.src/fib_iter(): Invalid number of variables")

        (_, machine) = self._run(ir)

        self.assertLessEqual(machine.step_count, 2010, "fib.src: Execution is still too slow")


# Start unit testing when module is directly loaded.
if __name__ == "__main__":
    unittest.main()
