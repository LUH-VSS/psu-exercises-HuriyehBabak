# coding: utf-8

import logging
from utils import double_dispatch
from CFG.types import (
    Add,
    Assign,
    Div,
    Function,
    Goto,
    IfGoto,
    LessEqual,
    Load,
    Mul,
    Reference,
    Return,
    Store,
    Sub,
    TranslationUnit,
    Variable,
    Instruction,
    Call,
    BasicBlock,
)
import subprocess
import sys
import os
import tempfile
from typing import Optional, Literal, Union

logger = logging.getLogger("backend")

Register = Union[
    Literal["%eax"],
    Literal["%ebx"],
    Literal["%ecx"],
    Literal["%edx"],
    Literal["%esi"],
    Literal["%edi"],
]


class X86Backend:
    def __init__(self, ra="spilling", cc="stack"):
        self.fd = tempfile.NamedTemporaryFile("w+", suffix=".s")
        self.registers = ("%eax", "%ebx", "%ecx", "%edx", "%esi", "%edi")

        logger.info(
            "Initialize X86 backend: register allocator: %s, calling convention: %s",
            ra,
            cc,
        )

        if ra == "spilling":
            self.RA = SpillingRegisterAllocator(self)
        elif ra == "remember":
            self.RA = RememberingRegisterAllocator(self)
        else:
            raise RuntimeError(
                "Unknown register allocation strategy: %s (possible values: spilling, remember)",
                ra,
            )

        if cc == "stack":
            self.CC = StackCallingConvention(self)
        elif cc == "register":
            self.CC = RegisterCallingConvention(self)
        else:
            raise RuntimeError("Unknown calling convention: %s (possible values: stack, register)", cc)

    def compile(self, elf_fn: str):
        runtime_src_fn = os.path.join(os.path.dirname(__file__), "x86-runtime.c")
        assert self.fd
        self.fd.flush()
        logger.info("Run gcc -m32 to produce %s", elf_fn)
        subprocess.check_call(["gcc", "-m32", "-o", elf_fn, self.fd.name, runtime_src_fn])
        self.fd.close()
        self.fd = None

    @staticmethod
    def run(elf_fn: str, silent=False, timeout=None):
        if not silent:
            logger.warning("Run binary %s", elf_fn)
        output = subprocess.check_output([elf_fn], timeout=timeout)
        if not silent:
            sys.stdout.write(output.decode())
        output = [tuple(x.split(":", 1)) for x in output.decode().split("\n") if ":" in x]
        return dict(output)  # type: ignore

    def emit(self, translation_unit: TranslationUnit):
        for function in translation_unit.functions:
            self.emit_function(function)

    def emit_label(self, name: str):
        assert self.fd
        self.fd.write("{}:\n".format(name))

    def mangle_symbol(self, obj: Function):
        """Mangle the name for a given symbol. At the moment, only functions
        have a name that is addressable. If you want to implement
        static overloading. Here is the place to implement it.

        """
        assert isinstance(obj, Function)
        return "l0_" + obj.label.name

    def emit_function(self, function: Function):
        assert self.fd

        name = self.mangle_symbol(function)
        # Emit a Function Prefix
        self.fd.write(".globl {}\n".format(name))
        self.fd.write(".type {}, @function\n".format(name))

        self.current_function = function
        self.instr_count_func = 0

        # The function Body
        self.emit_label(name)

        self.RA.before_Function(function)

        assert isinstance(function.entry_block, BasicBlock)
        self.emit_basic_block(function, function.entry_block)
        rest_blocks = list(function.basic_blocks)
        rest_blocks.remove(function.entry_block)
        for bb in rest_blocks:
            self.emit_basic_block(function, bb)

        self.RA.after_Function(function)

        logger.info(f"Generated Function {function} with {self.instr_count_func} instructions")

        # Emit an Assembler Epilogue
        self.fd.write(".size {}, .-{}\n#{}\n".format(name, name, "-" * 79))

    def bb_label(self, function: Function, bb: BasicBlock | Function):
        return ".L{}_{}".format(self.mangle_symbol(function), bb.label.name)

    def emit_basic_block(self, function: Function, bb: BasicBlock):
        assert self.fd

        self.emit_label(self.bb_label(function, bb))
        self.RA.before_BasicBlock(bb)

        if function.entry_block == bb:
            self.CC.function_entry(function)

        for instr in bb.instructions:
            self.emit_comment(repr(instr))
            self.RA.before_Instruction(instr)
            double_dispatch(self, "emit_", instr, function, bb)
            self.RA.after_Instruction(instr)
            self.fd.write("\n")
            if isinstance(instr, Return):
                break

    ################################################################
    # Code Generators for each IR instruction
    def emit_comment(self, string: str):
        assert self.fd
        self.fd.write("\t## {}\n".format(string))

    def emit_instr(self, opcode: str, *args: str, comment=""):
        assert self.fd
        if comment:
            comment = "\t# " + comment
        self.fd.write("\t{} {}{}\n".format(opcode, ", ".join(args), comment))
        self.instr_count_func += 1

    def emit_Add(self, instr: Add, function: Function, bb: BasicBlock):
        lhs = self.RA.load(instr.lhs)
        rhs = self.RA.load(instr.rhs, modify=True)
        self.emit_instr("add", lhs, rhs)
        self.RA.write(rhs, instr.dst)

    def emit_Sub(self, instr: Sub, function: Function, bb: BasicBlock):
        lhs = self.RA.load(instr.lhs, modify=True)
        rhs = self.RA.load(instr.rhs)
        self.emit_instr("sub", rhs, lhs)
        self.RA.write(lhs, instr.dst)

    def emit_Mul(self, instr: Mul, function: Function, bb: BasicBlock):
        lhs = self.RA.load(instr.lhs, modify=True)
        rhs = self.RA.load(instr.rhs)
        self.emit_instr("imul", rhs, lhs)
        self.RA.write(lhs, instr.dst)

    def emit_Div(self, instr: Div, function: Function, bb: BasicBlock):
        self.RA.load(0, "%edx")
        self.RA.load(instr.lhs, "%eax", modify=True)
        self.RA.load(instr.rhs, "%ecx", modify=True)
        self.emit_instr("idiv", "%ecx")
        self.RA.write("%eax", instr.dst)  # divisor

    def emit_LessEqual(self, instr: LessEqual, function: Function, bb: BasicBlock):
        eax = self.RA.alloc_register("%eax")
        lhs = self.RA.load(instr.lhs)
        rhs = self.RA.load(instr.rhs)
        self.emit_instr("cmp", rhs, lhs)
        self.emit_instr("setle", "%al")
        self.emit_instr("movzb", "%al", eax)
        self.RA.write(eax, instr.dst)

    def emit_Goto(self, instr: Goto, function: Function, bb: BasicBlock):
        self.emit_instr("jmp", self.bb_label(function, instr.label.target))

    def emit_IfGoto(self, instr: IfGoto, function: Function, bb: BasicBlock):
        cond = self.RA.load(instr.cond)
        self.emit_instr("test", cond, cond)
        self.emit_instr("jne", self.bb_label(function, instr.then_label.target))
        self.emit_instr("jmp", self.bb_label(function, instr.else_label.target))

    def emit_Assign(self, instr: Assign, function: Function, bb: BasicBlock):
        src = self.RA.load(instr.value)
        dst = self.RA.alloc_register()
        self.emit_instr("mov", src, dst)
        self.RA.write(dst, instr.dst)

    def emit_Reference(self, instr: Reference, function: Function, bb: BasicBlock):
        assert isinstance(instr.obj, Variable)
        reg_addr = self.RA.reference(instr.obj)
        self.RA.write(reg_addr, instr.dst)

    def emit_Store(self, instr: Store, function: Function, bb: BasicBlock):
        value = self.RA.load(instr.value)
        ptr = self.RA.load(instr.ptr)
        self.emit_instr("mov", value, "({})".format(ptr))

    def emit_Load(self, instr: Load, function: Function, bb: BasicBlock):
        value = self.RA.alloc_register()
        ptr = self.RA.load(instr.ptr)
        self.emit_instr("mov", "({})".format(ptr), value)
        self.RA.write(value, instr.dst)

    def emit_Call(self, instr: Call, function: Function, bb: BasicBlock):
        # Push the Arguments
        self.CC.call_prologue(instr)

        self.emit_instr("call", self.mangle_symbol(instr.callee))

        # Remove the Arguments again
        self.CC.call_epilogue(instr)

    def emit_Return(self, instr: Return, function: Function, bb: BasicBlock):
        self.CC.function_return(function, instr.value)


