# coding: utf-8

from CFG.types import *
from collections import defaultdict
from typing import Optional


class Interpreter:
    def __init__(self, program: TranslationUnit) -> None:
        self.memory = [None] * 1001

        self.labels = {}
        # Insert a first function call
        for function in program.functions:
            if function.label.name == "main":
                main_ret = Variable("main_ret")
                main_ret.slot = 0
                self.memory[0] = Call(main_ret, function, [])
                self.memory[1] = None
                break
        else:
            raise RuntimeError("No main function found")
        self.pc = 2
        for function in program.functions:
            self.load_function(function)

        # 4 Register
        self.hp = self.pc  # Heap Pointer
        self.pc = 0  # Instruction Pointer
        self.sp = len(self.memory) - 1  # Stack Pointer
        self.bp = self.sp  # Base Pointer

        self.step_count = 0

    def load_function(self, function: Function) -> None:
        for bb in function.basic_blocks:
            self.labels[bb.label] = self.pc  # Next Address
            if bb == function.entry_block:
                self.labels[function.label] = self.labels[bb.label]
            for instr in bb.instructions:
                self.memory[self.pc] = instr
                self.pc += 1

            # Calculate Layout for Call_Frame
            frame_layout = ["__ret__"]
            for param in function.parameters:
                param.slot = len(frame_layout)
                frame_layout.append(param)
            for variable in function.variables:
                variable.slot = len(frame_layout)
                frame_layout.append(variable)
            function.frame_layout = frame_layout

    def dump(self) -> None:
        addr_to_label = defaultdict(list)
        for label, addr in self.labels.items():
            addr_to_label[addr].append(label)

        dots = False
        for addr, instr in enumerate(self.memory):
            if instr is None:
                if not dots:
                    print("...")
                dots = True
                continue
            dots = False
            extra = ""
            if addr in addr_to_label:
                extra = " # {}".format(addr_to_label[addr])
            print("{:>4}   {!r:<30}{}".format(addr, instr, extra))

    def dump_frame(self, sp: int, bp: int):
        (callee, return_addr, old_bp, return_value_addr) = self.memory[bp]
        print(
            "| Call Frame: size={}, Return Address=&{}, Return Value=&{}".format(
                len(callee.frame_layout), return_addr, return_value_addr
            )
        )
        for idx in reversed(range(sp + 1, bp + 1)):
            extra = ""
            offset = bp - idx
            if offset >= 0 and offset < len(callee.frame_layout):
                extra = "({})".format(callee.frame_layout[offset])
            print("| {:>4} {:<12} {!r:}".format(idx, extra, self.memory[idx]))
        print()

    def exec(self, *args, max_steps: Optional[int] = None, **kwargs) -> int:
        while max_steps is None or self.step_count <= max_steps:
            x = self.step(*args, **kwargs)
            if x is not None:
                return x

    def step(self, trace: bool = False, calls: bool = False, frames: bool = False) -> Optional[int]:
        self.step_count += 1

        def read(op):
            if isinstance(op, Variable):
                return self.memory[self.bp - op.slot]
            elif isinstance(op, int):
                return op
            else:
                raise RuntimeError(
                    "Invalid Operand: {}",
                )

        # Instruction Fetch
        instr = self.memory[self.pc]
        if trace:
            print("TRACE", self.pc, instr)
            if frames and self.bp != self.sp:
                self.dump_frame(self.sp, self.bp)
        self.pc += 1
        if isinstance(instr, Call):
            args = [read(arg) for arg in instr.arguments]
            if calls:
                print("CALL", instr.callee, instr.arguments)
            # Allocate Space on the stack for the Call Frame
            old_bp = self.bp
            self.bp = self.sp
            self.sp = self.sp - len(instr.callee.frame_layout)
            if self.sp < self.hp:
                raise RuntimeError("Stack Overflow")
            # Return Information
            self.memory[self.bp - 0] = (instr.callee, self.pc, old_bp, old_bp - instr.dst.slot)
            # Insert Arguments into the Call Frame
            for param, arg in zip(instr.callee.parameters, args):
                self.memory[self.bp - param.slot] = arg
            self.pc = self.labels[instr.callee.label]

            if calls and frames:
                self.dump_frame(self.sp, self.bp)

        elif isinstance(instr, Return):
            (callee, old_pc, old_bp, return_value_ref) = self.memory[self.bp]
            return_value = read(instr.value)
            if calls:
                print("RETURN", callee, return_value)
            if calls and frames:
                self.dump_frame(self.sp, self.bp)
            self.memory[return_value_ref] = return_value
            self.sp = self.bp
            self.bp = old_bp
            self.pc = old_pc
        elif isinstance(instr, (LessEqual, Add, Sub, Mul, Div, Assign)):
            ops = list(map(read, instr.operands_src()))
            # Keep in Mind this is not 32 Bit Operations. I'm sorry Mum
            operations = {
                LessEqual: lambda a, b: int(a <= b),
                Add: lambda a, b: (a + b),
                Sub: lambda a, b: (a - b),
                Mul: lambda a, b: (a * b),
                Div: lambda a, b: (a // b),
                Assign: lambda x: x,
            }
            value = operations[type(instr)](*ops)
            self.memory[self.bp - instr.dst.slot] = value
        elif isinstance(instr, Reference):
            ref = self.bp - instr.obj.slot
            self.memory[self.bp - instr.dst.slot] = ref

        elif isinstance(instr, Store):
            ptr = read(instr.ptr)
            value = read(instr.value)
            self.memory[ptr] = value
        elif isinstance(instr, Load):
            ptr = read(instr.ptr)
            self.memory[self.bp - instr.dst.slot] = self.memory[ptr]
        elif isinstance(instr, IfGoto):
            if read(instr.cond) != 0:
                self.pc = self.labels[instr.then_label]
            else:
                self.pc = self.labels[instr.else_label]
        elif isinstance(instr, Goto):
            self.pc = self.labels[instr.label]
        elif instr is None:
            return self.memory[-1]
        else:
            raise RuntimeError("Unsupported Operation: {}".format(instr))
