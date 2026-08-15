# 🎚️ LIVE MIXER

### A Modern Digital Audio Mixing Console Built with Python

<p align="center">
  <strong>Mix. Control. Create.</strong>
  <br>
  A powerful, modular and low-latency audio mixer designed for real-time sound control.
</p>

<p align="center">

![Python](https://img.shields.io/badge/Python-3.11+-3776AB?style=flat-square\&logo=python\&logoColor=white)
![Audio](https://img.shields.io/badge/Real--Time-Audio-8A2BE2?style=flat-square)
![PortAudio](https://img.shields.io/badge/PortAudio-Supported-black?style=flat-square)
![License](https://img.shields.io/badge/License-MIT-green?style=flat-square)

</p>

---

## 🎧 About

**Live Mixer** is a professional-inspired digital audio mixing application built with **Python**.

It brings the essential experience of a physical audio mixer into a modern software environment.

Control multiple audio channels, adjust levels, manage your master output, monitor audio levels, and build a foundation for advanced audio production.

> **Designed for simplicity. Engineered for real-time performance.**

---

# ✨ Features

### 🎛️ Multi-Channel Mixing

Manage multiple audio channels from one clean mixing environment.

* Individual channel gain
* Channel faders
* Pan control
* Mute
* Solo
* Real-time levels

### 🎚️ Master Control

Take complete control of your final output with a dedicated master channel.

### 📊 Live Audio Meters

Monitor your sound in real time using:

* Peak levels
* RMS levels
* Channel monitoring
* Master output monitoring

### ⚡ Low-Latency Audio

Built around a real-time audio pipeline using **PortAudio** and **sounddevice** for responsive input and output.

### 🔊 Device Management

Discover and select available audio input and output devices directly from the application.

### 💾 Configuration

Store mixer settings using a simple JSON configuration system.

### 🧩 Modular Architecture

The system is designed to grow.

Future audio effects, recording, presets, routing, and advanced DSP can be added without rebuilding the entire application.

---

# 🖥️ Experience

Live Mixer is designed around the familiar workflow of a physical mixing console.

```text
┌─────────────────────────────────────────────────────┐
│                    LIVE MIXER                       │
├────────┬────────┬────────┬────────┬─────────────────┤
│  CH 01 │  CH 02 │  CH 03 │  CH 04 │     MASTER     │
│        │        │        │        │                 │
│   ▮    │   ▮    │   ▮    │   ▮    │      ▮          │
│   ▮    │   ▮    │   ▮    │   ▮    │      ▮          │
│   ▮    │   ▮    │   ▮    │   ▮    │      ▮          │
│        │        │        │        │                 │
│  MUTE  │  MUTE  │  MUTE  │  MUTE  │                 │
│  SOLO  │  SOLO  │  SOLO  │  SOLO  │                 │
│        │        │        │        │                 │
│   ║    │   ║    │   ║    │   ║    │       ║         │
│   ║    │   ║    │   ║    │   ║    │       ║         │
│   ▼    │   ▼    │   ▼    │   ▼    │       ▼         │
└────────┴────────┴────────┴────────┴─────────────────┘
```

The goal is simple:

**Everything you need to control your sound — in one place.**

---

# 🏗️ How It Works

```text
🎤 Audio Input
      │
      ▼
🔊 Audio Engine
      │
      ▼
🎚️ Channel Processing
      │
      ├── Gain
      ├── Pan
      ├── Mute
      └── Solo
      │
      ▼
🎛️ Mixer Bus
      │
      ▼
🎚️ Master Control
      │
      ▼
🔊 Stereo Output
```

The interface communicates with the audio engine through controlled parameters, keeping the real-time audio pipeline separate from the user interface.

---

# 🧠 Built for Real-Time Audio

Live Mixer follows an important rule:

> **The audio processing thread should stay focused on audio.**

The real-time callback avoids unnecessary operations such as:

```text
❌ File operations
❌ Network requests
❌ GUI updates
❌ Printing
❌ Blocking operations
❌ Unnecessary memory allocation
```

This helps keep the audio pipeline responsive and stable.

---

# 📁 Project Structure

```text
Live-Mixer-python/
│
├── main.py
│
├── app/
│   └── Application logic
│
├── audio/
│   ├── engine.py
│   ├── mixer.py
│   ├── channel.py
│   └── dsp/
│
├── gui/
│   └── Mixer interface
│
├── recording/
│   └── Recording system
│
├── presets/
│   └── Mixer presets
│
├── config/
│   └── Configuration
│
├── tests/
│   └── Automated tests
│
├── requirements.txt
└── README.md
```

---

# 🚀 Getting Started

## 1. Clone

```bash
git clone https://github.com/kiyaab/Live-Mixer-python.git
cd Live-Mixer-python
```

## 2. Create Virtual Environment

### Windows

```bash
python -m venv .venv
.venv\Scripts\activate
```

### Linux / macOS

```bash
python3 -m venv .venv
source .venv/bin/activate
```

## 3. Install Dependencies

```bash
pip install -r requirements.txt
```

## 4. Start Live Mixer

```bash
python main.py
```

---

# 🧪 CLI Mode

You can also run the audio engine without the graphical interface:

```bash
python main.py --cli
```

---

# 🧪 Run Tests

```bash
python -m pytest tests/ -v
```

---

# ⚙️ Default Configuration

| Setting     |       Value |
| ----------- | ----------: |
| Sample Rate |   48,000 Hz |
| Buffer Size | 128 samples |
| Channels    |           4 |
| Format      |     Float32 |
| Output      |      Stereo |

---

# 🛣️ Roadmap

### ✅ Phase 1 — Core Engine

* [x] Audio device discovery
* [x] Input/output selection
* [x] Duplex audio
* [x] Multi-channel mixing
* [x] Channel gain
* [x] Master gain
* [x] Peak metering
* [x] RMS metering
* [x] JSON configuration
* [x] Thread-safe controls

### 🚧 Phase 2 — Mixer UI

* [ ] Professional mixer interface
* [ ] Animated level meters
* [ ] Advanced faders
* [ ] Improved device management
* [ ] Keyboard controls
* [ ] Custom mixer layouts

### 🔮 Phase 3 — Audio Effects

* [ ] Equalizer
* [ ] Compressor
* [ ] Limiter
* [ ] Noise Gate
* [ ] Reverb
* [ ] Delay
* [ ] Effects routing

### 🎙️ Phase 4 — Recording

* [ ] Audio recording
* [ ] Multi-track recording
* [ ] WAV export
* [ ] Recording sessions
* [ ] Input monitoring

### 🎛️ Phase 5 — Professional Workflow

* [ ] Mixer presets
* [ ] Scene management
* [ ] Session management
* [ ] Automation
* [ ] Advanced routing
* [ ] Channel templates

---

# 🎯 Vision

Live Mixer is being built with a bigger goal in mind:

**Create a powerful, accessible and extensible digital mixing platform.**

From simple audio mixing to live performance, recording, studio production and advanced DSP — the architecture is designed to evolve.

```text
                 LIVE MIXER
                     │
       ┌─────────────┼─────────────┐
       ▼             ▼             ▼
    🎤 LIVE       🎙️ RECORD      🎚️ STUDIO
       │             │             │
       └─────────────┼─────────────┘
                     ▼
               🔊 AUDIO ENGINE
                     │
                     ▼
              🎛️ PROFESSIONAL
                 MIXING
```

---

# 👨‍💻 Created By

## Endegena Abebe

**Software Developer • Full-Stack Engineer • Creator**

Live Mixer is designed and developed by **Endegena Abebe**, combining software engineering with an interest in real-time audio technology.

> **Built with Python. Designed with purpose. Created by Endegena Abebe.**

---

# 🤝 Contributing

Contributions and ideas are welcome.

You can contribute by:

* Reporting bugs
* Suggesting features
* Improving the audio engine
* Improving the interface
* Adding DSP modules
* Improving documentation
* Submitting pull requests

---

# 📄 License

This project is released under the **MIT License**.

See [`LICENSE`](LICENSE) for more information.

---

<div align="center">

### 🎚️ LIVE MIXER

**Mix • Control • Create**

Built with Python
Created by **Endegena Abebe**

⭐ Star the repository if you like the project.

</div>
