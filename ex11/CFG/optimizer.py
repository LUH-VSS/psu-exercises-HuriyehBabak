# coding: utf-8

from CFG.types import (
    Function,
    Variable,
    TranslationUnit,
    Add,
    Sub,
    Mul,
    Assign,
    Div,
    LessEqual,
    IfGoto,
    Goto,
    BasicBlock,
    BinopInstruction,
    Store,
    Call,
    Return,
)
from utils import double_dispatch  # type: ignore
from CFG.utils import EquivalenceClasses  # For the constant value propagation
import logging
from typing import Optional, Tuple, Union

logger = logging.getLogger("optimizer")


class Optimizer:
    def __init__(self) -> None:
        self.optimizers = []
        # Look at a single Instruction
        self.optimizers.append(ConstantFolding())
        # Look at a whole basic block
        self.optimizers.append(ConstantValuePropagation())
        # CFG-Optimization
        self.optimizers.append(MergeBlocks())
        self.optimizers.append(RedundantJumpElimination())
        # Garbage Cleanup
        self.optimizers.append(DeadBlockElimination())
        self.optimizers.append(DeadVariableElimination())

    def optimize(self, program: TranslationUnit) -> None:
        for func in program.functions:
            self.optimize_function(func)

    def optimize_function(self, function: Function) -> bool:
        changed = True
        while changed:
            changed = False
            for optimizer in self.optimizers:
                c = optimizer.optimize_function(function)
                if c:
                    logger.info(f"{function} changed by {optimizer.__class__.__name__}")
                    changed = True
        return changed


################################################################
# Part 1: Constant Folding


