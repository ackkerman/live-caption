from CaptionWindow import CaptionWindow
from PyQt5 import QtWidgets, QtCore
import sys
import queue
import threading
import signal

from audio import audio_capture_worker
from recognizer import recognize_worker

# --- 音声キャプチャ設定 ---
SAMPLE_RATE = 48000
CHUNK_SIZE =4000
MONITOR_DEVICE_INDEX = 0

# --- 音声ストリームを入れるキュー ---
audio_queue = queue.Queue()

# --- 停止フラグとCtrl+Cカウント ---
stop_event = threading.Event()
ctrl_c_count = 0


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

if __name__ == "__main__":
    signal.signal(signal.SIGINT, handle_sigint)

    app = QtWidgets.QApplication(sys.argv)
    window = CaptionWindow()

    # 音声キャプチャ用スレッド
    threading.Thread(
        target=audio_capture_worker,
        args=(audio_queue, stop_event, MONITOR_DEVICE_INDEX, SAMPLE_RATE, CHUNK_SIZE),
        daemon=True,
    ).start()

    # 音声認識用スレッド
    threading.Thread(
        target=recognize_worker,
        args=(window, audio_queue, stop_event),
        kwargs={"sample_rate": SAMPLE_RATE},
        daemon=True,
    ).start()

    timer = QtCore.QTimer()
    timer.timeout.connect(periodic_check)
    timer.start(100)  # 毎100ミリ秒

    sys.exit(app.exec_())
