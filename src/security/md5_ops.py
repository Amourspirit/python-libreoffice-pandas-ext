from __future__ import annotations
import hashlib
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from typing import Union
    from os import PathLike

    StrOrBytesPath = Union[str, bytes, PathLike[str], PathLike[bytes]]  # stable
    FileDescriptorOrPath = Union[int, StrOrBytesPath]


def get_md5_binary(fnm: FileDescriptorOrPath) -> str:
    """Gets md5 hash of binary file

    Args:
        fnm (FileDescriptorOrPath): File descriptor or path

    Returns:
        str: md5 hash
    """
    return hashlib.md5(open(fnm, "rb").read()).hexdigest()
