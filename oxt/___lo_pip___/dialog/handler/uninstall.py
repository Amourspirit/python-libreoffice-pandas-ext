from __future__ import annotations
from typing import Any, TYPE_CHECKING, List, Tuple, cast, Set
import contextlib

import uno
import unohelper

from com.sun.star.awt import XActionListener  # type: ignore
from com.sun.star.awt import XContainerWindowEventHandler  # type: ignore
from com.sun.star.beans import PropertyChangeEvent  # type: ignore # struct
from com.sun.star.beans import XPropertyChangeListener  # type: ignore
from com.sun.star.awt.MessageBoxType import QUERYBOX, INFOBOX, ERRORBOX  # type: ignore

from ...basic_config import BasicConfig
from ...lo_util.resource_resolver import ResourceResolver

from ...settings.settings import Settings
from ...oxt_logger import OxtLogger

# from ...ver.req_version import ReqVersion
# from ...ver.rules.ver_rules import VerRules
from ..message_dialog import MessageDialog


if TYPE_CHECKING:
    from com.sun.star.awt import UnoControlDialog  # type: ignore # service
    from com.sun.star.awt import UnoControlCheckBoxModel  # type: ignore
    from com.sun.star.awt import UnoControlButton  # type: ignore # service


IMPLEMENTATION_NAME = f"{BasicConfig().lo_implementation_name}.OptUninstallPage"


class ButtonUninstallListener(unohelper.Base, XActionListener):
    def __init__(self, dialog_handler: "OptionsDialogUninstallHandler") -> None:
        self._log = OxtLogger(log_name=self.__class__.__name__)
        self._log.debug("ButtonListener.__init__")
        self.dialog_handler = dialog_handler
        self._log.debug("ButtonListener.__init__ done")
        self._config = BasicConfig()

    def disposing(self, Source: Any) -> None:  # noqa: ANN401, N803
        pass

    def actionPerformed(self, rEvent: Any) -> None:  # noqa: ANN401, N802, N803
        # sourcery skip: extract-method
        self._log.debug("ButtonListener.actionPerformed")
        try:
            cmd = str(rEvent.ActionCommand)
            self._log.debug(f"ButtonListener.actionPerformed cmd: {cmd}")
            if cmd == "UninstallItems":
                if not self.dialog_handler.uninstall_pkgs:
                    self._log.debug("ButtonListener.actionPerformed: uninstall_pkg is False")
                    title = self.dialog_handler._resource_resolver.resolve_string("msg13")
                    msg = self.dialog_handler._resource_resolver.resolve_string("msg16")
                    _ = MessageDialog(
                        self.dialog_handler.ctx,
                        title=title,
                        message=msg,
                        type=INFOBOX,
                    ).execute()
                    return
                title = self.dialog_handler._resource_resolver.resolve_string("msg14")
                msg = self.dialog_handler._resource_resolver.resolve_string("msg15")
                # buttons: https://api.libreoffice.org/docs/idl/ref/namespacecom_1_1sun_1_1star_1_1awt_1_1MessageBoxButtons.html
                # results: https://api.libreoffice.org/docs/idl/ref/namespacecom_1_1sun_1_1star_1_1awt_1_1MessageBoxResults.html

                result = MessageDialog(
                    self.dialog_handler.ctx,
                    title=title,
                    message=msg,
                    buttons=3,  # Yes, NO
                    type=QUERYBOX,
                ).execute()
                if result == 2:
                    # yes has been clicked
                    if self._uninstall_items():
                        title = self.dialog_handler._resource_resolver.resolve_string("msg13")
                        msg = self.dialog_handler._resource_resolver.resolve_string("msg17")
                        _ = MessageDialog(
                            self.dialog_handler.ctx,
                            title=title,
                            message=msg,
                            type=INFOBOX,
                        ).execute()
                    else:
                        title = self.dialog_handler._resource_resolver.resolve_string("msg01")
                        msg = self.dialog_handler._resource_resolver.resolve_string("msg18")
                        _ = MessageDialog(
                            self.dialog_handler.ctx,
                            title=title,
                            message=msg,
                            type=ERRORBOX,
                        ).execute()
                    self._log.debug("ButtonListener.actionPerformed: UninstallItems")

        except Exception as err:
            self._log.error(f"ButtonListener.actionPerformed: {err}", exc_info=True)
            raise err

    def _uninstall_items(self) -> bool:
        try:
            from ...install.install_pkg import InstallPkg

            installer = InstallPkg(self.dialog_handler.ctx, flag_upgrade=False)
            success = True
            self._log.debug("_uninstall_items() uninstall_pkgs: %s", self.dialog_handler.uninstall_pkgs)
            for item in self.dialog_handler.uninstall_pkgs:
                success = success and installer.uninstall(item, remove_tracking_file=True)
            self.dialog_handler.uninstall_pkgs.clear()
            return success
        except Exception as e:
            self._log.error("_uninstall_items(): %s", e, exc_info=True)
        return False


