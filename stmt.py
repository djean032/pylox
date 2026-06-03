from __future__ import annotations

from dataclasses import make_dataclass
from typing import Any, cast

from tokens import Token
from expr import Expr, Variable


class Stmt:
    pass


_SPEC: dict[str, list[tuple[str, Any]]] = {
    "Block": [("statements", list[Stmt])],
    "Class": [("name", Token), ("superclass", Variable | None), ("methods", "list[Function]")],
    "Expression": [("expr", Expr)],
    "Function": [("name", Token), ("params", list[Token]), ("body", list[Stmt])],
    "If": [("condition", Expr), ("then_branch", Stmt), ("else_branch", Stmt | None)],
    "Print": [("expr", Expr)],
    "Return": [("keyword", Token), ("value", Expr | None)],
    "Var": [("name", Token), ("initializer", Expr | None)],
    "While": [("condition", Expr), ("body", Stmt)],
}


def _build_stmt_classes() -> dict[str, type[Stmt]]:
    classes: dict[str, type[Stmt]] = {}
    for name, fields in _SPEC.items():
        cls = make_dataclass(
            cls_name=name,
            fields=fields,
            bases=(Stmt,),
            slots=True,
        )
        classes[name] = cast(type[Stmt], cls)
    return classes


_classes = _build_stmt_classes()
Block = _classes["Block"]
Class = _classes["Class"]
Expression = _classes["Expression"]
Function = _classes["Function"]
If = _classes["If"]
Print = _classes["Print"]
Return = _classes["Return"]
Var = _classes["Var"]
While = _classes["While"]

__all__ = ["Stmt", "Block", "Class", "Expression", "Function", "If", "Print", "Return", "Var", "While"]
