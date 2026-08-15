"""Launch the Live Mixer GUI."""

from __future__ import annotations

import sys

from PySide6.QtWidgets import QApplication

from app.application import LiveMixerApplication
from gui.main_window import MainWindow


def run_gui(app: LiveMixerApplication) -> int:
    """Create Qt application and show main window."""
    qt_app = QApplication(sys.argv)
    qt_app.setApplicationName("Live Mixer")
    qt_app.setOrganizationName("LiveMixer")

    window = MainWindow(app)
    window.show()

    return qt_app.exec()
