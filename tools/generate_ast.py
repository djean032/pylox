from __future__ import annotations

from pathlib import Path

AST_SPEC: dict[str, list[tuple[str, str]]] = {
    "Assign": [("name", "Token"), ("value", "Expr")],
    "Binary": [("left", "Expr"), ("operator", "Token"), ("right", "Expr")],
    "Call": [("callee", "Expr"), ("paren", "Token"), ("arguments", "list[Expr]")],
    "Get": [("object", "Expr"), ("name", "Token")],
    "Grouping": [("expression", "Expr")],
    "Literal": [("value", "object")],
    "Logical": [("left", "Expr"), ("operator", "Token"), ("right", "Expr")],
    "Unary": [("operator", "Token"), ("right", "Expr")],
    "Variable": [("name", "Token")],
}

STMT_SPEC: dict[str, list[tuple[str, str]]] = {
    "Block": [("statements", "list[Stmt]")],
    "Class": [("name", "Token"), ("methods", "list[Function]")],
    "Expression": [("expr", "Expr")],
    "Function": [("name", "Token"), ("params", "list[Token]"), ("body", "list[Stmt]")],
    "If": [
        ("condition", "Expr"),
        ("then_branch", "Stmt"),
        ("else_branch", "Stmt | None"),
    ],
    "Print": [("expr", "Expr")],
    "Return": [("keyword", "Token"), ("value", "Expr | None")],
    "Var": [("name", "Token"), ("initializer", "Expr | None")],
    "While": [("condition", "Expr"), ("body", "Stmt")],
}


def gen_expr_py(spec: dict[str, list[tuple[str, str]]]) -> str:
    lines: list[str] = []
    lines.append("from __future__ import annotations")
    lines.append("")
    lines.append("from dataclasses import make_dataclass")
    lines.append("from typing import Any")
    lines.append("")
    lines.append("from tokens import Token")
    lines.append("")
    lines.append("")
    lines.append("class Expr:")
    lines.append("    pass")
    lines.append("")
    lines.append("")
    lines.append("_SPEC: dict[str, list[tuple[str, Any]]] = {")
    for class_name, fields in spec.items():
        field_str = ", ".join(f'("{name}", {type_name})' for name, type_name in fields)
        lines.append(f'    "{class_name}": [{field_str}],')
    lines.append("}")
    lines.append("")
    lines.append("")
    lines.append("def _build_expr_classes() -> dict[str, type[Expr]]:")
    lines.append("    classes: dict[str, type[Expr]] = {}")
    lines.append("    for name, fields in _SPEC.items():")
    lines.append("        cls = make_dataclass(")
    lines.append("            cls_name=name,")
    lines.append("            fields=fields,")
    lines.append("            bases=(Expr,),")
    lines.append("            slots=True,")
    lines.append("        )")
    lines.append("        classes[name] = cls")
    lines.append("    return classes")
    lines.append("")
    lines.append("")
    lines.append("_classes = _build_expr_classes()")
    for class_name in spec:
        lines.append(f'{class_name} = _classes["{class_name}"]')
    lines.append("")
    exports = ", ".join(f'"{name}"' for name in ["Expr", *spec.keys()])
    lines.append(f"__all__ = [{exports}]")
    lines.append("")
    return "\n".join(lines)


def gen_stmt_py(spec: dict[str, list[tuple[str, str]]]) -> str:
    lines: list[str] = []
    lines.append("from __future__ import annotations")
    lines.append("")
    lines.append("from dataclasses import make_dataclass")
    lines.append("from typing import Any")
    lines.append("")
    lines.append("from tokens import Token")
    lines.append("from expr import Expr")
    lines.append("")
    lines.append("")
    lines.append("class Stmt:")
    lines.append("    pass")
    lines.append("")
    lines.append("")
    lines.append("_SPEC: dict[str, list[tuple[str, Any]]] = {")
    for class_name, fields in spec.items():
        field_str = ", ".join(f'("{name}", {type_name})' for name, type_name in fields)
        lines.append(f'    "{class_name}": [{field_str}],')
    lines.append("}")
    lines.append("")
    lines.append("")
    lines.append("def _build_stmt_classes() -> dict[str, type[Stmt]]:")
    lines.append("    classes: dict[str, type[Stmt]] = {}")
    lines.append("    for name, fields in _SPEC.items():")
    lines.append("        cls = make_dataclass(")
    lines.append("            cls_name=name,")
    lines.append("            fields=fields,")
    lines.append("            bases=(Stmt,),")
    lines.append("            slots=True,")
    lines.append("        )")
    lines.append("        classes[name] = cls")
    lines.append("    return classes")
    lines.append("")
    lines.append("")
    lines.append("_classes = _build_stmt_classes()")
    for class_name in spec:
        lines.append(f'{class_name} = _classes["{class_name}"]')
    lines.append("")
    exports = ", ".join(f'"{name}"' for name in ["Stmt", *spec.keys()])
    lines.append(f"__all__ = [{exports}]")
    lines.append("")
    return "\n".join(lines)


def gen_expr_pyi(spec: dict[str, list[tuple[str, str]]]) -> str:
    lines: list[str] = []
    lines.append("from __future__ import annotations")
    lines.append("")
    lines.append("from tokens import Token")
    lines.append("")
    lines.append("")
    lines.append("class Expr: ...")
    lines.append("")
    for class_name, fields in spec.items():
        lines.append(f"class {class_name}(Expr):")
        if not fields:
            lines.append("    ...")
        else:
            for field_name, field_type in fields:
                lines.append(f"    {field_name}: {field_type}")
        params = ", ".join(f"{name}: {type_name}" for name, type_name in fields)
        if params:
            lines.append(f"    def __init__(self, {params}) -> None: ...")
        else:
            lines.append("    def __init__(self) -> None: ...")
        lines.append("")
    return "\n".join(lines)


def gen_stmt_pyi(spec: dict[str, list[tuple[str, str]]]) -> str:
    lines: list[str] = []
    lines.append("from __future__ import annotations")
    lines.append("")
    lines.append("from tokens import Token")
    lines.append("from expr import Expr")
    lines.append("")
    lines.append("")
    lines.append("class Stmt: ...")
    lines.append("")
    for class_name, fields in spec.items():
        lines.append(f"class {class_name}(Stmt):")
        if not fields:
            lines.append("    ...")
        else:
            for field_name, field_type in fields:
                lines.append(f"    {field_name}: {field_type}")
        params = ", ".join(f"{name}: {type_name}" for name, type_name in fields)
        if params:
            lines.append(f"    def __init__(self, {params}) -> None: ...")
        else:
            lines.append("    def __init__(self) -> None: ...")
        lines.append("")
    return "\n".join(lines)


def main() -> None:
    repo_root = Path(__file__).resolve().parents[1]
    expr_py = repo_root / "expr.py"
    expr_pyi = repo_root / "expr.pyi"
    stmt_py = repo_root / "stmt.py"
    stmt_pyi = repo_root / "stmt.pyi"

    expr_py.write_text(gen_expr_py(AST_SPEC), encoding="utf-8")
    expr_pyi.write_text(gen_expr_pyi(AST_SPEC), encoding="utf-8")
    stmt_py.write_text(gen_stmt_py(STMT_SPEC), encoding="utf-8")
    stmt_pyi.write_text(gen_stmt_pyi(STMT_SPEC), encoding="utf-8")

    print(f"Wrote {expr_py}")
    print(f"Wrote {expr_pyi}")
    print(f"Wrote {stmt_py}")
    print(f"Wrote {stmt_pyi}")


if __name__ == "__main__":
    main()