class ConstantFolding:
    def optimize_function(self, function: Function) -> bool:
        changed = False
        for bb in function.basic_blocks:
            for idx, instr in enumerate(bb.instructions):
                replace = double_dispatch(self, "fold_", instr, ignore_missing=True)
                if replace:
                    logger.debug(f"Constant-Folding: {instr} -> {replace}")
                    bb.instructions[idx] = replace
                    changed = True
        return changed

    def constant(self, operand: Union[int, Variable]) -> bool:
        return isinstance(operand, int)

    def fold_Add(self, instr: Add) -> Optional[Assign]:
        if isinstance(instr.lhs, int) and isinstance(instr.rhs, int):
            return Assign(instr.dst, instr.lhs + instr.rhs)

    def fold_Sub(self, instr: Sub) -> Optional[Assign]:
        if isinstance(instr.lhs, int) and isinstance(instr.rhs, int):
            return Assign(instr.dst, instr.lhs - instr.rhs)

    def fold_Mul(self, instr: Mul) -> Optional[Assign]:
        if isinstance(instr.lhs, int) and isinstance(instr.rhs, int):
            return Assign(instr.dst, instr.lhs * instr.rhs)

    def fold_Div(self, instr: Div) -> Optional[Assign]:
        if isinstance(instr.lhs, int) and isinstance(instr.rhs, int):
            return Assign(instr.dst, instr.lhs // instr.rhs)

    def fold_LessEqual(self, instr: LessEqual) -> Optional[Assign]:
        if isinstance(instr.lhs, int) and isinstance(instr.rhs, int):
            return Assign(instr.dst, int(instr.lhs <= instr.rhs))

    def fold_IfGoto(self, instr: IfGoto) -> Optional[Goto]:
        if self.constant(instr.cond):
            if instr.cond:
                return Goto(instr.then_label)
            else:
                return Goto(instr.else_label)


################################################################
# Part 2: ConstantValuePropagation


class ConstantValuePropagation:
    def optimize_function(self, function: Function) -> bool:
        changed = False
        CFG = function.CFG()

        states: dict[BasicBlock, EquivalenceClasses] = {}
        for bb in function.basic_blocks:
            states[bb] = EquivalenceClasses()

        worklist = list(function.basic_blocks)
        while worklist != []:
            bb = worklist.pop(0)

            if bb != function.entry_block:
                d_ins = [states[pred] for pred in CFG.predecessors[bb]]
                d_in = EquivalenceClasses.merge(d_ins)
            else:
                d_in = EquivalenceClasses()

            block_changed, d_out = self.transform(bb, d_in)

            if d_out != states[bb]:
                states[bb] = d_out
                for succ in CFG.successors[bb]:
                    worklist.append(succ)

            # Did the transformation change the instructions?
            changed = changed or block_changed

        for bb in function.basic_blocks:
            logger.debug(f"{function}: {bb} after_state: {states[bb]}")

        return changed

    def transform(self, bb: BasicBlock, equivalences: EquivalenceClasses) -> Tuple[bool, EquivalenceClasses]:
        equivalences = EquivalenceClasses(equivalences)
        changed = False

        def replace(operand):
            equiv_set = equivalences.find(operand)
            if len(equiv_set) == 1:
                return operand

            for elem in equiv_set:
                if isinstance(elem, int):
                    return elem
            for elem in equiv_set:
                if not elem.temporary and operand.temporary:
                    return elem
            return operand

        for instr in bb.instructions:
            old_str = repr(instr)
            if isinstance(instr, BinopInstruction):
                instr.lhs = replace(instr.lhs)
                instr.rhs = replace(instr.rhs)
            elif isinstance(instr, (Assign, Store, Return)):
                instr.value = replace(instr.value)
            elif isinstance(instr, Call):
                r = replace(instr.callee)
                assert isinstance(r, Function)
                instr.callee = r
                instr.arguments = [replace(a) for a in instr.arguments]
            elif isinstance(instr, IfGoto):
                instr.cond = replace(instr.cond)

            if old_str != repr(instr):
                logger.debug(f"Value-Propagation: '{old_str}' -> '{instr}', values={equivalences}")
                changed = True

            # Kill Equivalences
            if instr.operand_dst():
                dst = instr.operand_dst()
                equivalences.kill(dst)

            # Establish new Equivalences
            if isinstance(instr, Assign):
                # kill(instr.dst) already happended
                equivalences.union(instr.dst, instr.value)
            elif isinstance(instr, (Store, Call)):
                equivalences = EquivalenceClasses()

        return changed, equivalences


################################################################
# Part 3: CFG-Optimization


class MergeBlocks:
    """Merge two blocks if they are strictly subsequent"""

    def optimize_function(self, function: Function) -> bool:
        changed = False
        CFG = function.CFG()

        # TODO: Merge den aktuellen Block und seine Nachfolger,
        #       wenn this nur einen Nachfolger hat und dieser Nachfolger
        #       nur this als Vorgänger hat.

        return changed


class RedundantJumpElimination:
    def optimize_function(self, function: Function) -> bool:
        changed = False
        CFG = function.CFG()

        for this in function.basic_blocks:
            if len(CFG.successors[this]) == 1 and len(this.instructions) == 1:
                goto_label = CFG.successors[this][0].label
                for prev in CFG.predecessors[this]:
                    logger.debug(f"Dead-Code Elimination: {prev} -> {this} -> {goto_label}")
                    last_instr = prev.instructions[-1]
                    if isinstance(last_instr, Goto):
                        assert last_instr.label == this.label
                        last_instr.label = goto_label
                        changed = True
                    if isinstance(last_instr, IfGoto):
                        if last_instr.then_label == this.label:
                            last_instr.then_label = goto_label
                            changed = True
                        if last_instr.else_label == this.label:
                            last_instr.else_label = goto_label
                            changed = True

            # Remove everything after an return statement
            for idx, instr in enumerate(this.instructions):
                if isinstance(instr, Return) and len(this.instructions[idx + 1 :]) > 0:
                    del this.instructions[idx + 1 :]
                    changed = True
        return changed


class DeadBlockElimination:
    """Remove all blocks that have no predecessor."""

    def optimize_function(self, function: Function) -> bool:
        changed = False

        CFG = function.CFG()

        for bb in list(function.basic_blocks):
            if len(CFG.predecessors[bb]) == 0 and bb != function.entry_block:
                logger.debug(f"Dead-Code Elimination: {bb} has no predecessors")
                function.basic_blocks.remove(bb)
                changed = True

        return changed


################################################################
# 4. Dead Variable Elimination


class DeadVariableElimination:
    def optimize_function(self, function: Function) -> bool:
        changed = False
        never_read = set(function.variables)

        # TODO: Analyse: Finde alle Variablen, die in einer Instruktion gelesen werden.
        #                (Tipp: Instruction.operands_src())
        # TODO: Transformation: Alle Variablen, die nie gelesen werden, können gelöscht werden.
        #       - Lösche Instruktionen, die diese Variablen schreiben (Tipp: Instruction.operand_dst())
        #       - Lösche die Variablen aus der Funktion

        return changed
