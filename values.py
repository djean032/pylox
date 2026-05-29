from __future__ import annotations

from typing import TYPE_CHECKING, TypeAlias, Union

if TYPE_CHECKING:
    from loxcallable import LoxCallable
    from loxinstance import LoxInstance
    from loxclass import LoxClass


LoxValue: TypeAlias = Union[
    float, str, bool, "LoxCallable", "LoxInstance", "LoxClass", None
]