class StackCallingConvention:
    def __init__(self, backend: X86Backend):
        self.backend = backend
        self.RA = backend.RA

        self.eax = None

    def call_prologue(self, instr: Call):
        for argument in reversed(instr.arguments):
            reg = self.RA.load(argument)
            self.backend.emit_instr("push", reg)
            self.RA.free_register(reg)

        self.RA.alloc_register("%eax")

    def call_epilogue(self, instr: Call):
        argc = len(instr.arguments)
        if argc > 0:
            self.backend.emit_instr("add", f"${argc*4}", "%esp")
        # Ein Call zerstört den gesamten Zustand und das Ergebnis ist
        # in %eax zu finden.
        self.RA.reset_state()
        self.RA.write("%eax", instr.dst)

    def function_entry(self, function: Function):
        # Setup the Call Frame information
        for idx, param in enumerate(function.parameters):
            param.ebp_offset = 4 * idx + 8

        slots = len(function.variables)
        self.backend.emit_instr("enter", "$" + str(slots * 4), "$0")

        for idx, var in enumerate(function.variables):
            var.ebp_offset = -4 * idx - 4

    def function_return(self, function: Function, return_value):
        self.RA.load(return_value, "%eax")
        self.backend.emit_instr("leave")
        self.backend.emit_instr("ret")


