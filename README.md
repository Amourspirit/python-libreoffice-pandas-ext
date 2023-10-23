# Python Pandas Extension for LibreOffice

[Pandas](https://pandas.pydata.org/) is a fast, powerful, flexible and easy to use open source data analysis and manipulation tool, built on top of the Python programming language.

## Example

The following example shows how to use Pandas to create a data frame and then use the data frame to populate a Calc spreadsheet.
The source code can be found in the [macro](./macro) folder.

```python
import pandas as pd

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
```

## Dev Container

This project is generated from [Python LibreOffice Pip Extension Template](https://github.com/Amourspirit/python-libreoffice-pip) which in turn was generated from the [Live LibreOffice Python Template] This means this project can be run/developed in a Development container or Codespace with full access to LibreOffice.

### Accessing LibreOffice

The ports to access LibreOffice are `3032` for http and `3033` for https.

See also: [How do I access the LibreOffice in a GitHub Codespace?](https://github.com/Amourspirit/live-libreoffice-python/wiki/FAQ#how-do-i-access-the-libreoffice-in-a-github-codespace) on [Live LibreOffice Python Template].

## Running Macro

The example macro is already installed in LibreOffice when the container is started and be found in the [macro](./macro) folder.
However, the extension must be installed before running the example macro. From LibreOffice open the extension manager, `Tools -> Extension Manager ...` and add `pandas.oxt`

When prompted choose `Only for me`. Restart LibreOffice and Pandas will install.

![Add Extension Dialog](https://github.com/Amourspirit/python-libreoffice-pandas-ext/assets/4193389/d62d9a5b-299d-48bd-bc41-0d0ff6718364)

![For whom do you want to install the extension dialog box](https://github.com/Amourspirit/python-libreoffice-numpy-ext/assets/4193389/ee0369a2-f2f9-45d9-b093-66a138078f2a)

[Live LibreOffice Python Template]:https://github.com/Amourspirit/live-libreoffice-python