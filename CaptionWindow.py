from PyQt5 import QtWidgets, QtCore
import sys
import textwrap

class CaptionWindow(QtWidgets.QLabel):
    def __init__(self):
        super().__init__()
        self.setWindowFlags(
            QtCore.Qt.WindowStaysOnTopHint |
            QtCore.Qt.FramelessWindowHint |
            QtCore.Qt.Tool
        )
        # self.setAttribute(QtCore.Qt.WA_TranslucentBackground)
        self.setStyleSheet("""
            QLabel {
                color: white;
                font-size: 32px;
                background-color: rgba(0, 0, 0, 0.7);
                padding: 12px 24px;
                border-radius: 16px;
            }          
        """)
        self.setText("")
        screen = QtWidgets.QApplication.primaryScreen().availableGeometry()
        # 最大幅は画面幅からマージンを差し引いた値に設定
        self.max_width = screen.width() - 100
        self.setWordWrap(True)
        self.setMaximumWidth(self.max_width)
        self.adjustSize()

        # 10秒無音で自動非表示にするタイマー
        self.hide_timer = QtCore.QTimer(self)
        self.hide_timer.setSingleShot(True)
        self.hide_timer.setInterval(10000)
        self.hide_timer.timeout.connect(self.clear_caption)

        # 状態管理
        self.transparency = False
        self.layout_mode = "bottom-center"

        # ドラッグ用
        self.drag_position = None

        self.update_position()
        self.hide()

    def clear_caption(self):
        """字幕を消してウィンドウを隠す"""
        self.setText("")
        self.adjustSize()
        self.hide()

    def update_position(self):
        """レイアウトモードに応じて位置を調整"""
        screen = QtWidgets.QApplication.primaryScreen().availableGeometry()
        if self.layout_mode == "bottom-center":
            x = (screen.width() - self.width()) // 2
            y = screen.height() - self.height() - 50
        elif self.layout_mode == "top-left":
            x = 50
            y = 50
        elif self.layout_mode == "top-center":
            x = (screen.width() - self.width()) // 2
            y = 50
        elif self.layout_mode == "bottom-right":
            x = screen.width() - self.width() - 50
            y = screen.height() - self.height() - 50
        else:
            # デフォルト
            x, y = 100, 100
        self.move(x, y)

    def keyPressEvent(self, event):
        if event.key() == QtCore.Qt.Key_T:
            # Tキーで透過トグル
            if self.transparency:
                self.setWindowOpacity(1.0)
            else:
                self.setWindowOpacity(0.5)
            self.transparency = not self.transparency

        elif event.key() == QtCore.Qt.Key_Space:
            # Spaceキーでレイアウトモード変更
            layout_options = ["bottom-center", "top-left", "top-center", "bottom-right"]
            next_index = (layout_options.index(self.layout_mode) + 1) % len(layout_options)
            self.layout_mode = layout_options[next_index]
            self.update_position()

    def mousePressEvent(self, event):
        if event.button() == QtCore.Qt.LeftButton:
            self.drag_position = event.globalPos() - self.frameGeometry().topLeft()

    def mouseMoveEvent(self, event):
        if self.drag_position and event.buttons() == QtCore.Qt.LeftButton:
            self.move(event.globalPos() - self.drag_position)

    def mouseReleaseEvent(self, event):
        self.drag_position = None

    def update_caption(self, text: str):
        """キャプションをリアルタイム更新"""
        # 画面サイズに応じて最大幅を更新し、テキストを折り返して表示
        screen = QtWidgets.QApplication.primaryScreen().availableGeometry()
        self.max_width = screen.width() - 100
        self.setMaximumWidth(self.max_width)

        metrics = self.fontMetrics()
        char_width = metrics.averageCharWidth()
        line_chars = max(1, self.max_width // char_width)
        wrapped_lines = textwrap.wrap(text, width=line_chars)
        display_lines = wrapped_lines[-2:]
        display_text = "\n".join(display_lines)

        self.setText(display_text)
        self.adjustSize()
        self.update_position()
        self.show()

        # 無音カウントダウンをリセット
        self.hide_timer.start()

if __name__ == "__main__":
    # 単体テスト
    app = QtWidgets.QApplication(sys.argv)
    window = CaptionWindow()

    # デモ: 5秒後にキャプション変更
    QtCore.QTimer.singleShot(5000, lambda: window.update_caption("これは5秒後に更新されたキャプションです"))

    sys.exit(app.exec_())
