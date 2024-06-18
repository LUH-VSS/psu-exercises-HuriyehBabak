from AST.visitor import Visitor
from AST.types import *
from typing import List, Optional, Union


class Namespace:
    def __init__(self, decl: Union[TranslationUnitDecl, FuncDecl, CodeBlock]) -> None:
        self.decl = decl
        self.names = {}

    def createName(self, name: str, decl: Union[FuncDecl, VarDecl], overloaded: bool = False) -> None:
        if overloaded:
            self.names[name] = self.names.get(name, []) + [decl]
        else:
            assert name not in self.names, "Duplicate Definition of Name: {}".format(name)
            self.names[name] = decl

    def findName(self, name: str) -> Optional[Union[VarDecl, List[FuncDecl]]]:
        return self.names.get(name)

    def __repr__(self):
        return "ns@{}:{}".format(self.decl, self.names)


class SymbolTable:
    def __init__(self) -> None:
        self.namespaces = []

    def openNamespace(self, decl: Union[TranslationUnitDecl, FuncDecl, CodeBlock]) -> None:
        NS = Namespace(decl)
        self.namespaces.append(NS)

    def closeNamespace(self, decl: Union[TranslationUnitDecl, FuncDecl, CodeBlock]) -> None:
        """Closes the currently opened namespace by a given declaration. The declaration passed in MUST equal the instance being passed to the most recent openNamespace call.

        :param decl: The declaration of the namespace to be closed.
        """
        NS = self.namespaces.pop()
        assert NS.decl == decl, "You are holding it wrong"

    def currentFunction(self) -> FuncDecl:
        """Returns the current function within the namespace hierarchy.

        :return: The function being added the last which is in fact the current function.
        """
        # Traverse from end to start since the current function is the function
        # being append at the very last.
        for i in reversed(range(0, len(self.namespaces))):
            if isinstance(self.namespaces[i].decl, FuncDecl):
                return self.namespaces[i].decl

    def createName(self, name: str, decl: Union[FuncDecl, VarDecl], overloaded: bool = False) -> None:
        """Creates a name for a given declaration within the innermost namespace of the ns hierarchy.

        :param name: The name of the declaration.
        :param decl: The declaration.
        """
        # The name is created within the last added namespace of the hierarchy.
        self.namespaces[-1].createName(name, decl, overloaded=overloaded)

    def findName(self, name: str) -> Union[VarDecl, List[FuncDecl]]:
        """Returns a declaration by a given name within the namespace hierarchy using closest-nested scope rule (CSNR).

        :param name: The name to find.
        :return: The declaration of name. None if name does not exist.
        """
        # Iterate over all namespaces to find the declaration by name.
        # Start from behind, because CSNR operates from the inside to the outside of the namespace hierarchy.
        for i in reversed(range(0, len(self.namespaces))):
            decl = self.namespaces[i].findName(name)
            if decl != None:
                return decl
        return None

    def __repr__(self) -> str:
        return "\n".join([repr(x) for x in self.namespaces])


