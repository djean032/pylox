from __future__ import annotations

from dataclasses import make_dataclass
from typing import Any

from tokens import Token


class Expr:
    pass


_SPEC: dict[str, list[tuple[str, Any]]] = {
    "Binary": [("left", Expr), ("operator", Token), ("right", Expr)],
    "Unary": [("operator", Token), ("right", Expr)],
    "Grouping": [("expression", Expr)],
    "Literal": [("value", object)],
    "Variable": [("name", Token)],
}


def _build_expr_classes() -> dict[str, type[Expr]]:
    classes: dict[str, type[Expr]] = {}
    for name, fields in _SPEC.items():
        cls = make_dataclass(
            cls_name=name,
            fields=fields,
            bases=(Expr,),
            slots=True,
        )
        classes[name] = cls
    return classes


_classes = _build_expr_classes()
Binary = _classes["Binary"]
Unary = _classes["Unary"]
Grouping = _classes["Grouping"]
Literal = _classes["Literal"]
Variable = _classes["Variable"]

__all__ = ["Expr", "Binary", "Unary", "Grouping", "Literal", "Variable"]