class CheckBoxUninstallListener(unohelper.Base, XPropertyChangeListener):
    def __init__(self, handler: "OptionsDialogUninstallHandler") -> None:
        self._log = OxtLogger(log_name=self.__class__.__name__)
        self._log.debug("__init__")
        self.handler = handler
        self._config = BasicConfig()
        self._log.debug("__init__ done")

    def disposing(self, Source: Any) -> None:  # noqa: ANN401, N803
        pass

    def propertyChange(self, evt: PropertyChangeEvent) -> None:  # noqa: N802
        self._log.debug("propertyChange")
        try:
            # state (evn.NewValue) will be 1 for true and 0 for false
            src = cast("UnoControlCheckBoxModel", evt.Source)
            if src.Name in self._config.uninstall_gui_map:
                self._log.debug("propertyChange() checkbox %s found in uninstall_gui_map", src.Name)
                state = self.handler.state_to_bool(cast(int, (evt.NewValue)))
                self._log.debug("propertyChange() checkbox %s state: %s", src.Name, state)
                if state:
                    self.handler._uninstall_pkgs.add(self._config.uninstall_gui_map[src.Name])
                else:
                    self.handler._uninstall_pkgs.discard(self._config.uninstall_gui_map[src.Name])
            else:
                self._log.debug("propertyChange() checkbox %s not found in uninstall_gui_map", src.Name)
        except Exception as err:
            self._log.error("propertyChange: %s", err, exc_info=True)
            raise


class OptionsDialogUninstallHandler(unohelper.Base, XContainerWindowEventHandler):
    def __init__(self, ctx: Any) -> None:  # noqa: ANN401
        self._logger = OxtLogger(log_name=self.__class__.__name__)
        self._logger.debug("__init__")
        self.ctx = ctx
        self._uninstall_pkgs = set()
        self._config = BasicConfig()
        self._resource_resolver = ResourceResolver(self.ctx)
        self._window_name = "uninstall"  # uninstall.xdl file name
        self._settings = Settings()
        self._logger.debug("__init__ done")

    # region XContainerWindowEventHandler
    def callHandlerMethod(  # type: ignore  # noqa: N802
        self,
        xWindow: UnoControlDialog,  # noqa: N803
        EventObject: Any,  # noqa: ANN401, N803
        MethodName: str,  # noqa: ANN401, N803
    ) -> bool:  # type: ignore
        self._logger.debug("callHandlerMethod: %s", MethodName)
        if MethodName == "external_event":
            try:
                return self._handle_external_event(xWindow, EventObject)
            except Exception as e:
                print(e)
        return True

    def getSupportedMethodNames(self) -> Tuple[str, ...]:  # noqa: N802
        return ("external_event",)

    # endregion XContainerWindowEventHandler

    def _handle_external_event(self, window: UnoControlDialog, ev_name: str) -> bool:
        self._logger.debug("_handle_external_event: %s", ev_name)
        if ev_name == "ok":
            self._save_data(window)
        elif ev_name == "back":
            self._load_data(window, "back")
        elif ev_name == "initialize":
            self._load_data(window, "initialize")
        return True

    def _save_data(self, window: UnoControlDialog) -> None:
        pass

    def get_package_version(self) -> str:
        from importlib.metadata import PackageNotFoundError, version

        with contextlib.suppress(PackageNotFoundError):
            return version(self._config.package_name)
        return ""

    def _load_data(self, window: UnoControlDialog, ev_name: str) -> None:
        # sourcery skip: extract-method
        name = cast(str, window.getModel().Name)  # type: ignore
        self._logger.debug("_load_data name: %s", name)
        self._logger.debug("_load_data ev_name: %s", ev_name)
        if name != self._window_name:
            return
        try:
            if ev_name == "initialize":
                btn_listener = ButtonUninstallListener(self)
                btn_uninstall = cast("UnoControlButton", window.getControl("btnUninstall"))
                btn_uninstall.setActionCommand("UninstallItems")
                btn_uninstall.addActionListener(btn_listener)

                chk_listener = CheckBoxUninstallListener(self)
                for key in self._config.uninstall_gui_map:
                    chk = cast("UnoControlCheckBoxModel", window.getControl(key))
                    if chk is None:
                        self._logger.error("_load_data(): chk is None for control key %s", key)
                        continue
                    chk_model = chk.getModel()  # type: ignore
                    chk_model.addPropertyChangeListener("State", chk_listener)

            for control in window.Controls:  # type: ignore
                if not control.supportsService("com.sun.star.awt.UnoControlEdit"):
                    model = control.Model
                    model.Label = self._resource_resolver.resolve_string(model.Label)

        except Exception as err:
            self._logger.error("_load_data(): %s", err, exc_info=True)
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
    def uninstall_pkgs(self) -> Set[str]:
        return self._uninstall_pkgs
