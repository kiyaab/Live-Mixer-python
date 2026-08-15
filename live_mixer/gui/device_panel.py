"""Device selection and transport controls."""

from __future__ import annotations

from typing import Optional

from PySide6.QtCore import Signal
from PySide6.QtWidgets import (
    QComboBox,
    QGroupBox,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QSpinBox,
    QVBoxLayout,
    QWidget,
)

from audio.device_manager import AudioDeviceInfo, DeviceManager


class DevicePanel(QWidget):
    """Input/output device selection and start/stop controls."""

    start_requested = Signal()
    stop_requested = Signal()
    devices_changed = Signal(int, int, int, int)  # in_dev, out_dev, channels, buffer

    def __init__(self, device_manager: DeviceManager, parent=None) -> None:
        super().__init__(parent)
        self._device_manager = device_manager
        self._running = False

        layout = QVBoxLayout(self)
        group = QGroupBox("Audio Devices")
        group_layout = QHBoxLayout(group)

        group_layout.addWidget(QLabel("Input:"))
        self.input_combo = QComboBox()
        self.input_combo.setMinimumWidth(220)
        group_layout.addWidget(self.input_combo)

        group_layout.addWidget(QLabel("Output:"))
        self.output_combo = QComboBox()
        self.output_combo.setMinimumWidth(220)
        group_layout.addWidget(self.output_combo)

        group_layout.addWidget(QLabel("Channels:"))
        self.channels_spin = QSpinBox()
        self.channels_spin.setRange(1, 32)
        self.channels_spin.setValue(4)
        group_layout.addWidget(self.channels_spin)

        group_layout.addWidget(QLabel("Buffer:"))
        self.buffer_spin = QSpinBox()
        self.buffer_spin.setRange(64, 2048)
        self.buffer_spin.setSingleStep(64)
        self.buffer_spin.setValue(128)
        group_layout.addWidget(self.buffer_spin)

        self.start_btn = QPushButton("▶  START")
        self.start_btn.setObjectName("startButton")
        self.start_btn.clicked.connect(self._on_start)
        group_layout.addWidget(self.start_btn)

        self.stop_btn = QPushButton("■  STOP")
        self.stop_btn.setObjectName("stopButton")
        self.stop_btn.setEnabled(False)
        self.stop_btn.clicked.connect(self._on_stop)
        group_layout.addWidget(self.stop_btn)

        layout.addWidget(group)
        self._populate_devices()

    def _populate_devices(self) -> None:
        self.input_combo.clear()
        self.output_combo.clear()

        default_in = DeviceManager.get_default_input()
        default_out = DeviceManager.get_default_output()

        in_index = 0
        for i, dev in enumerate(self._device_manager.list_input_devices()):
            label = f"[{dev.index}] {dev.name} ({dev.max_input_channels}ch)"
            self.input_combo.addItem(label, dev.index)
            if dev.index == default_in:
                in_index = i
        self.input_combo.setCurrentIndex(in_index if self.input_combo.count() else -1)

        out_index = 0
        for i, dev in enumerate(self._device_manager.list_output_devices()):
            label = f"[{dev.index}] {dev.name} ({dev.max_output_channels}ch)"
            self.output_combo.addItem(label, dev.index)
            if dev.index == default_out:
                out_index = i
        self.output_combo.setCurrentIndex(out_index if self.output_combo.count() else -1)

    def _on_start(self) -> None:
        self.start_requested.emit()

    def _on_stop(self) -> None:
        self.stop_requested.emit()

    def set_running(self, running: bool) -> None:
        self._running = running
        self.start_btn.setEnabled(not running)
        self.stop_btn.setEnabled(running)
        self.input_combo.setEnabled(not running)
        self.output_combo.setEnabled(not running)
        self.channels_spin.setEnabled(not running)
        self.buffer_spin.setEnabled(not running)

    def get_selected_input(self) -> Optional[int]:
        return self.input_combo.currentData()

    def get_selected_output(self) -> Optional[int]:
        return self.output_combo.currentData()

    def get_channels(self) -> int:
        return self.channels_spin.value()

    def get_buffer_size(self) -> int:
        return self.buffer_spin.value()

    def set_channels(self, n: int) -> None:
        self.channels_spin.setValue(n)

    def set_buffer_size(self, n: int) -> None:
        self.buffer_spin.setValue(n)

    def select_devices(self, input_device: Optional[int], output_device: Optional[int]) -> None:
        if input_device is not None:
            for i in range(self.input_combo.count()):
                if self.input_combo.itemData(i) == input_device:
                    self.input_combo.setCurrentIndex(i)
                    break
        if output_device is not None:
            for i in range(self.output_combo.count()):
                if self.output_combo.itemData(i) == output_device:
                    self.output_combo.setCurrentIndex(i)
                    break
