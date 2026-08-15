"""Application orchestration layer."""

from __future__ import annotations

from pathlib import Path
from typing import Optional

from app.settings import AppSettings, load_settings, save_settings
from audio.device_manager import DeviceManager
from audio.engine import AudioEngine
from utils.logging import setup_logging


class LiveMixerApplication:
    """
    Top-level application controller.

    Bridges configuration, device management, and the audio engine.
    GUI will attach to this class in Phase 2.
    """

    def __init__(self, config_path: Optional[Path] = None) -> None:
        self.logger = setup_logging()
        self.config_path = config_path or Path("config/default_config.json")
        self.settings = self._load_or_default()
        self.device_manager = DeviceManager()
        self.engine = AudioEngine(
            config=self.settings.to_engine_config(),
            device_manager=self.device_manager,
        )
        self._apply_channel_settings()

    def _load_or_default(self) -> AppSettings:
        if self.config_path.exists():
            try:
                return load_settings(self.config_path)
            except (OSError, ValueError) as exc:
                self.logger.warning("Failed to load config: %s — using defaults", exc)
        return AppSettings()

    def _apply_channel_settings(self) -> None:
        if self.settings.channels:
            self.engine.mixer.apply_channel_states(self.settings.channels)

    def reconfigure_engine(self) -> None:
        """Rebuild engine from current settings (call before start)."""
        if self.engine.is_running:
            self.engine.stop()
        self.engine = AudioEngine(
            config=self.settings.to_engine_config(),
            device_manager=self.device_manager,
        )
        self._apply_channel_settings()

    def list_devices(self) -> None:
        """Print available audio devices."""
        inputs = self.device_manager.list_input_devices()
        outputs = self.device_manager.list_output_devices()

        self.logger.info("=== Input Devices ===")
        for dev in inputs:
            self.logger.info(
                "  [%d] %s (%s) — %d in, %d Hz",
                dev.index,
                dev.name,
                dev.hostapi,
                dev.max_input_channels,
                dev.default_sample_rate,
            )

        self.logger.info("=== Output Devices ===")
        for dev in outputs:
            self.logger.info(
                "  [%d] %s (%s) — %d out, %d Hz",
                dev.index,
                dev.name,
                dev.hostapi,
                dev.max_output_channels,
                dev.default_sample_rate,
            )

    def start(self) -> None:
        """Start the audio engine."""
        self.logger.info(
            "Starting engine: %d Hz, %d samples, %d channels",
            self.settings.sample_rate,
            self.settings.buffer_size,
            self.settings.num_channels,
        )
        self.engine.start()
        self.logger.info("Audio engine running")

    def stop(self) -> None:
        """Stop the audio engine."""
        self.engine.stop()
        self.logger.info("Audio engine stopped")

    def save_config(self, path: Optional[Path] = None) -> None:
        """Persist current settings."""
        self.settings.master_gain_db = self.engine.master.gain.gain_db
        self.settings.channels = self.engine.mixer.get_channel_states()
        save_settings(self.settings, path or self.config_path)
        self.logger.info("Configuration saved to %s", path or self.config_path)

    @property
    def is_running(self) -> bool:
        return self.engine.is_running
