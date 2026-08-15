"""Audio device discovery and configuration."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Optional

import sounddevice as sd


@dataclass(frozen=True)
class AudioDeviceInfo:
    """Summary of an audio device."""

    index: int
    name: str
    max_input_channels: int
    max_output_channels: int
    default_sample_rate: float
    hostapi: str
    is_input: bool
    is_output: bool


class DeviceManager:
    """
    Enumerates and selects audio input/output devices.

    Separated from the real-time engine for clean dependency injection.
    """

    def __init__(self) -> None:
        self._input_device: Optional[int] = None
        self._output_device: Optional[int] = None

    @staticmethod
    def list_devices() -> list[AudioDeviceInfo]:
        """Return all available audio devices."""
        devices: list[AudioDeviceInfo] = []
        hostapis = sd.query_hostapis()
        for index, dev in enumerate(sd.query_devices()):
            hostapi_name = hostapis[dev["hostapi"]]["name"]
            max_in = int(dev["max_input_channels"])
            max_out = int(dev["max_output_channels"])
            devices.append(
                AudioDeviceInfo(
                    index=index,
                    name=dev["name"],
                    max_input_channels=max_in,
                    max_output_channels=max_out,
                    default_sample_rate=float(dev["default_samplerate"]),
                    hostapi=hostapi_name,
                    is_input=max_in > 0,
                    is_output=max_out > 0,
                )
            )
        return devices

    @staticmethod
    def list_input_devices() -> list[AudioDeviceInfo]:
        return [d for d in DeviceManager.list_devices() if d.is_input]

    @staticmethod
    def list_output_devices() -> list[AudioDeviceInfo]:
        return [d for d in DeviceManager.list_devices() if d.is_output]

    @staticmethod
    def get_default_input() -> Optional[int]:
        try:
            return sd.default.device[0]
        except (TypeError, IndexError, sd.PortAudioError):
            return None

    @staticmethod
    def get_default_output() -> Optional[int]:
        try:
            return sd.default.device[1]
        except (TypeError, IndexError, sd.PortAudioError):
            return None

    @property
    def input_device(self) -> Optional[int]:
        return self._input_device

    @property
    def output_device(self) -> Optional[int]:
        return self._output_device

    def set_input_device(self, device_index: Optional[int]) -> None:
        self._validate_device(device_index, require_input=True)
        self._input_device = device_index

    def set_output_device(self, device_index: Optional[int]) -> None:
        self._validate_device(device_index, require_output=True)
        self._output_device = device_index

    def resolve_devices(
        self,
        input_device: Optional[int] = None,
        output_device: Optional[int] = None,
    ) -> tuple[int, int]:
        """Resolve device indices, falling back to system defaults."""
        in_dev = input_device if input_device is not None else self._input_device
        out_dev = output_device if output_device is not None else self._output_device

        if in_dev is None:
            in_dev = self.get_default_input()
        if out_dev is None:
            out_dev = self.get_default_output()

        if in_dev is None or out_dev is None:
            raise RuntimeError("No audio input/output device available")

        self._validate_device(in_dev, require_input=True)
        self._validate_device(out_dev, require_output=True)
        return in_dev, out_dev

    @staticmethod
    def get_device_info(device_index: int) -> AudioDeviceInfo:
        dev = sd.query_devices(device_index)
        hostapis = sd.query_hostapis()
        return AudioDeviceInfo(
            index=device_index,
            name=dev["name"],
            max_input_channels=int(dev["max_input_channels"]),
            max_output_channels=int(dev["max_output_channels"]),
            default_sample_rate=float(dev["default_samplerate"]),
            hostapi=hostapis[dev["hostapi"]]["name"],
            is_input=int(dev["max_input_channels"]) > 0,
            is_output=int(dev["max_output_channels"]) > 0,
        )

    @staticmethod
    def _validate_device(
        device_index: Optional[int],
        require_input: bool = False,
        require_output: bool = False,
    ) -> None:
        if device_index is None:
            return
        info = DeviceManager.get_device_info(device_index)
        if require_input and not info.is_input:
            raise ValueError(f"Device {device_index} ({info.name}) has no inputs")
        if require_output and not info.is_output:
            raise ValueError(f"Device {device_index} ({info.name}) has no outputs")

    @staticmethod
    def check_sample_rate(device_index: int, sample_rate: int, channels: int) -> bool:
        """Return True if the device supports the given sample rate."""
        try:
            sd.check_input_settings(
                device=device_index,
                samplerate=sample_rate,
                channels=channels,
            )
            return True
        except sd.PortAudioError:
            return False
