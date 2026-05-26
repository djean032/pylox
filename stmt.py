from __future__ import annotations

from dataclasses import make_dataclass
from typing import Any

from tokens import Token
from expr import Expr


class Stmt:
    pass


_SPEC: dict[str, list[tuple[str, Any]]] = {
    "Expression": [("expr", Expr)],
    "Print": [("expr", Expr)],
    "Var": [("name", Token), ("initializer", Expr)],
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
Print = _classes["Print"]
Var = _classes["Var"]

__all__ = ["Expr", "Expression", "Print", "Var"]
