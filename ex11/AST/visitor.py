from AST.types import TranslationUnitDecl, Node
from utils import double_dispatch
from typing import Any, Optional


class Visitor:
    """Base Class for a Pre/Post AST-Tree Visitor."""

    def pre_Node(self, N: Node) -> None:
        pass

    def post_Node(self, N: Node) -> None:
        pass

    def _dispatch(self, prefix: str, tree: Node, *args, **kwargs) -> Any:
        return double_dispatch(self, prefix, tree, *args, **kwargs)

    # Visit this node and visit the direct children
    def visit(self, tree: Node, *args, **kwargs) -> Any:
        return self._dispatch("visit_", tree, *args, **kwargs)

    # Recursive Traversal
    def traversal(self, tree: TranslationUnitDecl) -> None:
        self._parent_paths = []
        self._traversal(tree)

    def name(self) -> Optional[str]:
        if self._parent_paths:
            return self._parent_paths[-1][1]

    def _traversal(self, tree: Node) -> None:
        assert isinstance(tree, Node), "Cannot traverse a non-Node object: " + str(tree)
        self._dispatch("pre_", tree)
        for name, child in tree.children():
            self._parent_paths.append((self, name, child))
            self._traversal(child)
            self._parent_paths.pop()
        self._dispatch("post_", tree)


class ASTDumper(Visitor):
    def __init__(self) -> None:
        self.indent = 0

    def pre_TranslationUnitDecl(self, N: TranslationUnitDecl) -> None:
        print(repr(N))

    def pre_Node(self, N: Node) -> None:
        print("  " * self.indent + self.name() + " := " + repr(N))
        self.indent += 1

    def post_Node(self, N: Node) -> None:
        self.indent -= 1
