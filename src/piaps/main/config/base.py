from dataclasses import dataclass
from typing import dataclass_transform


@dataclass_transform(kw_only_default=True, frozen_default=True)
def config[ClsT](cls: type[ClsT]) -> type[ClsT]:
    return dataclass(cls, frozen=True, kw_only=True)
