# coding: utf-8

from AST.visitor import Visitor
from CFG.types import *
import AST.types
import logging
from typing import Union

logger = logging.getLogger("codegen")


class CodeGeneration(Visitor):
    def __init__(self) -> None:
        super().__init__()

    def rvalue(self, tree: AST.types.Expr, *args, **kwargs) -> Union[Variable, int]:
        return self._dispatch("rvalue_", tree, *args, **kwargs)

    def lvalue(self, tree, *args, **kwargs) -> Variable:
        return self._dispatch("lvalue_", tree, *args, **kwargs)

    def compile(self, ast: AST.types.TranslationUnitDecl) -> TranslationUnit:
        self.visit(ast)
        return self.current_program

    ################################################################
    # Declarations

    def visit_TranslationUnitDecl(self, decl: AST.types.TranslationUnitDecl) -> None:
        self.current_program = TranslationUnit()
        self.current_function = None
        self.current_variables = None
        self.current_block = None
        self.ir_objs = {}

        for child in decl.decls:
            self.visit(child)

    def visit_FuncDecl(self, decl: AST.types.FuncDecl) -> None:
        func = Function(decl.name)
        decl.ir_obj = func
        # Generate a Function Object
        self.current_program.functions.append(func)
        self.current_function = func
        self.current_variables = {}

        for param_decl in decl.params:
            reg = self.current_function.create_parameter(param_decl.name)
            param_decl.ir_obj = reg

        # Generate a Basic Block
        self.current_block = func.create_block()

        # Visit all statements
        for stmt in decl.statements:
            self.visit(stmt)

        self.current_block.append(Return, 0)

        # We are nice and sort the blocks for our students. Sometimes their CFG might be broken
        try:
            self.current_function.sort_blocks()
        except:
            logger.info("CFG reordering did not work. Probably your CFG is broken")

        # Teardown
        self.current_function = None
        self.current_variables = None

    def visit_VarDecl(self, decl: AST.types.VarDecl) -> None:
        reg = self.current_function.create_variable(decl.name)
        decl.ir_obj = reg

    ################################################################
    # Expressions
    def rvalue_Literal(self, literal: AST.types.Literal) -> int:
        return literal.value

    def rvalue_Identifier(self, identifier: AST.types.Identifier) -> Variable:
        return identifier.decl.ir_obj

    def lvalue_Identifier(self, identifier: AST.types.Identifier) -> Variable:
        ret = self.current_function.create_variable()
        self.current_block.append(Reference, ret, identifier.decl.ir_obj)
        return ret

    def rvalue_BinopExpr(self, binop: AST.types.BinopExpr) -> Variable:
        args = [self.rvalue(child) for _, child in binop.children()]
        reg = self.current_function.create_variable()
        self.current_block.append(binop.name(), reg, *args)
        return reg

    def rvalue_Neg(self, expr: AST.types.Neg) -> Variable:
        reg = self.current_function.create_variable()
        self.current_block.append(Sub, reg, 0, self.rvalue(expr.expr))
        return reg

    def rvalue_Ref(self, expr: AST.types.Ref) -> Variable:
        return self.lvalue(expr.expr)

    def lvalue_Ref(self, expr: AST.types.Ref) -> Variable:
        ret = self.current_function.create_variable()
        x = self.lvalue(expr.expr)
        self.current_block.append(Reference, ret, x)
        return ret

    def rvalue_Deref(self, expr: AST.types.Deref) -> Variable:
        op = self.rvalue(expr.expr)
        reg = self.current_function.create_variable()
        self.current_block.append(Load, reg, op)
        return reg

    def lvalue_Deref(self, expr: AST.types.Deref) -> Variable:
        return self.rvalue(expr.expr)

    def rvalue_CallExpr(self, call_expr: AST.types.CallExpr) -> Variable:
        args = [self.rvalue(arg) for arg in call_expr.arguments]
        ast_func = call_expr.callee.decl
        ir_func = ast_func.ir_obj
        reg = self.current_function.create_variable()
        self.current_block.append(Call, reg, ir_func, args)
        return reg

    def rvalue_Assign(self, assign: AST.types.Assign) -> Union[Variable, int]:
        rhs = self.rvalue(assign.rhs)
        if isinstance(assign.lhs, AST.types.Identifier):
            # Sonderfall für Variablen auf der linken Seite
            variable = assign.lhs.decl.ir_obj
            self.current_block.append(Assign, variable, rhs)
        else:
            ref = self.lvalue(assign.lhs)
            self.current_block.append(Store, ref, rhs)

        return rhs

    ################################################################
    # Statements
    def visit_CodeBlock(self, block: AST.types.CodeBlock) -> None:
        for stmt in block.statements:
            self.visit(stmt)

    def visit_Assign(self, assign: AST.types.Assign) -> None:
        self.rvalue_Assign(assign)

    def visit_Expr(self, assign):
        self.rvalue(assign)

    def visit_ReturnStmt(self, stmt: AST.types.ReturnStmt) -> None:
        val = self.rvalue(stmt.expr)
        self.current_block.append(Return, val)

    def visit_IfStmt(self, stmt: AST.types.IfStmt) -> None:
        then_block = self.current_function.create_block()
        else_block = self.current_function.create_block()
        after_block = self.current_function.create_block()

        cond = self.rvalue(stmt.cond)
        self.current_block.append(IfGoto, cond, then_block.label, else_block.label)

        self.current_block = then_block
        self.visit(stmt.then_block)
        self.current_block.append(Goto, after_block.label)

        self.current_block = else_block
        if stmt.else_block:
            self.visit(stmt.else_block)
        self.current_block.append(Goto, after_block.label)

        self.current_block = after_block

    def visit_WhileStmt(self, stmt: AST.types.WhileStmt) -> None:
        loop_header = self.current_function.create_block()
        loop_body = self.current_function.create_block()
        after_loop = self.current_function.create_block()

        self.current_block.append(Goto, loop_header.label)
        self.current_block = loop_header
        cond = self.rvalue(stmt.cond)
        self.current_block.append(IfGoto, cond, loop_body.label, after_loop.label)

        self.current_block = loop_body
        self.visit(stmt.body)
        self.current_block.append(Goto, loop_header.label)

        self.current_block = after_loop
