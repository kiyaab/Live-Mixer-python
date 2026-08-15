"""Dark mixing-console theme."""

DARK_STYLE = """
QMainWindow, QWidget {
    background-color: #1a1a1e;
    color: #e0e0e0;
    font-family: "Segoe UI", "Ubuntu", sans-serif;
    font-size: 12px;
}

QLabel#titleLabel {
    font-size: 18px;
    font-weight: bold;
    color: #ffffff;
    letter-spacing: 2px;
}

QLabel#statusLabel {
    color: #888;
    font-size: 11px;
}

QGroupBox {
    border: 1px solid #333;
    border-radius: 4px;
    margin-top: 8px;
    padding-top: 12px;
    font-weight: bold;
    color: #aaa;
}

QGroupBox::title {
    subcontrol-origin: margin;
    left: 8px;
    padding: 0 4px;
}

QSlider::groove:vertical {
    background: #2a2a30;
    width: 8px;
    border-radius: 4px;
}

QSlider::handle:vertical {
    background: #4a9eff;
    height: 18px;
    margin: 0 -5px;
    border-radius: 4px;
}

QSlider::groove:horizontal {
    background: #2a2a30;
    height: 6px;
    border-radius: 3px;
}

QSlider::handle:horizontal {
    background: #4a9eff;
    width: 14px;
    margin: -5px 0;
    border-radius: 4px;
}

QPushButton {
    background-color: #2a2a30;
    border: 1px solid #444;
    border-radius: 4px;
    padding: 6px 12px;
    min-height: 24px;
}

QPushButton:hover {
    background-color: #353540;
    border-color: #555;
}

QPushButton:pressed {
    background-color: #4a9eff;
    color: #000;
}

QPushButton:checked {
    background-color: #c0392b;
    border-color: #e74c3c;
    color: #fff;
}

QPushButton#soloButton:checked {
    background-color: #f39c12;
    border-color: #e67e22;
    color: #000;
}

QPushButton#startButton {
    background-color: #27ae60;
    border-color: #2ecc71;
    color: #fff;
    font-weight: bold;
}

QPushButton#startButton:hover {
    background-color: #2ecc71;
}

QPushButton#stopButton {
    background-color: #c0392b;
    border-color: #e74c3c;
    color: #fff;
    font-weight: bold;
}

QComboBox {
    background-color: #2a2a30;
    border: 1px solid #444;
    border-radius: 4px;
    padding: 4px 8px;
    min-height: 24px;
}

QComboBox::drop-down {
    border: none;
    width: 20px;
}

QComboBox QAbstractItemView {
    background-color: #2a2a30;
    border: 1px solid #444;
    selection-background-color: #4a9eff;
}

QScrollArea {
    border: none;
    background-color: #1a1a1e;
}

QDoubleSpinBox, QSpinBox {
    background-color: #2a2a30;
    border: 1px solid #444;
    border-radius: 4px;
    padding: 2px 4px;
}
"""

# Meter colors
METER_GREEN = "#27ae60"
METER_YELLOW = "#f1c40f"
METER_RED = "#e74c3c"
METER_BG = "#111114"
METER_CLIP = "#ff0000"
