import sys
from CFG.utils import functions_to_dot
from dataclasses import dataclass, fields, field
import dataclasses
from utils.typeshed import check_type
from typing import Any, Dict, Optional, Union, List
from collections import defaultdict


class TranslationUnit:
    def __init__(self) -> None:
        self.functions = []

    def find_function(self, name: str) -> "Function":
        for f in self.functions:
            if f.name == name:
                return f
        raise ValueError(f"Function {name} does not exist")

    def dump(self):
        print("Functions:")
        for f in self.functions:
            f.dump()

    def dump_as_dot(self, filename: str) -> None:
        functions_to_dot(self.functions, filename)


class Label:
    def __init__(self, target: Union["BasicBlock", "Function"], name: str) -> None:
        self.target = target
        self.name = name

    def __repr__(self) -> str:
        return ".{}".format(self.name)


class Variable:
    def __init__(self, name: str, temporary: bool = False) -> None:
        self.name = name
        self.temporary = temporary
        self.ebp_offset: int = -1

    def __repr__(self) -> str:
        return self.name


class CFG:
    def __init__(self, function: "Function") -> None:
        self.successors: Dict["BasicBlock", List["BasicBlock"]] = {}
        self.predecessors: Dict["BasicBlock", List["BasicBlock"]] = defaultdict(list)
        for bb in function.basic_blocks:
            self.successors[bb] = bb.successors()
            for bb2 in self.successors[bb]:
                self.predecessors[bb2].append(bb)


class Function:
    def __init__(self, name: str) -> None:
        self.label = Label(self, name)
        self.name = name
        self.parameters: list[Variable] = []
        self.variables: list[Variable] = []
        self.basic_blocks: list[BasicBlock] = []
        self.entry_block: Optional[BasicBlock] = None

    def create_block(self) -> "BasicBlock":
        bb = BasicBlock("BB{}".format(len(self.basic_blocks)))
        if not self.basic_blocks:
            # The first created block becomes the entry block
            self.entry_block = bb
        self.basic_blocks.append(bb)
        return bb

    def create_variable(self, var_name: Optional[str] = None) -> Variable:
        if not var_name:
            var_name = "t{}".format(len(self.variables))
            temporary = True
        else:
            temporary = False
        var = Variable(var_name, temporary)
        self.variables.append(var)
        return var

    def create_parameter(self, name: str) -> Variable:
        var = Variable("p{}_{}".format(len(self.parameters), name))
        self.parameters.append(var)
        return var

    def dump(self):
        print("{} {{".format(self))
        for bb in self.basic_blocks:
            bb.dump()
        print("}")

    def CFG(self) -> CFG:
        """We calculate an CFG instance every time, we are asked for it.
        Thereby, the data never gets outdated."""
        return CFG(self)

    def sort_blocks(self) -> None:
        """Uses breath-first search to order the blocks. This makes the life
        of students hopefully a little bit easier."""
        visited = set()
        basic_blocks = []
        cfg = CFG(self)

        def recursive(BB1):
            if BB1 in visited:
                return
            visited.add(BB1)
            basic_blocks.append(BB1)
            for BB2 in cfg.successors[BB1]:
                recursive(BB2)

        recursive(self.entry_block)
        basic_blocks += list(set(self.basic_blocks) - visited)
        assert len(self.basic_blocks) == len(basic_blocks)
        self.basic_blocks = basic_blocks

    def __repr__(self) -> str:
        return "func:{}".format(self.label.name)


