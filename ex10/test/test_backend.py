# Unit testing framework
import unittest
from collections import defaultdict
from pathlib import Path
from AST.analysis import SemanticAnalysis
from CFG.codegen import CodeGeneration
from backend.X86Backend import X86Backend
import tempfile


def make_compile_run_test(filename, expected, ra, cc):
    filename = Path("programs") / filename

    def func(self):
        elf_fn, _ = self._compile(filename, ra=ra, cc=cc)
        output = self._run(elf_fn)
        l0_return = int(output["L0 Return"])

        self.assertEqual(l0_return, expected, f"[{filename},ra={ra},cc={cc}] Program did not produce expected outcome")

    return func


class TestBackend(unittest.TestCase):
    """Test the IR Code Generator."""

    def setUp(self):
        """Load the L0 Grammar."""
        from parserll1.generator import load_parser

        self.parser = load_parser("L", silent=True)

        import warnings

        warnings.simplefilter("ignore", ResourceWarning)

    def _compile(self, filename, ra, cc):
        with open(filename) as fd:
            tree = self.parser.parse(fd.read())
        SemanticAnalysis().traversal(tree)
        ir = CodeGeneration().compile(tree)

        # Assembler
        backend = X86Backend(ra=ra, cc=cc)

        # Record all instructions
        asm = defaultdict(list)
        backend_emit_instr = backend.emit_instr

        def my_emit(opcode, *args, **kwargs):
            backend_emit_instr(opcode, *args, **kwargs)
            asm[backend.current_function].append((opcode, args))

        backend.emit_instr = my_emit

        backend.emit(ir)

        if cc == "register":
            for func, instrs in asm.items():
                has_push = any([x[0] == "push" for x in instrs])
                if len(func.parameters) < 6:
                    self.assertFalse(has_push, "Calling convention should not use 'push' opcode")

        elf_fn = tempfile.mktemp()
        backend.compile(elf_fn)
        return elf_fn, asm

    def _run(self, elf_fn):
        ret = X86Backend.run(elf_fn, silent=True, timeout=1)
        return ret

    def test_xchg_spilling(self):
        _, asm = self._compile("programs/xchg.src", cc="stack", ra="remember")
        for func, instrs in asm.items():
            if func.label.name != "xchg":
                continue

            constant_register = None
            for opcode, args in instrs:
                if opcode == "mov" and "$1" in args:
                    constant_register = args[1]

                if constant_register and opcode == "mov" and constant_register == args[0]:
                    if args[1][0] == "%":
                        constant_register = args[1]
                    elif "(" in args[1]:
                        self.fail(
                            "The remembering allocator spills too many variables. Only referenced variables need to be spilled on a Load"
                        )
            break
        else:
            assert False, "Function xchg not found"


for fn, expected in (("fib.src", 2 * 55), ("fastcall.src", 100), ("xchg.src", 42), ("multiarg.src", 82)):
    for ra in ("spilling", "remember"):
        for cc in ("stack", "register"):
            name = f"test_{fn.removesuffix('.src')}_{ra}_{cc}"
            test = make_compile_run_test(fn, expected, ra, cc)
            setattr(TestBackend, name, test)


# Start unit testing when module is directly loaded.
if __name__ == "__main__":
    unittest.main()
