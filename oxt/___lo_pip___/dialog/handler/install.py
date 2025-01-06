from __future__ import annotations
from typing import Any, Tuple, TYPE_CHECKING, cast, Set
import uno
import unohelper

from com.sun.star.awt import XContainerWindowEventHandler
from com.sun.star.beans import PropertyChangeEvent  # struct
from com.sun.star.beans import XPropertyChangeListener

from ...basic_config import BasicConfig
from ...lo_util.resource_resolver import ResourceResolver

from ...oxt_logger import OxtLogger
from ...settings.install_settings import InstallSettings

if TYPE_CHECKING:
    from com.sun.star.awt import UnoControlDialog  # service
    from com.sun.star.awt import UnoControlCheckBoxModel


IMPLEMENTATION_NAME = f"{BasicConfig().lo_implementation_name}.InstallPage"


class CheckBoxListener(unohelper.Base, XPropertyChangeListener):
    def __init__(self, handler: "OptionsDialogHandler") -> None:
        self._log = OxtLogger(log_name=self.__class__.__name__)
        self._log.debug("__init__")
        self.handler = handler
        self._log.debug("__init__ done")

    def disposing(self, ev: Any) -> None:  # type: ignore  # noqa: ANN401
        pass

    def propertyChange(self, ev: PropertyChangeEvent) -> None:  # type: ignore # noqa: N802
        self._log.debug("propertyChange")
        try:
            # state (evn.NewValue) will be 1 for true and 0 for false
            src = cast("UnoControlCheckBoxModel", ev.Source)
            if src.Name in self.handler.gui_chk_map:
                if cast(int, (ev.NewValue)):
                    self.handler.no_install_packages.discard(self.handler.gui_chk_map[src.Name])
                else:
                    self.handler.no_install_packages.add(self.handler.gui_chk_map[src.Name])

        except Exception as err:
            self._log.error("propertyChange: %s", err, exc_info=True)
            raise


class OptionsDialogHandler(unohelper.Base, XContainerWindowEventHandler):
    def __init__(self, ctx: Any) -> None:  # noqa: ANN401
        self._log = OxtLogger(log_name=self.__class__.__name__)
        self._log.debug("__init__")
        self.ctx = ctx
        self._config = BasicConfig()
        self._resource_resolver = ResourceResolver(self.ctx)
        install_settings = InstallSettings()
        self._no_install_packages = install_settings.no_install_packages.copy()
        self._window_name = "install"
        self._gui_chk_map = {"chkOdfpy": "odfpy"}
        self._log.debug("__init__ done")

    # region XContainerWindowEventHandler
    def callHandlerMethod(self, window: UnoControlDialog, eventObject: Any, method: str) -> bool:  # type: ignore # noqa: ANN401, N802, N803
        self._log.debug("callHandlerMethod() %s", method)
        if method == "external_event":
            try:
                self._handle_external_event(window, eventObject)
            except Exception as e:
                self._log.error("callHandlerMethod() %s", e, exc_info=True)
            return True

    def getSupportedMethodNames(self) -> Tuple[str, ...]:  # noqa: ANN201, N802
        return ("external_event",)

    # endregion XContainerWindowEventHandler

    def _handle_external_event(self, window: UnoControlDialog, ev_name: str) -> bool:
        self._log.debug("_handle_external_event: %s", ev_name)
        if ev_name == "ok":
            self._save_data(window)
        elif ev_name == "back":
            self._load_data(window, "back")
        elif ev_name == "initialize":
            self._load_data(window, "initialize")
        return True

    def _save_data(self, window: UnoControlDialog) -> None:
        name = cast(str, window.getModel().Name)  # type: ignore
        self._log.debug("_save_data name() %s", name)
        if name != self._window_name:
            self._log.debug("_save_data name() %s != %s. Returning", name, self._window_name)
            return

        install_settings = InstallSettings()
        install_settings.no_install_packages = self._no_install_packages

        self._log.debug("_save_data() no_install_packages: %s", install_settings.no_install_packages)

    def _load_data(self, window: UnoControlDialog, ev_name: str) -> None:
        # sourcery skip: extract-method
        name = cast(str, window.getModel().Name)  # type: ignore
        self._log.debug("_load_data name() %s:", name)
        self._log.debug("_load_data() ev_name: %s", ev_name)
        if name != self._window_name:
            return
        try:
            if ev_name == "initialize":
                listener = CheckBoxListener(self)
                for control in window.Controls:  # type: ignore
                    model = control.Model
                    model.Label = self._resource_resolver.resolve_string(model.Label)
                    if control.supportsService("com.sun.star.awt.UnoControlCheckBox"):
                        if model.Name == "chkOdfpy":
                            is_checked = self.gui_chk_map["chkOdfpy"] not in self.no_install_packages
                            model.State = self.bool_to_state(is_checked)

                        model.addPropertyChangeListener("State", listener)

        except Exception as err:
            self._log.error("_load_data() %s", err, exc_info=True)
            raise err
        return

    def state_to_bool(self, state: int) -> bool:
        return bool(state)

    def bool_to_state(self, value: bool) -> int:
        return int(value)

    @property
    def resource_resolver(self) -> ResourceResolver:
        return self._resource_resolver

    @property
    def no_install_packages(self) -> Set[str]:
        return self._no_install_packages

    @property
    def gui_chk_map(self) -> dict:
        return self._gui_chk_map
