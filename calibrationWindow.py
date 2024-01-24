import sys
import os

from PyQt5.QtWidgets import (
    QApplication,
    QLabel,
    QVBoxLayout,
    QGridLayout,
    QStackedLayout,
    QWidget,
    QMainWindow
)
from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtGui import QPixmap, QFont, QPalette, QColor
from PyQt5.QtWidgets import QGraphicsOpacityEffect

class CalibWindow(QMainWindow):
    closed = pyqtSignal()

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
        self.msg_label.setStyleSheet(f"background-color: transparant;")

        self.mode_label = QLabel(f"", self)
        self.mode_label.setFont(font)
        self.mode_label.setAlignment(Qt.AlignLeft)

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
        layout_v.addWidget(self.mode_label)
        layout_v.addWidget(self.curlabel_label)
        layout_v.addLayout(layout_grid)
 
        self.ctr_widget = QWidget()
        self.ctr_widget.setLayout(layout_v)
        self.setCentralWidget(self.ctr_widget)

    def resizeEvent(self, event):
        # Update image size when resize window
        for cls in self.file_name.keys():
            self.set_img(cls)
    
    def closeEvent(self, event):
        self.closed.emit()
        event.accept()

    # set pixmap of image label
    def set_img(self, cls):
        image_path = os.path.join(self.current_dir, "icon", self.file_name[cls])
        width = int(self.height() * 0.22)  # 窗口宽度的20%
        height = int(self.height() * 0.22)  # 窗口高度的20%
        pixmap = QPixmap(image_path).scaled(width, height)
        self.image_labels[cls].setPixmap(pixmap)

    # set the class(label) to show and let others invisible
    def set_cls_img(self, cls2show):
        for cls, img in self.image_labels.items():
            # set opacity of current class to 1.0 (visible)
            if cls == cls2show:
                opacity_effect = QGraphicsOpacityEffect(self)
                opacity_effect.setOpacity(1.0)
                img.setGraphicsEffect(opacity_effect)
            # set opacity of other class to 0.0 (invisible)
            else:
                opacity_effect = QGraphicsOpacityEffect(self)
                opacity_effect.setOpacity(0.0)
                img.setGraphicsEffect(opacity_effect)
    
    # set current label
    def set_label(self, cur_label):
        if cur_label == None: 
            self.curlabel_label.setText("Current Label : N/A")
        else:
            self.curlabel_label.setText(f"Current Label :  {cur_label}")

    # set current mode
    def set_mode(self, text):
        self.mode_label.setText(text)

    # set massage
    def set_msg(self, msg):
        self.msg_label.setText(msg)    

    def set_msg_bg(self, invisible):
        color = "transparent" if invisible else "black"
        self.msg_label.setStyleSheet(f"background-color: {color};")

if __name__ == "__main__":
    app = QApplication(sys.argv)
    w = CalibWindow()
    w.show()
    app.exec()