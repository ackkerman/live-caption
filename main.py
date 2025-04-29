from CaptionWindow import CaptionWindow
from PyQt5 import QtWidgets, QtCore
import sys
import sounddevice as sd
import queue
import threading
import signal
from vosk import Model, KaldiRecognizer
import json

# --- 音声キャプチャ設定 ---
SAMPLE_RATE = 48000
CHUNK_SIZE =4000
MONITOR_DEVICE_INDEX = 0

# --- 音声ストリームを入れるキュー ---
audio_queue = queue.Queue()

# --- 停止フラグとCtrl+Cカウント ---
stop_event = threading.Event()
ctrl_c_count = 0

def audio_capture_worker():
    """sounddeviceでモニター音声をキャプチャ"""
    def callback(indata, frames, time, status):
        if status:
            print(f"Audio Callback Status: {status}", file=sys.stderr)
        audio_queue.put(indata.copy())

    stream = sd.InputStream(
        device=MONITOR_DEVICE_INDEX,
        samplerate=SAMPLE_RATE,
        channels=1,
        dtype='int16',
        blocksize=CHUNK_SIZE,
        callback=callback,
    )

    with stream:
        threading.Event().wait()

def recognize_worker(window: CaptionWindow):
    """Voskで音声認識してキャプション更新（Partial対応版）"""
    model = Model(lang="en-us")  # or "ja" model for Japanese
    rec = KaldiRecognizer(model, SAMPLE_RATE)

    final_text = ""

    while not stop_event.is_set():
        try:
            indata = audio_queue.get(timeout=0.1)  # timeout付きにして停止チェック
        except queue.Empty:
            continue
        bytes_data = indata.tobytes()

        if rec.AcceptWaveform(bytes_data):
            result = rec.Result()
            text = json.loads(result).get("text", "")
            if text:
                print(f"[FINAL] {text}")
                final_text = text
                window.update_caption(final_text)
        else:
            partial_result = rec.PartialResult()
            partial_text = json.loads(partial_result).get("partial", "")
            if partial_text:
                print(f"[PARTIAL] {partial_text}")
                window.update_caption(f"{final_text} {partial_text}")


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
    threading.Thread(target=audio_capture_worker, daemon=True).start()

    # 音声認識用スレッド
    threading.Thread(target=recognize_worker, args=(window,), daemon=True).start()

    timer = QtCore.QTimer()
    timer.timeout.connect(periodic_check)
    timer.start(100)  # 毎100ミリ秒

    sys.exit(app.exec_())
