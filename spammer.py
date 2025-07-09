import sys
import keyboard
from PyQt5.QtWidgets import (
    QApplication, QWidget, QPushButton, QVBoxLayout, QLabel, QLineEdit, QSlider, QHBoxLayout, QMessageBox, QSystemTrayIcon, QMenu, QAction, QStyle, QSpinBox
)
from PyQt5.QtCore import QTimer, Qt
from PyQt5.QtGui import QIcon

class KeySpammer(QWidget):
    def __init__(self):
        super().__init__()

        self.hold_key = ''
        self.spam_key = ''
        self.spamming = False

        self.timer = QTimer()
        self.timer.timeout.connect(self.check_keys)

        self.init_ui()
        self.init_tray()

    def init_ui(self):
        self.setWindowTitle('Key Spammer')
        self.setFixedSize(300, 360)

        layout = QVBoxLayout()

        self.hold_label = QLabel('Hold Key: (e.g., a)')
        self.hold_input = QLineEdit()

        self.spam_label = QLabel('Spam Key: (e.g., b)')
        self.spam_input = QLineEdit()

        speed_label = QLabel('Spam Speed:')
        self.speed_slider = QSlider(Qt.Horizontal)
        self.speed_slider.setMinimum(1)
        self.speed_slider.setMaximum(100)
        self.speed_slider.setValue(10)

        self.speed_value_label = QLabel(f'{self.speed_slider.value()} ms')
        self.speed_slider.valueChanged.connect(lambda: self.speed_value_label.setText(f'{self.speed_slider.value()} ms'))

        custom_speed_label = QLabel('Or Custom Speed (ms):')
        self.custom_speed_input = QLineEdit()

        self.start_button = QPushButton('Start Listening')
        self.start_button.setToolTip('Shortcut: Ctrl+Shift+S to stop')
        self.start_button.clicked.connect(self.start_listening)

        self.stop_button = QPushButton('Stop Listening')
        self.stop_button.setToolTip('Shortcut: Ctrl+Shift+S to stop')
        self.stop_button.clicked.connect(self.stop_listening)

        self.status_label = QLabel('Status: Idle')

        layout.addWidget(self.hold_label)
        layout.addWidget(self.hold_input)
        layout.addWidget(self.spam_label)
        layout.addWidget(self.spam_input)
        layout.addWidget(speed_label)
        layout.addWidget(self.speed_slider)
        layout.addWidget(self.speed_value_label)
        layout.addWidget(custom_speed_label)
        layout.addWidget(self.custom_speed_input)

        button_layout = QHBoxLayout()
        button_layout.addWidget(self.start_button)
        button_layout.addWidget(self.stop_button)

        layout.addLayout(button_layout)
        layout.addWidget(self.status_label)

        self.setLayout(layout)

    def init_tray(self):
        self.tray_icon = QSystemTrayIcon(QIcon('black.png'), self)
        tray_menu = QMenu()

        show_action = QAction("Show", self)
        show_action.triggered.connect(self.show_window)

        exit_action = QAction("Exit", self)
        exit_action.triggered.connect(QApplication.instance().quit)

        tray_menu.addAction(show_action)
        tray_menu.addAction(exit_action)

        self.tray_icon.setContextMenu(tray_menu)
        self.tray_icon.activated.connect(self.tray_icon_clicked)
        self.tray_icon.show()

    def tray_icon_clicked(self, reason):
        if reason == QSystemTrayIcon.DoubleClick:
            self.show_window()

    def show_window(self):
        self.show()
        self.tray_icon.showMessage('Key Spammer', 'Restored from tray.', QSystemTrayIcon.Information, 2000)

    def closeEvent(self, event):
        event.ignore()
        self.hide()
        self.tray_icon.showMessage('Key Spammer', 'Minimized to tray. Right-click or double-click tray icon to restore.', QSystemTrayIcon.Information, 3000)

    def start_listening(self):
        self.hold_key = self.hold_input.text().strip().lower()
        self.spam_key = self.spam_input.text().strip().lower()

        if not self.hold_key or not self.spam_key:
            QMessageBox.warning(self, 'Input Error', 'Please set both keys.')
            return
        if self.custom_speed_input.text():
            try:
                interval = int(self.custom_speed_input.text()) 
            except ValueError:
                QMessageBox.warning(self, 'Input Error', 'Please enter a valid number for custom speed.')
                return
        else:
            interval = self.speed_slider.value()

        self.status_label.setText(f'Status: Listening for "{self.hold_key}" to spam "{self.spam_key}"')
        keyboard.block_key(self.hold_key)
        self.timer.start(interval)

        keyboard.add_hotkey('ctrl+shift+s', self.stop_listening)

    def stop_listening(self):
        self.timer.stop()
        keyboard.unblock_key(self.hold_key)
        self.status_label.setText('Status: Stopped')

    def check_keys(self):
        if keyboard.is_pressed(self.hold_key):
            keyboard.send(self.spam_key)

if __name__ == '__main__':
    app = QApplication(sys.argv)
    app.setQuitOnLastWindowClosed(False)

    spammer = KeySpammer()
    spammer.show()

    sys.exit(app.exec_())