class RegisterCallingConvention(StackCallingConvention):
    def __init__(self, backend):
        super().__init__(backend)

    def function_entry(self, function: Function):
        if len(function.parameters) > len(self.backend.registers):
            return super().function_entry(function)

        # TODO: Slots für Variablen UND Parameter
        # TODO: Parameter mit Slots assoziieren
        self.RA.dump_state()

    def call_prologue(self, instr: Call):
        if len(instr.arguments) > len(self.backend.registers):
            return super().call_prologue(instr)

        # TODO: Argumente in Register laden
        raise NotImplementedError("Register Calling Convention not implemeted")

    def call_epilogue(self, instr: Call):
        if len(instr.arguments) > len(self.backend.registers):
            return super().call_epilogue(instr)

        # TODO: Ein Call zerstört den Zustand
        # TODO: Rückgabewert in Register schreiben
        raise NotImplementedError("Register Calling Convention not implemeted")
        self.RA.dump_state()


class SpillingRegisterAllocator:
    def __init__(self, backend: X86Backend):
        self.backend = backend

    def before_Function(self, function: Function): ...

    def after_Function(self, func: Function): ...

    def before_BasicBlock(self, bb: BasicBlock): ...

    def after_BasicBlock(self, bb: BasicBlock): ...

    def before_Instruction(self, instr: Instruction):
        self.available_registers = list(self.backend.registers)

    def after_Instruction(self, instr: Instruction): ...

    def _var_operand(self, variable: Variable):
        return "{}(%ebp)".format(variable.ebp_offset)

    def dump_state(self):
        """The spilling allocator has no state"""
        pass

    def reset_state(self):
        """The spilling allocator has no state"""
        pass

    def alloc_register(self, dst_reg: Optional[Register] = None):
        if dst_reg is None:
            dst_reg = self.available_registers.pop()
        else:
            assert dst_reg in self.available_registers, f"Register {dst_reg} was already allocated"
            self.available_registers.remove(dst_reg)
        return dst_reg

    def free_register(self, register: Register):
        assert register not in self.available_registers, (
            register,
            self.available_registers,
        )
        assert register in self.backend.registers
        self.available_registers.append(register)

    def load(
        self,
        src: Union[Variable, int],
        dst_reg: Optional[Register] = None,
        modify=False,
    ):
        assert isinstance(src, (Variable, int)), "Invalid Argument Type"

        dst_reg = self.alloc_register(dst_reg)

        if isinstance(src, int):
            self.backend.emit_instr("mov", "$" + str(src), dst_reg)
        elif isinstance(src, Variable):
            self.backend.emit_instr("mov", self._var_operand(src), dst_reg, comment=f"load {src}")
        return dst_reg

    def write(self, src_reg: Register, variable: Variable):
        assert isinstance(variable, Variable)
        assert src_reg in self.backend.registers

        self.backend.emit_instr("mov", src_reg, self._var_operand(variable))

    def reference(self, src: Variable, dst_reg: Optional[Register] = None):
        dst_reg = self.alloc_register(dst_reg)
        self.backend.emit_instr("lea", self._var_operand(src), dst_reg)
        return dst_reg


