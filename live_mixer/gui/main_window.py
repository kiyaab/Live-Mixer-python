"""Main application window."""

from __future__ import annotations

from PySide6.QtCore import QTimer
from PySide6.QtWidgets import (
    QHBoxLayout,
    QLabel,
    QMainWindow,
    QMessageBox,
    QStatusBar,
    QVBoxLayout,
    QWidget,
)

from app.application import LiveMixerApplication
from gui.device_panel import DevicePanel
from gui.mixer_view import MixerView
from gui.styles import DARK_STYLE


class MainWindow(QMainWindow):
    """Live Mixer main window."""

    METER_INTERVAL_MS = 33  # ~30 fps

    def __init__(self, app: LiveMixerApplication) -> None:
        super().__init__()
        self._app = app
        self.setWindowTitle("Live Mixer")
        self.setMinimumSize(900, 520)
        self.resize(1100, 600)
        self.setStyleSheet(DARK_STYLE)

        central = QWidget()
        self.setCentralWidget(central)
        layout = QVBoxLayout(central)
        layout.setSpacing(8)
        layout.setContentsMargins(12, 12, 12, 12)

        header = QHBoxLayout()
        title = QLabel("LIVE MIXER")
        title.setObjectName("titleLabel")
        header.addWidget(title)
        header.addStretch()

        self.status_info = QLabel("Stopped")
        self.status_info.setObjectName("statusLabel")
        header.addWidget(self.status_info)
        layout.addLayout(header)

        self.device_panel = DevicePanel(self._app.device_manager)
        self.device_panel.set_channels(self._app.settings.num_channels)
        self.device_panel.set_buffer_size(self._app.settings.buffer_size)
        self.device_panel.select_devices(
            self._app.settings.input_device,
            self._app.settings.output_device,
        )
        self.device_panel.start_requested.connect(self._on_start)
        self.device_panel.stop_requested.connect(self._on_stop)
        layout.addWidget(self.device_panel)

        self.mixer_view = MixerView(num_channels=self._app.settings.num_channels)
        self.mixer_view.connect_engine(self._app.engine)
        if self._app.settings.channels:
            self.mixer_view.load_channel_states(self._app.settings.channels)
        self.mixer_view.load_master_gain(self._app.settings.master_gain_db)
        layout.addWidget(self.mixer_view, stretch=1)

        status = QStatusBar()
        self.setStatusBar(status)
        self._cpu_label = QLabel("CPU: —")
        self._latency_label = QLabel("Latency: —")
        self._rate_label = QLabel("48 kHz")
        self._buffer_label = QLabel("128 samples")
        status.addWidget(self._cpu_label)
        status.addWidget(self._latency_label)
        status.addWidget(self._rate_label)
        status.addWidget(self._buffer_label)

        self._meter_timer = QTimer(self)
        self._meter_timer.timeout.connect(self._update_meters)
        self._meter_timer.start(self.METER_INTERVAL_MS)

    def _on_start(self) -> None:
        in_dev = self.device_panel.get_selected_input()
        out_dev = self.device_panel.get_selected_output()
        channels = self.device_panel.get_channels()
        buffer_size = self.device_panel.get_buffer_size()

        self._app.settings.input_device = in_dev
        self._app.settings.output_device = out_dev
        self._app.settings.num_channels = channels
        self._app.settings.buffer_size = buffer_size

        if channels != len(self.mixer_view.channel_strips):
            self._rebuild_mixer_view(channels)

        self._app.reconfigure_engine()
        self.mixer_view.connect_engine(self._app.engine)

        try:
            self._app.start()
        except Exception as exc:
            QMessageBox.critical(
                self,
                "Audio Error",
                f"Failed to start audio engine:\n\n{exc}\n\n"
                "Try different devices or fewer channels.",
            )
            return

        self.device_panel.set_running(True)
        self.status_info.setText("● RUNNING")
        self.status_info.setStyleSheet("color: #2ecc71; font-weight: bold;")
        self._update_status_labels()

    def _on_stop(self) -> None:
        self._app.stop()
        self.device_panel.set_running(False)
        self.status_info.setText("Stopped")
        self.status_info.setStyleSheet("color: #888;")

    def _rebuild_mixer_view(self, num_channels: int) -> None:
        layout = self.centralWidget().layout()
        old_view = self.mixer_view
        layout.removeWidget(old_view)
        old_view.deleteLater()

        self.mixer_view = MixerView(num_channels=num_channels)
        self.mixer_view.connect_engine(self._app.engine)
        if self._app.settings.channels:
            self.mixer_view.load_channel_states(self._app.settings.channels)
        self.mixer_view.load_master_gain(self._app.settings.master_gain_db)
        layout.addWidget(self.mixer_view, stretch=1)

    def _update_meters(self) -> None:
        if not self._app.is_running:
            return
        meters = self._app.engine.get_meter_levels()
        self.mixer_view.update_meters(meters)
        self._update_status_labels()

    def _update_status_labels(self) -> None:
        status = self._app.engine.get_status()
        self._cpu_label.setText(f"CPU: {status.cpu_percent:.1f}%")
        self._latency_label.setText(f"Latency: {status.estimated_latency_ms:.1f} ms")
        self._rate_label.setText(f"{status.sample_rate // 1000} kHz")
        self._buffer_label.setText(f"{status.block_size} samples")

    def closeEvent(self, event) -> None:
        if self._app.is_running:
            self._app.stop()
        self._app.save_config()
        event.accept()
