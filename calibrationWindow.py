import sys
import os
from time import time
import random
random.seed(18796441854)

from PyQt5.QtWidgets import (
    QApplication,
    QLabel,
    QVBoxLayout,
    QGridLayout,
    QWidget,
    QMainWindow
)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QPixmap, QFont
from PyQt5.QtWidgets import QGraphicsOpacityEffect

class CalibWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        # get current directory
        self.current_dir = os.path.dirname(os.path.abspath(__file__))

        self.setWindowTitle("MI Calibration")
        self.setGeometry(100, 100, 1000, 750)

        # Init text labels
        font = QFont()
        font.setPointSize(20)  # Font size
        self.msg_label = QLabel("Ready",self)
        self.msg_label.setFont(font)
        self.msg_label.setAlignment(Qt.AlignCenter)

        self.finish_label = QLabel(f"Finished Trial : 0 / 0", self)
        self.finish_label.setFont(font)
        self.finish_label.setAlignment(Qt.AlignLeft)

        self.curlabel_label = QLabel(f"Current Label : N/A", self)
        self.curlabel_label.setFont(font)
        self.curlabel_label.setAlignment(Qt.AlignLeft)
        # Init image labels 
        self.file_name = {
            "LH":"fist_L.png",
            "RH":"fist_R.png",
            "BH":"fist_Both.png",
            "F" :"foot.png"
        }
        self.image_labels = {}
        for cls in self.file_name.keys():
            self.image_labels[cls] = QLabel(self)
            self.set_img(cls)

        layout_grid = QGridLayout()
        layout_grid.addWidget(self.image_labels["LH"], 1, 0)
        layout_grid.addWidget(self.image_labels["RH"], 1, 2)
        layout_grid.addWidget(self.image_labels["BH"], 0, 1)
        layout_grid.addWidget(self.image_labels["F"] , 2, 1)
        layout_grid.addWidget(self.msg_label, 1, 1)
        layout_grid.setAlignment(Qt.AlignCenter)
        layout_grid.setContentsMargins(50,50,50,50)
        layout_grid.setSpacing(75)

        layout_v = QVBoxLayout()
        layout_v.addWidget(self.finish_label)
        layout_v.addWidget(self.curlabel_label)
        layout_v.addLayout(layout_grid)

        self.ctr_widget = QWidget()
        self.ctr_widget.setLayout(layout_v)
        self.setCentralWidget(self.ctr_widget)

    def resizeEvent(self, event):
        # Update image size when resize window
        for cls in self.file_name.keys():
            self.set_img(cls)

    def set_img(self, cls):
        image_path = os.path.join(self.current_dir, "icon", self.file_name[cls])
        width = int(self.height() * 0.22)  # 窗口宽度的20%
        height = int(self.height() * 0.22)  # 窗口高度的20%
        pixmap = QPixmap(image_path).scaled(width, height)
        self.image_labels[cls].setPixmap(pixmap)

    def set_label(self, cur_label):
        if cur_label == None:
            self.curlabel_label.setText("Current Label : N/A")
        else:
            for cls, img in self.image_labels.items():
                if cls == cur_label:
                    opacity_effect = QGraphicsOpacityEffect(self)
                    opacity_effect.setOpacity(1.0)
                    # 应用透明度效果到 QLabel
                    self.image_labels[cls].setGraphicsEffect(opacity_effect)
                else:
                    opacity_effect = QGraphicsOpacityEffect(self)
                    opacity_effect.setOpacity(0.0)
                    # 应用透明度效果到 QLabel
                    self.image_labels[cls].setGraphicsEffect(opacity_effect)
            
            self.curlabel_label.setText(f"Current Label : {cur_label}")

    def set_finished_trial(self, finished, total):
        self.finish_label.setText(f"Finished Trial : {finished} / {total}")

if __name__ == "__main__":
    app = QApplication(sys.argv)
    w = CalibWindow()
    w.show()
    app.exec()