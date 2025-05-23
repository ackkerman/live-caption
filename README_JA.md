# Live Caption App for Linux

[English](./README.md) / [日本語](./README_JA.md)

PCで再生されるすべての音声をリアルタイム認識して、  
画面に字幕（キャプション）を表示するアプリです。

Androidの「Live Caption」機能にインスパイアされて作られました。

https://github.com/user-attachments/assets/5fbaa334-c55b-49f7-b66b-9903ab4a828f



## ✨ 主な機能

- OS全体の音声（動画・音楽・通話など）をキャプチャ
- Vosk音声認識エンジンでリアルタイム字幕化
- 部分認識 (Partial) にも対応し、超低遅延なキャプション表示
- キャプション表示ウィンドウは最前面固定・自由配置可能
- Ctrl+Cを二度押すことで安全に終了可能


## 🖥 動作環境

- Linux（**PipeWire または PulseAudio環境**）
- Python 3.10 以上推奨
- モニターソース（例：`alsa_output.pci-0000_00_1f.3.analog-stereo.monitor`）が利用可能なこと


## 🛠 インストール手順

1. リポジトリのクローン

2. 必要なパッケージをインストール

    ```bash
    poetry install
    ```

3. モニターソースのデバイス番号を確認

    ```bash
    poetry run python scripts/monitor_device.py
    ```

5. `live_caption/cli.py` 内の `MONITOR_DEVICE_INDEX` を正しい番号に設定するか、
   起動時に `--device` オプションで指定してください


## 🚀 起動方法

```bash
poetry run live-caption
```

主なオプション:

```bash
poetry run live-caption --device 2 --mic-device 1 --sample-rate 44100 --chunk-size 2048
```

- キャプションウィンドウが最前面に表示されます
- 音声に合わせてリアルタイム字幕が更新されます
- キーボードの **M** キーでマイクのオン・オフを切り替えられます


## 🛑 終了方法

- Ctrl+C を**2回押す**と安全にアプリが終了します
- アプリが固まることなく、リソースもきれいに開放されます


## ⚙️ 今後の拡張予定

- [x] **デバイスマイクのオン・オフ**
- [ ] **キャプションのスタイル変更対応**
- [x] **キャプションの折り返し・複数行表示**
- [ ] **Whisper.cppなど他の音声認識エンジンへの切り替え**
- [ ] **多言語キャプション対応（言語自動切替・同時翻訳）**  
- [ ] **キャプションの位置とサイズのGUI調整ツール**  
- [ ] **クリックスルー（マウス透過）モード**  
- [x] **フェードアウト付き終了／自動非表示オプション**

## 🛡 注意事項

- 認識精度はVoskモデルに依存します。  
  より高精度な認識が必要な場合は、大きいモデルまたは別エンジンへの切り替えを検討してください。
- 本アプリはローカル動作のみで、音声データは外部に送信されません。

## 📜 ライセンス

MIT License
