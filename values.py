from __future__ import annotations

from typing import TYPE_CHECKING, TypeAlias, Union

if TYPE_CHECKING:
    from loxcallable import LoxCallable


LoxValue: TypeAlias = Union[float, str, bool, "LoxCallable", None]
