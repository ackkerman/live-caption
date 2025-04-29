from CaptionWindow import CaptionWindow
from PyQt5 import QtWidgets
import sys
import sounddevice as sd
import queue
import threading
from vosk import Model, KaldiRecognizer
import json

# --- 音声キャプチャ設定 ---
SAMPLE_RATE = 48000
CHUNK_SIZE = 36000
MONITOR_DEVICE_INDEX = 0

# --- 音声ストリームを入れるキュー ---
audio_queue = queue.Queue()

def audio_capture_worker():
    """sounddeviceでモニター音声をキャプチャ"""
    def callback(indata, frames, time, status):
        if status:
            print(f"Audio Callback Status: {status}", file=sys.stderr)
        # 16bit PCM形式に変換してqueueへ
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
    """Voskで音声認識してキャプション更新"""
    model = Model(lang="en-us")  # or "ja" model for Japanese
    rec = KaldiRecognizer(model, SAMPLE_RATE)

    while True:
        indata = audio_queue.get()
        if indata is None:
            continue
        bytes_data = indata.tobytes()
        if rec.AcceptWaveform(bytes_data):
            result = rec.Result()
            text = json.loads(result).get("text", "")
            if text:
                print(f"Recognized: {text}")
                window.update_caption(text)

if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    window = CaptionWindow()

    # 音声キャプチャ用スレッド
    threading.Thread(target=audio_capture_worker, daemon=True).start()

    # 音声認識用スレッド
    threading.Thread(target=recognize_worker, args=(window,), daemon=True).start()

    sys.exit(app.exec_())
