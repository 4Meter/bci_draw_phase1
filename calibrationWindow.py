import sys
import os
from time import time
import random
random.seed(18796441854)

from pylsl import StreamInfo, StreamOutlet
import numpy as np
import pygame 
from math import pi

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

        # Settings
        self.pause = False
        self.start_time = time()
        self.end_time = time()
        self.cur_label = None
        self.calib_IDX = 0
        self.SSVEP_IDX = 0
        #initiliza MI parameter
        self.MI_init()
        self.warmup_finined = False
        self.warmup_labels = ['EOG-open','EOG-open']
        self.warmup_labels += self.MI_labels
        self.warmup_IDX = 0

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

        self.finish_label = QLabel(f"Finished Trial : 0 / {self.total_trial_num}", self)
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

        # Init pyLSL
        info = StreamInfo(name='MotorImag-Markers', type='Markers', channel_count=1,
                  nominal_srate=0, channel_format='string',
                  source_id='t8u43t98u')
        self.outlet = StreamOutlet(info)

    def set_img(self, cls):
        image_path = os.path.join(self.current_dir, "icon", self.file_name[cls])
        width = int(self.height() * 0.22)  # 窗口宽度的20%
        height = int(self.height() * 0.22)  # 窗口高度的20%
        pixmap = QPixmap(image_path).scaled(width, height)
        self.image_labels[cls].setPixmap(pixmap)

    def resizeEvent(self, event):
        # Update image size when resize window
        for cls in self.file_name.keys():
            self.set_img(cls)


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

    # ---MI Related Methods---
    # set the class to show and let others invisible
    #initiliza MI parameter
    def MI_init(self):
        self.trials_per_class = 48
        self.perform_time = 3.2
        self.eog_perform_time = 3
        self.wait_time = 2
        self.rest_every = 40
        self.rest_duration = 20
        self.MI_labels = ['LH', 'RH', 'F', 'BH']
        self.trial_labels = ['LH', 'RH', 'F', 'BH', 'SSVEP']
        self.total_trial_num = self.trials_per_class * len(self.trial_labels)

        #隨機SSVEP頻率 (0表示不顯示有12組,其他四個頻率9組)
        SSVEP_list = np.array([0,6,4.3,7.6,10])
        SSVEP_list = np.repeat(SSVEP_list,6)
        SSVEP_list = np.append(SSVEP_list,[0,0,0,0,0,0,0,0,0,
                                        6,6,6,6,6,6,6,6,6])
        random.shuffle(SSVEP_list)
        if len(SSVEP_list) != self.trials_per_class:
            print("SSVEP length is not match!")
        
        #產生實驗順序
        labels_arr = []
        for j in range(int(self.trials_per_class*len(self.trial_labels)/self.rest_every)):
            run_arr = []
            for i in range(int(self.rest_every/len(self.trial_labels))):
                for label in self.trial_labels:
                    run_arr.append(label)
            random.shuffle(run_arr)
            print(run_arr)
            labels_arr.append(run_arr)
        def flatten(l):
            return [item for sublist in l for item in sublist]
        self.labels_arr = flatten(labels_arr)

    def trial_start(self):
        if not self.warmup_finined:
            self.cur_label = self.warmup_labels[self.warmup_IDX]
            # play audio

            # set timer
        else:
            ...
        

    def initial_state_end(self):
        pass

    def trial_process(self):
        pass

    def process_end(self):
        pass

    def trial_rest(self):
        pass

    def trial_end(self):
        pass

if __name__ == "__main__":
    app = QApplication(sys.argv)
    w = CalibWindow()
    w.show()
    app.exec()