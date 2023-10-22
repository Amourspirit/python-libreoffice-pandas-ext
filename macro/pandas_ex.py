from __future__ import annotations

try:
    import pandas as pd
except ImportError:
    raise ImportError("The Pandas Extension must be installed from the 'dist' directory before running this macro!")

from ooodev.dialog.msgbox import MsgBox, MessageBoxType
from ooodev.macro.macro_loader import MacroLoader
from ooodev.office.calc import Calc
from ooodev.utils.info import Info
from ooodev.utils.lo import Lo


def _do_work() -> None:
    # make sure we are working on a Calc Spreadsheet
    doc = Lo.XSCRIPTCONTEXT.getDocument()
    if not Info.is_doc_type(doc_type=Lo.Service.CALC, obj=doc):
        MsgBox.msgbox(msg="Not a Calc document", title="Error", boxtype=MessageBoxType.ERRORBOX)
        return

    # create a data frame and add some data to it.
    df = pd.DataFrame()
    df["Name"] = ["Anil", "Raju", "Arun"]
    df["Age"] = ["32", "34", "45"]

    data = (("Name", "Age"),)  # Column names
    # convert data frame values into something that Calc can use.
    data += tuple(df.itertuples(index=False, name=None))

    sheet = Calc.get_active_sheet()
    # set the data starting at cell A1
    Calc.set_array(values=data, sheet=sheet, name="A1")


def demo(*args) -> None:
    with MacroLoader():
        # using MacroLoader so we can use OooDev in macros
        _do_work()


g_exportedScripts = (demo,)