class RememberingRegisterAllocator(SpillingRegisterAllocator):
    def before_Function(self, function):
        super().before_Function(function)

        self.var_referenced: set[Variable] = set()
        # TODO: Find all variables that are used in Reference

        self.reset_state()

    def before_BasicBlock(self, bb):
        self.reset_state()

    def before_Instruction(self, instr):
        self.dump_state()
        self.reg_free: dict[Register, bool] = {reg: True for reg in self.backend.registers}

        # TODO: Handle end of basic block   (Goto+IfGoto)
        # TODO: Handle call   instructions  (Call)
        # TODO: Handle store  instructions  (Store)
        # TODO: Handle load   instructions  (Load)

    def after_Instruction(self, instr):
        self.dump_state()

    ################################################################
    # Register-Allocation Code
    def reset_state(self):
        """(Re-)initialize the allocator state"""
        self.reg_values: dict[Register, Optional[Union[Variable, int]]] = {reg: None for reg in self.backend.registers}
        self.reg_dirty: dict[Register, bool] = {reg: False for reg in self.backend.registers}
        self.reg_free: dict[Register, bool] = {reg: True for reg in self.backend.registers}

    def dump_state(self):
        """Dump the current state as an assembler comment"""
        regs = []
        for reg in self.backend.registers:
            if not self.reg_values[reg]:
                continue
            regs.append(f"{reg}={self.reg_values[reg]},d={int(self.reg_dirty[reg])}")
        if regs:
            self.backend.emit_comment("RA-state: " + ", ".join(regs))

    def _spill_register(self, reg: Register):
        variable = self.reg_values[reg]
        if variable and self.reg_dirty[reg]:
            assert isinstance(variable, Variable)
            self.backend.emit_instr("mov", reg, self._var_operand(variable), comment=f"spill {variable}")
            self.reg_dirty[reg] = False

    def _kill_register(self, reg: Register):
        self.reg_values[reg] = None
        self.reg_dirty[reg] = False

    ################################################################
    # The Register Allocation Code
    ################################################################

    def _find_register(self, nonspill=False):
        """Prioritized search of a register. If nonspill is given, only
        non-dirty registers are considered."""
        free_registers: list[Register] = [reg for reg in self.backend.registers if self.reg_free[reg]]

        for reg in free_registers:
            if self.reg_values[reg] is None:
                return reg

        for reg in free_registers:
            if not self.reg_dirty[reg]:
                return reg

        # The user requested that the register must not be spilled.
        # However, there is no such register available.
        if nonspill:
            return None

        return free_registers[0]

    def _load_from_register(self, cache_reg: Register, dst_reg: Optional[Register], modify: bool):
        if dst_reg and cache_reg != dst_reg:
            # We should return the value in a specific register
            if self.reg_free[cache_reg]:
                # Move the value, if the old value was not already allocated
                self.backend.emit_instr("xchg", cache_reg, dst_reg)

                def xchg(D, a, b):
                    D[a], D[b] = D[b], D[a]

                xchg(self.reg_dirty, cache_reg, dst_reg)
                xchg(self.reg_values, cache_reg, dst_reg)
            else:
                # Copy the value without noteing it
                self.backend.emit_instr("mov", cache_reg, dst_reg)

        elif not dst_reg:
            dst_reg = cache_reg  # Default is: relabling
            if modify:
                # If this value is modified anyway, we copy it to a new register
                dst_reg = self._find_register(nonspill=True)
                if dst_reg:
                    self.backend.emit_instr("mov", cache_reg, dst_reg)
        assert dst_reg is not None, "Above code should decide on an register"

        # We only Spill the register, if the user intends to modify
        # the register. If it is only used as a source register thats
        # just fine.
        if modify:
            self._spill_register(dst_reg)

        self.reg_free[dst_reg] = False

        return dst_reg

    def alloc_register(self, dst_reg: Optional[Register] = None):
        if not dst_reg:
            dst_reg = self._find_register()
        assert dst_reg
        self._spill_register(dst_reg)  # In case
        self.reg_values[dst_reg] = None
        self.reg_free[dst_reg] = False
        return dst_reg

    def free_register(self, register: Register):
        self.reg_free[register] = True

    def load(self, src, dst_reg=None, modify=False):
        # Is the value already stored in the virtual register file?
        for cache_reg, value in self.reg_values.items():
            if src == value:
                return self._load_from_register(cache_reg, dst_reg, modify)

        # Not Cached -> Load from memory
        dst_reg = self.alloc_register(dst_reg)
        if isinstance(src, int):
            self.backend.emit_instr("mov", "$" + str(src), dst_reg)
        elif isinstance(src, Variable):
            self.backend.emit_instr("mov", self._var_operand(src), dst_reg, comment=f"load {src}")
        self.reg_values[dst_reg] = src
        self.reg_dirty[dst_reg] = False

        return dst_reg

    def write(self, src_reg, variable):
        assert not self.reg_dirty[src_reg]
        self.reg_values[src_reg] = variable
        self.reg_dirty[src_reg] = True
        # The actual mov to the slot is delayed

    def reference(self, src, dst_reg=None):
        dst_reg = self.alloc_register(dst_reg)
        self.backend.emit_instr("lea", self._var_operand(src), dst_reg)
        self.reg_values[dst_reg] = None
        self.reg_dirty[dst_reg] = False
        return dst_reg
