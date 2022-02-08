import logging
import pandas as pd

from pathlib import Path

from math import log10
from collections import Counter
from collections import OrderedDict

from PyQt5.QtWidgets import QMessageBox
from PyQt5.QtGui import QPixmap
from PyQt5.QtCore import Qt
from PyQt5.QtCore import pyqtSlot

from cand_viewer.view import ClassifierViewer


class ClassifierApp(ClassifierViewer):
    def __init__(self, image_paths, outfile, history_file=None):
        super().__init__()
        self._configure_logger()
        self.image_paths = image_paths
        self.outfile = outfile
        self.history_file = history_file
        self.history_label = {}
        self.image_index = 0
        self.image_label = {img: None for img in self.image_paths}
        self.btn_false.clicked.connect(self._on_click_left)
        self.btn_true.clicked.connect(self._on_click_right)
        self.btn_confirm.clicked.connect(self.export)
        self.btn_up.clicked.connect(self._on_click_up)

        if self.history_file is not None:
            self.history_file = Path(self.history_file)
            if self.history_file.exists():
                self._load_history()
        self._render_image()

    @property
    def num_images(self) -> int:
        return len(self.image_paths)

    def _load_history(self):
        self.logger.info(f"Loading history file - {self.history_file}")
        df = pd.read_csv(self.history_file)
        df = df.fillna("")
        history_label = df.to_dict("split")["data"]
        history_label = {
            img: int(label) for img, label in history_label if not isinstance(label, str)
        }
        self.history_label = history_label
        self.image_label.update(history_label)
        self._goto_next_unlabeled_image()

    def _render_image(self):
        assert 0 <= self.image_index < self.num_images
        image = QPixmap(self.image_paths[self.image_index])
        resize_width = min(image.width(), self.screen.width() * 0.75)
        resize_height = min(image.height(), self.screen.height() * 0.75)
        image = image.scaled(
            resize_width,
            resize_height,
            Qt.KeepAspectRatio,
            transformMode=Qt.SmoothTransformation,
        )
        self.label_head.setPixmap(image)
        self.label_head.resize(resize_width, resize_height)
        self._render_status()
        self.show()

    def _render_status(self):
        image_name = Path(self.image_paths[self.image_index]).stem
        counter = Counter(self.image_label.values())
        labeled = self.image_label[self.image_paths[self.image_index]]
        pad_zero = int(log10(self.num_images)) + 1
        image_str = str(self.image_index + 1).zfill(pad_zero)
        if labeled is not None:
            self.label_status.setText(
                f"({image_str}/{self.num_images}) {image_name} => Labeled as {labeled}"
            )
        else:
            self.label_status.setText(f"({image_str}/{self.num_images}) {image_name}")
        self.btn_false.setText(f"< False ({counter[0]})")
        self.btn_true.setText(f"True ({counter[1]}) >")
        self.btn_up.setText(f"Maybe ({counter[-1]}) ^")

    def _undo_image(self):
        if self.image_index == 0:
            QMessageBox.warning(self, "Warning", "Reach the top of images")
        else:
            self.image_index = max(self.image_index - 1, 0)
            self._render_image()

    def _next_image(self):
        if self.image_index == self.num_images - 1:
            QMessageBox.warning(self, "Warning", "Reach the end of images")
        else:
            self.image_index = min(self.image_index + 1, self.num_images - 1)
            self._render_image()

    def _goto_prev_unlabeled_image(self):
        if self.image_index == 0:
            QMessageBox.warning(self, "Warning", "Reach the top of images")
        else:
            prev_image_index = self.image_index
            for idx in range(self.image_index - 1, 0, -1):
                # label could be the value in [0, 1, None]
                if self.image_label[self.image_paths[idx]] is None:
                    prev_image_index = idx
                    break
            if prev_image_index == self.image_index:
                QMessageBox.information(
                    self, "Information", "No more prev unlabeled image"
                )
            else:
                self.image_index = prev_image_index
                self._render_image()

    def _goto_next_unlabeled_image(self):
        if self.image_index == self.num_images - 1:
            QMessageBox.warning(self, "Warning", "Reach the end of images")
        else:
            next_image_index = self.image_index
            for idx in range(self.image_index + 1, self.num_images):
                # label could be the value in [0, 1, None]
                if self.image_label[self.image_paths[idx]] is None:
                    next_image_index = idx
                    break
            if next_image_index == self.image_index:
                QMessageBox.information(
                    self, "Information", "No more next unlabeled image"
                )
            else:
                self.image_index = next_image_index
                self._render_image()

    @pyqtSlot()
    def _on_click_left(self):
        self.image_label[self.image_paths[self.image_index]] = 0
        if self.image_index == self.num_images - 1:
            self._render_image()
            QMessageBox.warning(self, "Warning", "Reach the end of images")
        else:
            self.image_index = min(self.image_index + 1, self.num_images - 1)
            self._render_image()

    @pyqtSlot()
    def _on_click_right(self):
        self.image_label[self.image_paths[self.image_index]] = 1
        if self.image_index == self.num_images - 1:
            self._render_image()
            QMessageBox.warning(self, "Warning", "Reach the end of images")
        else:
            self.image_index = min(self.image_index + 1, self.num_images - 1)
            self._render_image()

    @pyqtSlot()
    def _on_click_up(self):
        self.image_label[self.image_paths[self.image_index]] = -1
        if self.image_index == self.num_images - 1:
            self._render_image()
            QMessageBox.warning(self, "Warning", "Reach the end of images")
        else:
            self.image_index = min(self.image_index + 1, self.num_images - 1)
            self._render_image()

    @pyqtSlot()
    def export(self):
        orderdict = OrderedDict(sorted(self.image_label.items(), key=lambda x: x[0]))
        df = pd.DataFrame(
            data={"image": list(orderdict.keys()), "label": list(orderdict.values())},
            dtype="int",
        )
        df.to_csv(self.outfile, index=False)
        self.logger.info(f"Export label result {self.outfile}")

    def keyPressEvent(self, event):
        if event.key() in {Qt.Key_Left, Qt.Key_A}:
            self.btn_false.click()
        elif event.key() in {Qt.Key_Right, Qt.Key_D}:
            self.btn_true.click()
        elif event.key() in {Qt.Key_Up, Qt.Key_W}:
            self.btn_up.click()
        elif event.key() == Qt.Key_U:
            self._undo_image()
        elif event.key() == Qt.Key_N:
            self._next_image()
        elif event.key() == Qt.Key_PageUp:
            self._goto_prev_unlabeled_image()
        elif event.key() == Qt.Key_PageDown:
            self._goto_next_unlabeled_image()
        else:
            self.logger.debug(f"You Clicked {event.key()} but nothing happened...")

    def _configure_logger(self) -> None:
        self.logger = logging.getLogger("ClassifierApp")
