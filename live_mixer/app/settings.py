"""Application settings loaded from JSON configuration."""

from __future__ import annotations

import json
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Optional

from audio.channel import ChannelState
from audio.engine import EngineConfig


@dataclass
class AppSettings:
    """Application-wide settings."""

    sample_rate: int = 48000
    buffer_size: int = 128
    num_channels: int = 4
    input_device: Optional[int] = None
    output_device: Optional[int] = None
    master_gain_db: float = 0.0
    channels: list[ChannelState] = field(default_factory=list)

    def to_engine_config(self) -> EngineConfig:
        return EngineConfig(
            sample_rate=self.sample_rate,
            block_size=self.buffer_size,
            num_channels=self.num_channels,
            input_device=self.input_device,
            output_device=self.output_device,
            master_gain_db=self.master_gain_db,
        )

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> AppSettings:
        channels = [
            ChannelState(
                name=ch.get("name", f"CH{i + 1}"),
                input_gain_db=ch.get("gain_db", 0.0),
                fader_db=ch.get("fader_db", 0.0),
                pan=ch.get("pan", 0.0),
                mute=ch.get("mute", False),
                solo=ch.get("solo", False),
                phase_invert=ch.get("phase_invert", False),
            )
            for i, ch in enumerate(data.get("channels", []))
        ]
        return cls(
            sample_rate=data.get("sample_rate", 48000),
            buffer_size=data.get("buffer_size", 128),
            num_channels=data.get("num_channels", len(channels) or 4),
            input_device=data.get("input_device"),
            output_device=data.get("output_device"),
            master_gain_db=data.get("master_gain_db", 0.0),
            channels=channels,
        )

    def to_dict(self) -> dict[str, Any]:
        return {
            "sample_rate": self.sample_rate,
            "buffer_size": self.buffer_size,
            "num_channels": self.num_channels,
            "input_device": self.input_device,
            "output_device": self.output_device,
            "master_gain_db": self.master_gain_db,
            "channels": [
                {
                    "name": ch.name,
                    "gain_db": ch.input_gain_db,
                    "fader_db": ch.fader_db,
                    "pan": ch.pan,
                    "mute": ch.mute,
                    "solo": ch.solo,
                    "phase_invert": ch.phase_invert,
                }
                for ch in self.channels
            ],
        }


def load_settings(path: Path) -> AppSettings:
    """Load settings from a JSON file."""
    with path.open("r", encoding="utf-8") as f:
        data = json.load(f)
    return AppSettings.from_dict(data)


def save_settings(settings: AppSettings, path: Path) -> None:
    """Save settings to a JSON file."""
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as f:
        json.dump(settings.to_dict(), f, indent=2)