class BasicBlock:
    def __init__(self, name: str) -> None:
        self.label = Label(self, name)
        self.instructions: list[Instruction] = []

    def dump(self):
        print("{}: # successors: {}".format(self, self.successors()))
        for instr in self.instructions:
            print("  {!r}".format(instr))
        print()

    def append(self, Type: Any, *args, **kwargs) -> None:
        if isinstance(Type, str):
            Type = getattr(sys.modules[__name__], Type)
        instr = Type(*args, **kwargs)
        if len(self.instructions) > 0:
            last_instr = self.instructions[-1]
            assert not isinstance(last_instr, (Goto, IfGoto)), "Cannot append instruction to already closed block"

        self.instructions.append(instr)

    def successors(self) -> List["BasicBlock"]:
        if len(self.instructions) > 0:
            last_instr = self.instructions[-1]
            if isinstance(last_instr, Goto):
                assert isinstance(last_instr.label.target, BasicBlock)
                return [last_instr.label.target]
            if isinstance(last_instr, IfGoto):
                assert isinstance(last_instr.then_label.target, BasicBlock)
                assert isinstance(last_instr.else_label.target, BasicBlock)
                return [last_instr.then_label.target, last_instr.else_label.target]
        return []

    def __repr__(self) -> str:
        return "{}".format(self.label.name)


@dataclass
class Instruction:
    def __post_init__(self) -> None:
        """For IR Instruction, we validation that all attributes ahave the
        correct type.
        """
        for f in self.__operand_fields():
            assert f.type, "All operands must be typed."
            check_type(f.name, getattr(self, f.name), f.type)

    def __operand_fields(self):
        return [field for field in fields(self) if field.init]

    @property
    def opcode(self) -> str:
        return type(self).__name__

    def replace(self, **kwargs):
        return dataclasses.replace(self, **kwargs)

    def operands(self, ignore: List[str] = []) -> List[Any]:
        ret = []
        for f in self.__operand_fields():
            if f.name in ignore:
                continue
            if f.metadata.get("multiple"):
                ret.extend(getattr(self, f.name))
            else:
                ret.append(getattr(self, f.name))
        return ret

    def operand_dst(self) -> Optional[Variable]:
        if hasattr(self, "dst"):
            return self.dst  # type: ignore

    def operands_src(self) -> List[Any]:
        return self.operands(ignore=["dst"])

    def __repr__(self) -> str:
        operands = [repr(x) for x in self.operands_src()]
        ret = "{} {}".format(self.opcode, ", ".join(operands))
        if self.operand_dst():
            ret = "{!r:<3} := {}".format(self.operand_dst(), ret)
        return ret


@dataclass(repr=False)
class BinopInstruction(Instruction):
    dst: Variable
    lhs: Union[Variable, int]
    rhs: Union[Variable, int]


# Shortcuts for type sets to match lecture 08
@dataclass(repr=False)
class Add(BinopInstruction): ...


@dataclass(repr=False)
class Sub(BinopInstruction): ...


@dataclass(repr=False)
class Mul(BinopInstruction): ...


@dataclass(repr=False)
class Div(BinopInstruction): ...


@dataclass(repr=False)
class LessEqual(BinopInstruction): ...


@dataclass(repr=False)
class Assign(Instruction):
    dst: Variable
    value: Union[Variable, int]


# Memory
@dataclass(repr=False)
class Reference(Instruction):
    dst: Variable
    obj: Union[Variable, Label]


@dataclass(repr=False)
class Load(Instruction):
    dst: Variable
    ptr: Variable

    def __repr__(self):
        return "{} := Load *{}".format(self.dst, self.ptr)


@dataclass(repr=False)
class Store(Instruction):
    ptr: Variable
    value: Union[Variable, int]

    def __repr__(self):
        return "*{} := Store {}".format(self.ptr, self.value)


@dataclass(repr=False)
class StackAlloc(Instruction):
    dst: Variable
    size: int


@dataclass(repr=False)
class HeapAlloc(Instruction):
    dst: Variable
    size: int


@dataclass(repr=False)
class FreeAlloc(Instruction):
    value: Variable


@dataclass(repr=False)
class IfGoto(Instruction):
    cond: Union[Variable, int]
    then_label: Label
    else_label: Label


@dataclass(repr=False)
class Goto(Instruction):
    label: Label


@dataclass(repr=False)
class Call(Instruction):
    dst: Variable
    callee: Function
    arguments: List[Union[Variable, int]] = field(metadata=dict(multiple=True))


@dataclass(repr=False)
class Return(Instruction):
    value: Union[Variable, int]