class SemanticAnalysis(Visitor):
    def __init__(self) -> None:
        self.ST = SymbolTable()
        self.failed = False
        self.loop_counter = 0

    def error(self, node: Node, msg: str, *args) -> None:
        print(("Error at {}: " + msg).format(node, *args))
        self.failed = True

    def post_Expr(self, N: Expr):
        """Safeguard for implementing the visitor: Handle all expressions"""
        raise NotImplementedError(N)

    def pre_Decl(self, N: Decl):
        """Safeguard for implementing the visitor: Handle all declarations"""
        raise NotImplementedError(N)

    # Namespace Control
    def pre_TranslationUnitDecl(self, N: TranslationUnitDecl) -> None:
        self.ST.openNamespace(N)

    def post_TranslationUnitDecl(self, N: TranslationUnitDecl) -> None:
        self.ST.closeNamespace(N)
        if self.failed:
            print()
            raise RuntimeError("Semantic analysis failed")

    def pre_FuncDecl(self, N: FuncDecl) -> None:
        self.ST.createName(N.name, N, overloaded=True)
        self.ST.openNamespace(N)

    def post_FuncDecl(self, N: FuncDecl) -> None:
        self.ST.closeNamespace(N)

    def pre_CodeBlock(self, N: CodeBlock) -> None:
        self.ST.openNamespace(N)

    def post_CodeBlock(self, N: CodeBlock) -> None:
        self.ST.closeNamespace(N)

    def pre_VarDecl(self, N: VarDecl) -> None:
        self.ST.createName(N.name, N)

    # Statements
    def post_IfStmt(self, N: IfStmt) -> None:
        if not isinstance(N.cond.type, TypeInt):
            self.error(N, "invalid if-condition {}, expected int", N.cond.type)

    def post_ReturnStmt(self, N: ReturnStmt) -> None:
        function = self.ST.currentFunction()
        if N.expr.type != function.type.return_type:
            self.error(N, "invalid return type ({}), expected: {}", N.expr.type, function.type)

    def pre_WhileStmt(self, N: WhileStmt) -> None:
        self.loop_counter += 1

    def post_WhileStmt(self, N: WhileStmt) -> None:
        if not isinstance(N.cond.type, TypeInt):
            self.error(N, "invalid while-condition: {}, expected int", N.cond.type)

    def pre_ForStmt(self, N: ForStmt) -> None:
        self.loop_counter += 1

    def post_ForStmt(self, N: ForStmt) -> None:
        if not isinstance(N.cond.type, TypeInt):
            self.error(N, "invalid for-condition: {}, expected int", N.cond.type)

    def post_BreakStmt(self, N: BreakStmt) -> None:
        if self.loop_counter == 0:
            self.error(N, "break statement outside of loop")

    def post_ContinueStmt(self, N: BreakStmt) -> None:
        if self.loop_counter == 0:
            self.error(N, "continue statement outside of loop")

    # Leafs of our AST

    def post_Identifier(self, N: Identifier) -> None:
        # Name resolution
        N.decl = self.ST.findName(N.name)
        if N.decl is None:
            self.error(N, "Name not found")
            N.type = TypeInt()  # Continue Semantic Analysis for more errors
            return

        if isinstance(N.decl, list):
            # Overloaded Names have more than one declaration. The
            # actual type is derived at the call-site in an ad-hoc
            # manner. There, we also override the N.decl
            N.type = None
        else:
            N.type = N.decl.type

    def post_Literal(self, N: Literal) -> None:
        """All literals are integers"""
        N.type = TypeInt()

    # Unary Expressions
    def post_UnopExpr(self, N: UnopExpr) -> None:
        if not isinstance(N.expr.type, TypeInt):
            self.error(N, "invalid type, expected int")
        N.type = N.expr.type

    def post_Ref(self, N: Ref) -> None:
        N.type = TypePointer(N.expr.type)

    def post_Deref(self, N: Deref) -> None:
        if not isinstance(N.expr.type, TypePointer):
            self.error(N, "cannot derefence non-pointer type {}", N.expr.type)
            N.type = TypeInt()  # Continue Semantic Analysis for more errors
            return
        N.type = N.expr.type.pointee

    # Binary Expressions
    def post_BinopExpr(self, N: BinopExpr) -> None:
        if N.lhs.type != N.rhs.type:
            self.error(N, "operand-type mismatch: {} <-> {}", N.lhs.type, N.rhs.type)
        if not isinstance(N.lhs.type, TypeInt):
            self.error(N, "invalid type, expected int")
        N.type = N.lhs.type

    def post_Assign(self, N: Assign) -> None:
        if N.lhs.type != N.rhs.type:
            self.error(N, "operand-type mismatch: {} <-> {}", N.lhs.type, N.rhs.type)
        N.type = N.lhs.type

    def post_CallExpr(self, N: CallExpr) -> None:
        if N.callee.decl is None:
            return

        arguments = N.arguments
        # For functions, the post_Identifier() visitor sets a list of
        # declarations, as we want to support overloaded functions.
        # However, in the current version, we do not support
        # overloading.
        assert len(N.callee.decl) == 1, "Overloading is not yet implemented"

        N.callee.decl = N.callee.decl[0]
        N.callee.type = N.callee.decl.type

        # Check the function type
        func_type = N.callee.decl.type
        if len(arguments) != len(func_type.param_types):
            self.error(N, "number of arguments do not match parameter list")
            return

        for p, a in zip(func_type.param_types, arguments):
            if p != a.type:
                self.error(N, "argument<->parameter type mismatch: {} <-> {}".format(a.type, p))
                return

        N.type = func_type.return_type
