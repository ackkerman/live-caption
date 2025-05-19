import sys
import signal
import queue
import threading
import argparse

try:
    from PyQt5 import QtWidgets, QtCore
    from CaptionWindow import CaptionWindow
except Exception:  # pragma: no cover - optional for tests
    QtWidgets = None
    QtCore = None
    CaptionWindow = None

from audio import audio_capture_worker, microphone_capture_worker
from recognizer import recognize_worker

# --- 音声キャプチャ設定 ---
SAMPLE_RATE = 48000
CHUNK_SIZE =4000
MONITOR_DEVICE_INDEX = 0
MIC_DEVICE_INDEX = 1

# --- 音声ストリームを入れるキュー ---
audio_queue = queue.Queue()

# --- 停止フラグとCtrl+Cカウント ---
stop_event = threading.Event()
ctrl_c_count = 0
mic_enabled_event = threading.Event()


def handle_sigint(signum, frame):
    """Ctrl+Cを受けたときの処理"""
    global ctrl_c_count
    ctrl_c_count += 1
    if ctrl_c_count == 1:
        print("\n[INFO] Ctrl+C検知: もう一度押すと終了します！")
    elif ctrl_c_count >= 2:
        print("\n[INFO] 強制終了します！")
        stop_event.set()
        QtWidgets.QApplication.quit()

def periodic_check():
    """定期的に停止フラグをチェックする"""
    if stop_event.is_set():
        print("[INFO] 停止イベント検知、アプリケーション終了")
        QtWidgets.QApplication.quit()


def run_app(device_index=MONITOR_DEVICE_INDEX, sample_rate=SAMPLE_RATE, chunk_size=CHUNK_SIZE, mic_device_index=MIC_DEVICE_INDEX):
    """Start the caption application."""
    if QtWidgets is None or QtCore is None or CaptionWindow is None:
        raise ImportError("PyQt5 is required to run the application")
    signal.signal(signal.SIGINT, handle_sigint)

    app = QtWidgets.QApplication(sys.argv)
    window = CaptionWindow(mic_enabled_event)

    threading.Thread(
        target=audio_capture_worker,
        args=(audio_queue, stop_event, device_index, sample_rate, chunk_size),
        daemon=True,
    ).start()

    threading.Thread(
        target=microphone_capture_worker,
        args=(audio_queue, stop_event, mic_enabled_event, mic_device_index, sample_rate, chunk_size),
        daemon=True,
    ).start()

    threading.Thread(
        target=recognize_worker,
        args=(window, audio_queue, stop_event),
        kwargs={"sample_rate": sample_rate},
        daemon=True,
    ).start()

    timer = QtCore.QTimer()
    timer.timeout.connect(periodic_check)
    timer.start(100)

    sys.exit(app.exec_())


def main(argv=None):
    """CLI entry point"""
    parser = argparse.ArgumentParser(description="Live Caption app")
    parser.add_argument("--device", type=int, default=MONITOR_DEVICE_INDEX, help="Monitor device index")
    parser.add_argument("--mic-device", type=int, default=MIC_DEVICE_INDEX, help="Microphone device index")
    parser.add_argument("--sample-rate", type=int, default=SAMPLE_RATE, help="Audio sample rate")
    parser.add_argument("--chunk-size", type=int, default=CHUNK_SIZE, help="Capture chunk size")
    args = parser.parse_args(argv)
    run_app(args.device, args.sample_rate, args.chunk_size, args.mic_device)

if __name__ == "__main__":
    main()
