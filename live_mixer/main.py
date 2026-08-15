#!/usr/bin/env python3
"""
Live Mixer — entry point.

Launches the GUI by default. Use --cli for headless mode or --list-devices
to enumerate hardware.
"""

from __future__ import annotations

import argparse
import signal
import sys
import time
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from app.application import LiveMixerApplication  # noqa: E402


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Live Mixer — Professional Real-Time Audio Console",
    )
    parser.add_argument(
        "--config",
        type=Path,
        default=PROJECT_ROOT / "config" / "default_config.json",
        help="Path to configuration JSON",
    )
    parser.add_argument(
        "--list-devices",
        action="store_true",
        help="List audio devices and exit",
    )
    parser.add_argument(
        "--cli",
        action="store_true",
        help="Run in headless CLI mode (no GUI)",
    )
    parser.add_argument(
        "--duration",
        type=float,
        default=0.0,
        help="CLI mode: run for N seconds (0 = until Ctrl+C)",
    )
    parser.add_argument(
        "--input-device",
        type=int,
        default=None,
        help="Input device index",
    )
    parser.add_argument(
        "--output-device",
        type=int,
        default=None,
        help="Output device index",
    )
    parser.add_argument(
        "--channels",
        type=int,
        default=None,
        help="Number of input channels",
    )
    parser.add_argument(
        "--buffer-size",
        type=int,
        default=None,
        help="Audio buffer size in samples",
    )
    return parser.parse_args()


def apply_cli_overrides(app: LiveMixerApplication, args: argparse.Namespace) -> None:
    if args.input_device is not None:
        app.settings.input_device = args.input_device
        app.device_manager.set_input_device(args.input_device)
    if args.output_device is not None:
        app.settings.output_device = args.output_device
        app.device_manager.set_output_device(args.output_device)
    if args.channels is not None:
        app.settings.num_channels = args.channels
    if args.buffer_size is not None:
        app.settings.buffer_size = args.buffer_size
    app.reconfigure_engine()


def run_cli(app: LiveMixerApplication, args: argparse.Namespace) -> int:
    stop_requested = False

    def handle_signal(_signum, _frame) -> None:
        nonlocal stop_requested
        stop_requested = True

    signal.signal(signal.SIGINT, handle_signal)
    if hasattr(signal, "SIGTERM"):
        signal.signal(signal.SIGTERM, handle_signal)

    try:
        app.start()
    except Exception as exc:
        app.logger.error("Failed to start: %s", exc)
        app.list_devices()
        return 1

    app.logger.info("Press Ctrl+C to stop")
    start_time = time.monotonic()

    try:
        while not stop_requested:
            if args.duration > 0 and (time.monotonic() - start_time) >= args.duration:
                break
            status = app.engine.get_status()
            meters = app.engine.get_meter_levels()
            app.logger.info(
                "CPU: %.1f%% | Latency: %.1f ms | Master peak: %.3f | Callbacks: %d",
                status.cpu_percent,
                status.estimated_latency_ms,
                meters["master"]["peak"],
                status.stream_stats.callback_count,
            )
            time.sleep(2.0)
    finally:
        app.stop()

    return 0


def main() -> int:
    args = parse_args()
    app = LiveMixerApplication(config_path=args.config)

    if args.list_devices:
        app.list_devices()
        return 0

    apply_cli_overrides(app, args)

    if args.cli:
        return run_cli(app, args)

    from gui import run_gui

    return run_gui(app)


if __name__ == "__main__":
    sys.exit(main())
