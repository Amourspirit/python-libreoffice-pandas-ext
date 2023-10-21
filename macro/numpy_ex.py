from __future__ import annotations

try:
    import numpy as np
except ImportError:
    raise ImportError("The Pandas Extension must be installed from the 'dist' directory before running this macro!")

from ooodev.dialog.msgbox import MsgBox
from ooodev.macro.macro_loader import MacroLoader

def msg(*args):
    with MacroLoader():
        # using MacroLoader so we can use OooDev in macros
        _ = MsgBox.msgbox("Hello World!", "Greetings")


def np_ex01(*args):
    with MacroLoader():
        # using MacroLoader so we can use OooDev in macros
        x = np.arange(15, dtype=np.int64).reshape(3, 5)
        x[1:, ::2] = -99
        _ = MsgBox.msgbox(str(x), "Numpy 01")

        _ = MsgBox.msgbox(str(x.max(axis=1)).center(50), "x.max(axis=1)")


def np_ex02(*args):
    with MacroLoader():
        # using MacroLoader so we can use OooDev in macros.
        # Generate normally distributed random numbers:
        rng = np.random.default_rng()
        samples = rng.normal(size=2500)
        _ = MsgBox.msgbox(str(samples), "Numpy 02")


g_exportedScripts = (msg, np_ex01, np_ex02)
