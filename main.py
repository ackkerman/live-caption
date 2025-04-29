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
CHUNK_SIZE =4000
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
    """Voskで音声認識してキャプション更新（Partial対応版）"""
    model = Model(lang="en-us")  # or "ja" model for Japanese
    rec = KaldiRecognizer(model, SAMPLE_RATE)

    final_text = ""  # 最終確定テキスト保持用

    while True:
        indata = audio_queue.get()
        if indata is None:
            continue
        bytes_data = indata.tobytes()

        if rec.AcceptWaveform(bytes_data):
            # 音声フレーズが1個完了した場合
            result = rec.Result()
            import json
            text = json.loads(result).get("text", "")
            if text:
                print(f"[FINAL] {text}")  # ★確定結果を出力
                final_text = text
                window.update_caption(final_text)
        else:
            # フレーズ途中でも partial を拾う
            partial_result = rec.PartialResult()
            import json
            partial_text = json.loads(partial_result).get("partial", "")
            if partial_text:
                # 標準出力にPartialも出す（見た目確認用）
                print(f"[PARTIAL] {partial_text}")
                # ウィンドウには partial を即時反映（ヌルヌル！）
                window.update_caption(f"{final_text} {partial_text}")


if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    window = CaptionWindow()

    # 音声キャプチャ用スレッド
    threading.Thread(target=audio_capture_worker, daemon=True).start()

    # 音声認識用スレッド
    threading.Thread(target=recognize_worker, args=(window,), daemon=True).start()

    sys.exit(app.exec_())
