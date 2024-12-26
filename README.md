<p align="center">
<img src="https://github.com/Amourspirit/python-libreoffice-pandas-ext/assets/4193389/76e3b356-51b1-48d4-a92b-18bdcb46fcf6" alt="Pandas Extension Logo" width="174" height="174">
</p>


# Python Pandas Extension for LibreOffice

[Pandas](https://pandas.pydata.org/) is a fast, powerful, flexible and easy to use open source data analysis and manipulation tool, built on top of the Python programming language.

This is a LibreOffice extension that allows you to use Pandas in LibreOffice python macros and scripts.

The extension is on [LibreOffice Extensions](https://extensions.libreoffice.org/en/extensions/show/41998) and found in the [dist](./dist) folder.

## Example

The following example shows how to use Pandas to create a data frame and then use the data frame to populate a Calc spreadsheet.
The source code can be found in the [macro](./macro) folder.

```python
# using OooDev to for easy access to LibreOffice
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
        MsgBox.msgbox(
            msg="Not a Calc document",
            title="Error",
            boxtype=MessageBoxType.ERRORBOX,
        )
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

## Known Issues

### AppImage

Extension does not out of the box for AppImage on Linux. This is due to the AppImage not having the correct libraries installed. The following library is required: `_b2z`.

This is a know bug: [116412](https://bugs.documentfoundation.org/show_bug.cgi?id=116412) and may be fixed in the future. This is also a bug in Windows but this extension solves that issue for Windows.

There is no quick solution for this currently.

On possible fix is to install a version of python that matches your AppImage python version using a tool such as [pyenv](https://github.com/pyenv/pyenv). Then find the `_bz2` library and copy or link it to the AppImage `site-packages`.

For example if your AppImage python version is `3.8.10` then you would install a version of python `3.8` using `pyenv` and then find the `_bz2` library and copy or link it to the AppImage `site-packages`.
The file would need to be named `_bz2.cpython-3.8.so` in the `site-packages` folder of the AppImage where `3.8` is the major and minor version of the python that AppImage is using.

Here is an example of linking the file:

```bash
ln -s /home/user/.pyenv/versions/3.8.13/lib/python3.8/lib-dynload/_bz2.cpython-38-x86_64-linux-gnu.so /home/user/.local/lib/python3.8/site-packages/_bz2.cpython-3.8.so
```

You can use the [APSO](https://extensions.libreoffice.org/en/extensions/show/apso-alternative-script-organizer-for-python) extension to find the python version of the AppImage.

You can test if the library is installed by running the following in the APSO python console:

```python
>>> import _bz2
>>> _bz2.__file__
'/home/user/.local/lib/python3.8/site-packages/_bz2.cpython-3.8.so'
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

## Pandas Version

Pandas version can be changed in the extension options.

![image](https://github.com/user-attachments/assets/9469df5b-53b8-4af6-acb9-71791c5dc6db)

[Live LibreOffice Python Template]:https://github.com/Amourspirit/live-libreoffice-python