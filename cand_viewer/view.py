from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QDesktopWidget
from PyQt5.QtWidgets import QHBoxLayout
from PyQt5.QtWidgets import QGridLayout
from PyQt5.QtWidgets import QPushButton
from PyQt5.QtWidgets import QWidget
from PyQt5.QtWidgets import QLabel
from PyQt5.QtGui import QFont


class ClassifierViewer(QWidget):
    def __init__(self, title="Transient candidates classifier"):
        super().__init__()
        self.title = title
        self.desktop = QDesktopWidget()
        self.screen = self.desktop.availableGeometry()
        self.init_window()

    def init_window(self):
        self.setWindowTitle(self.title)
        self.init_widgets()

    def init_widgets(self):
        self.grid_root = QGridLayout()
        self.hbox_body = QHBoxLayout()
        self.hbox_foot = QHBoxLayout()
        self.setLayout(self.grid_root)

        self.label_head = QLabel(self)
        self.btn_false = QPushButton("< False", self)
        self.btn_true = QPushButton("True >", self)
        self.btn_up = QPushButton("Maybe^", self)
        self.label_status = QLabel(self)
        self.btn_confirm = QPushButton("Confirm", self)
        self.font_default = QFont()
        self.font_button = QFont()

        self.font_default.setBold(True)
        self.font_default.setPointSize(12)
        self.font_button.setPointSize(12)

        self.btn_false.setFont(self.font_default)
        self.btn_false.setStyleSheet("background-color : #ffa5a5")
        self.btn_true.setFont(self.font_default)
        self.btn_true.setStyleSheet("background-color: #c4ffc1")
        self.btn_up.setFont(self.font_default)
        self.btn_up.setStyleSheet("background-color: #feffa8")
        self.label_status.setFont(self.font_default)
        self.btn_confirm.setFont(self.font_button)

        self.grid_root.addWidget(self.label_head, 0, 0, Qt.AlignCenter)
        self.grid_root.addLayout(self.hbox_body, 1, 0)
        self.grid_root.addLayout(self.hbox_foot, 2, 0)
        self.hbox_body.addWidget(self.btn_false, Qt.AlignCenter)
        self.hbox_body.addWidget(self.btn_up, Qt.AlignCenter)
        self.hbox_body.addWidget(self.btn_true, Qt.AlignCenter)
        self.hbox_foot.addWidget(self.label_status, Qt.AlignLeft)
        self.hbox_foot.addWidget(self.btn_confirm, 0, Qt.AlignRight)
