# Live Caption App for Linux

[English](./README.md) / [日本語](./README_JA.md)

This application recognizes all audio played on your PC in real time  
and displays subtitles (captions) on the screen.

It is inspired by the "Live Caption" feature available on Android.

https://github.com/user-attachments/assets/5fbaa334-c55b-49f7-b66b-9903ab4a828f


## ✨ Features

- Capture all audio output from the system (videos, music, calls, etc.)
- Real-time subtitles using the Vosk speech recognition engine
- Supports partial recognition for ultra-low latency caption updates
- Always-on-top caption window with customizable positioning
- Safe termination by pressing Ctrl+C twice


## 🖥 System Requirements

- Linux (**PipeWire or PulseAudio** environment)
- Python 3.10 or higher recommended
- Monitor source available (e.g., `alsa_output.pci-0000_00_1f.3.analog-stereo.monitor`)


## 🛠 Installation

1. Clone this repository.

2. Install the required packages.

    ```bash
    poetry install
    ```

3. Check the monitor source device index.

    ```bash
    poetry run python scripts/monitor_device.py
    ```

4. Set the correct `MONITOR_DEVICE_INDEX` in `main.py`.


## 🚀 How to Run

```bash
poetry run python main.py
```

- A caption window will appear pinned to the top of your screen.
- Subtitles will update in real time according to the audio output.


## 🛑 How to Exit

- Press **Ctrl+C twice** to safely terminate the application.
- Resources will be properly released without freezing.

## 🧪 Running Tests

```bash
poetry run python -m unittest discover -v
```

The tests use simple mocks and do not require audio devices or Vosk models.


## ⚙️ Planned Future Enhancements

- [ ] **Toggle device microphone**
- [ ] **Customizable caption styles** (font, color, size, transparency, etc.)
- [x] **Text wrapping and multi-line caption support**
- [ ] **Switchable speech recognition engines (e.g., Whisper.cpp support)**
- [ ] **Multilingual captions (automatic language switching and translation)**
- [ ] **GUI tool for adjusting caption window position and size**
- [ ] **Click-through (mouse pass-through) mode for the caption window**
- [x] **Fade-out and auto-hide options when audio is not detected**


## 🛡 Notes

- Recognition accuracy depends on the Vosk model used.  
  For higher accuracy, consider using larger models or switching to different engines.
- This application works entirely locally; no audio data is sent externally.

## 📜 License

MIT License
