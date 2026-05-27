from __future__ import annotations

from dataclasses import make_dataclass
from typing import Any

from tokens import Token
from expr import Expr


class Stmt:
    pass


_SPEC: dict[str, list[tuple[str, Any]]] = {
    "Expression": [("expr", Expr)],
    "Function": [("name", Token), ("params", list[Token]), ("body", list[Stmt])],
    "If": [("condition", Expr), ("then_branch", Stmt), ("else_branch", Stmt | None)],
    "Print": [("expr", Expr)],
    "Var": [("name", Token), ("initializer", Expr | None)],
    "While": [("condition", Expr), ("body", Stmt)],
    "Block": [("statements", list[Stmt])],
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
        classes[name] = cls
    return classes


_classes = _build_stmt_classes()
Expression = _classes["Expression"]
Function = _classes["Function"]
If = _classes["If"]
Print = _classes["Print"]
Var = _classes["Var"]
While = _classes["While"]
Block = _classes["Block"]

__all__ = ["Expr", "Expression", "Function", "If", "Print", "Var", "While", "Block"]
