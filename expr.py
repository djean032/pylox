from __future__ import annotations

from dataclasses import make_dataclass
from typing import Any

from tokens import Token


class Expr:
    pass


_SPEC: dict[str, list[tuple[str, Any]]] = {
    "Assign": [("name", Token), ("value", Expr)],
    "Binary": [("left", Expr), ("operator", Token), ("right", Expr)],
    "Call": [("callee", Expr), ("paren", Token), ("arguments", list[Expr])],
    "Get": [("object", Expr), ("name", Token)],
    "Grouping": [("expression", Expr)],
    "Literal": [("value", object)],
    "Logical": [("left", Expr), ("operator", Token), ("right", Expr)],
    "Unary": [("operator", Token), ("right", Expr)],
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
Assign = _classes["Assign"]
Binary = _classes["Binary"]
Call = _classes["Call"]
Get = _classes["Get"]
Grouping = _classes["Grouping"]
Literal = _classes["Literal"]
Logical = _classes["Logical"]
Unary = _classes["Unary"]
Variable = _classes["Variable"]

__all__ = ["Expr", "Assign", "Binary", "Call", "Get", "Grouping", "Literal", "Logical", "Unary", "Variable"]
