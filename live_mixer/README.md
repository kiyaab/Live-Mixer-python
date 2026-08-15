# Live Mixer

Professional, modular, low-latency live digital audio mixing console in Python.

## Phase 1 Status

Phase 1 implements the core audio pipeline:

- Audio device discovery and selection
- Duplex input/output via PortAudio (sounddevice)
- Multi-channel mixer with per-channel input gain
- Master gain
- Preallocated buffers (real-time safe)
- Peak/RMS metering
- Thread-safe parameter control
- JSON configuration

## Requirements

- Python 3.11+
- PortAudio (installed automatically with sounddevice on most platforms)

## Installation

```bash
cd live_mixer
pip install -r requirements.txt
```

## Quick Start

### GUI (recommended)

```bash
python main.py
```

This opens the mixing console window where you can:
- Select input/output devices
- Click **START** to begin audio
- Adjust faders, pan, gain, mute, and solo per channel
- Control the master fader
- Watch live level meters

### CLI mode

```bash
python main.py --cli
```

## Architecture

```
Physical Inputs → Audio I/O (sounddevice) → Real-Time Engine
                                                    │
                                    ┌───────────────┼───────────────┐
                                    ▼               ▼               ▼
                                  CH1..N         Routing         Master
                                    │               │               │
                                    └───────────────┴───────────────┘
                                                    │
                                              Stereo Output
```

The GUI layer (Phase 2) communicates with the engine only through parameter
changes — it never touches audio buffers directly.

## Real-Time Rules

The audio callback never performs:

- File I/O, logging, or printing
- Memory allocations
- Blocking locks or network operations
- GUI updates

All buffers are preallocated. Parameter changes are smoothed to prevent clicks.

## Running Tests

```bash
python -m pytest tests/ -v
```

## Project Structure

```
live_mixer/
├── main.py                 # CLI entry point
├── app/                    # Application layer
├── audio/                  # Real-time engine + DSP
│   ├── engine.py           # Central audio engine
│   ├── mixer.py            # Channel summing
│   ├── channel.py          # Channel strip
│   └── dsp/                # DSP modules
├── gui/                    # PySide6 GUI (Phase 2)
├── recording/              # Recording subsystem (Phase 5)
├── presets/                # Scene/preset management (Phase 5)
├── config/                 # JSON configuration
└── tests/                  # Automated tests
```

## Default Settings

| Parameter    | Default   |
|-------------|-----------|
| Sample rate | 48,000 Hz |
| Buffer size | 128 samples |
| Channels    | 4         |
| Format      | float32   |

## License

MIT — see [LICENSE](LICENSE).
