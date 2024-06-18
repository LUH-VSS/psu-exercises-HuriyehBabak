from dataclasses import Field, dataclass, fields, field
from utils.typeshed import check_type
from typing import Any, Iterator, Optional, List


@dataclass
class Node:
    def __post_init__(self) -> None:
        """For AST Nodes, we do some validation on the initialization values:
        1. Ensure that all fields are either children or attribute
        2. Children have to be initialized to the correct type
        """
        for f in fields(self):
            field_name = "{}.{}".format(type(self).__name__, f.name)
            assert f.metadata.get("valid"), "The field {} is not annotated as Node.child() or Node.attribute()".format(
                field_name
            )

            # Check the type
            if f.init and f.type:
                check_type(f.name, getattr(self, f.name), f.type)

    @staticmethod
    def child(multiple: bool = False, repr: bool = False) -> Field:
        """Field initializer for AST Children"""
        return field(init=True, repr=repr, metadata=dict(valid=True, child=True, multiple=multiple))

    @staticmethod
    def attribute(init: bool = False) -> Field:
        """Field initializer for AST children"""
        if init:
            return field(init=True, metadata=dict(valid=True, child=False))
        else:
            return field(init=False, default=None, metadata=dict(valid=True, child=False))

    def name(self) -> str:
        return type(self).__name__

    def children(self) -> Iterator[Any]:
        for f in fields(self):
            value = getattr(self, f.name)
            if f.metadata["child"]:
                if value is None:
                    continue
                if f.metadata["multiple"]:
                    for idx, child in enumerate(value):
                        yield "{}[{}]".format(f.name, idx), child
                else:
                    yield (f.name, value)


@dataclass
class TypeExpr(Node):
    ...
    # FIXME: Forbid __eq__ and implement specific __eq__ methods (alternative: equal()).


@dataclass
class Decl(Node): ...


@dataclass
class Stmt(Node): ...


@dataclass
class Expr(Stmt):
    type: TypeExpr = Node.attribute()


################################################################
# Types


@dataclass
class TypeInt(TypeExpr):
    def __repr__(self) -> str:
        return "int"


@dataclass
class TypePointer(TypeExpr):
    pointee: TypeExpr = Node.child(repr=True)

    def __repr__(self) -> str:
        return f"pointer({repr(self.pointee)})"

    def __eq__(self, other: Any) -> bool:
        if not isinstance(other, TypePointer):
            return False
        return self.pointee == other.pointee


@dataclass
class TypeFunction(TypeExpr):
    return_type: TypeExpr = Node.child(repr=True)
    param_types: List[TypeExpr] = Node.child(repr=True, multiple=True)

    def __repr__(self) -> str:
        return f"func({repr(self.return_type)}, {repr(self.param_types)})"

    def __eq__(self, other: Any) -> bool:
        if not isinstance(other, TypeFunction):
            return False
        return self.return_type == other.return_type and self.param_types == other.param_types


################################################################
# Declarations


@dataclass
class Identifier(Expr):
    name: str = Node.attribute(init=True)


@dataclass
class Literal(Expr):
    value: int = Node.attribute(init=True)


@dataclass
class CodeBlock(Node):
    statements: List[Stmt] = Node.child(multiple=True)


@dataclass
class NamedDecl(Decl):
    name: str = Node.attribute(init=True)
    type: TypeExpr = Node.child()


@dataclass
class VarDecl(NamedDecl, Stmt): ...


@dataclass
class FuncDecl(NamedDecl):
    params: List[VarDecl] = Node.child(multiple=True)
    statements: List[Stmt] = Node.child(multiple=True)

    def __init__(self, name: str, params: List[VarDecl], return_type: TypeInt, statements: List[Stmt]) -> None:
        self.params = params
        self.statements = statements
        param_types = [p.type for p in params]
        func_type = TypeFunction(return_type, param_types)
        super().__init__(name, func_type)

    def __repr__(self):
        return f"FuncDecl(name={self.name}, type={self.type})"


@dataclass
class TranslationUnitDecl(Decl):
    decls: List[NamedDecl] = Node.child(multiple=True)


################################################################
# Statements
@dataclass
class IfStmt(Stmt):
    cond: Expr = Node.child()
    then_block: CodeBlock = Node.child()
    else_block: Optional[CodeBlock] = Node.child()


@dataclass
class ReturnStmt(Stmt):
    expr: Expr = Node.child()


@dataclass
class WhileStmt(Stmt):
    cond: Expr = Node.child()
    body: CodeBlock = Node.child()


@dataclass
class ForStmt(Stmt):
    init: Expr = Node.child()
    cond: Expr = Node.child()
    next: Expr = Node.child()
    body: CodeBlock = Node.child()


@dataclass
class BreakStmt(Stmt):
    pass


@dataclass
class ContinueStmt(Stmt):
    pass


################################################################
# Expressions


@dataclass
class UnopExpr(Expr):
    expr: Expr = Node.child()


@dataclass
class Not(UnopExpr): ...


@dataclass
class Neg(UnopExpr): ...


@dataclass
class Ref(UnopExpr): ...


@dataclass
class Deref(UnopExpr): ...


@dataclass
class BinopExpr(Expr):
    lhs: Expr = Node.child()
    rhs: Expr = Node.child()


@dataclass
class Assign(BinopExpr): ...


@dataclass
class Add(BinopExpr): ...


@dataclass
class Sub(BinopExpr): ...


@dataclass
class Mul(BinopExpr): ...


@dataclass
class Div(BinopExpr): ...


@dataclass
class LessEqual(BinopExpr): ...


@dataclass
class CallExpr(Expr):
    callee: Identifier = Node.child()
    arguments: List[Expr] = Node.child(multiple=True)
