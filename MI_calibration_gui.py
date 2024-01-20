import sys
import os
import time
import random
random.seed(18796441854)

from pylsl import StreamInfo, StreamOutlet
import numpy as np

from PyQt5.QtWidgets import (
    QApplication,
    QLabel,
    QProgressBar,
    QMainWindow,
    QPushButton,
    QVBoxLayout,
    QWidget,
    QFrame
)
from PyQt5.QtMultimedia import QSoundEffect
from PyQt5.QtCore import Qt, QThread, pyqtSignal, QUrl
from PyQt5.QtGui import QFont

# files
from calibrationWindow import CalibWindow


# main window for controlling clibration window
class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Control Panel")
        self.calib_win = CalibWindow()
        self.calib_win.closed.connect(lambda: self.button_show.setDisabled(False))

        # Vertical layout
        l = QVBoxLayout()

        # button1: initialize calibration window
        self.button_show = QPushButton("Show")
        self.button_show.clicked.connect(self.show_calib_window)
        l.addWidget(self.button_show)

        # button2: start session
        self.session_started = False
        self.is_pause = False
        self.button_start = QPushButton("Start")
        self.button_start.clicked.connect(self.start)
        l.addWidget(self.button_start)

        # button3: pause calibration
        self.button_pause = QPushButton("Pause")
        self.button_pause.clicked.connect(self.pause)
        self.button_pause.setDisabled(True)
        l.addWidget(self.button_pause)

        # separator
        separator_line = QFrame()
        separator_line.setFrameShape(QFrame.HLine)
        separator_line.setFrameShadow(QFrame.Sunken)
        l.addWidget(separator_line)
        # Init text label
        font = QFont()
        font.setPointSize(15)  # Font size
        self.msg_label = QLabel("Ready",self)
        self.msg_label.setFont(font)
        self.msg_label.setAlignment(Qt.AlignLeft)
        l.addWidget(self.msg_label)
        # QProgressBar
        self.progress_bar = QProgressBar()
        l.addWidget(self.progress_bar)

        # Central Widget
        w = QWidget()
        w.setLayout(l)
        self.setCentralWidget(w)
        
        #--------------------------------------------------
        # Settings
        self.start_time = time.time()
        self.end_time = time.time()
        self.cur_label = None
        self.cur_mode = None
        self.finished_trial = 0
        self.finished_ssvep = 0

        # Init MI parameters
        self.MI_init()

        # array of all Trials to process 
        # ( label , mode )
        # eog
        self.trials_all = [("EOG-OPEN", "EOG"), ("EOG-CLOSE", "EOG")]
        # warm up
        for label in self.trial_labels:
            self.trials_all.append((label, "Warm-up"))
        # calibration
        for label in self.labels_arr:
            self.trials_all.append((label, "Calibration"))
        
        self.cur_pointer = 0

        # Init Worker thread used to process trial
        self.worker = WorkerThread()
        self.worker.trigger_stage.connect(self.process_stage)
        self.worker.finished.connect(self.end_trial)
        # Init Worker thread used to process trial
        self.counter = CounterThread()
        self.counter.trigger.connect(self.calib_win.set_msg)
        self.counter.finished.connect(self.process_trial)

        # Init pyLSL
        info = StreamInfo(name='MotorImag-Markers', type='Markers', channel_count=1,
                  nominal_srate=0, channel_format='string',
                  source_id='t8u43t97u')
        self.outlet = StreamOutlet(info)

        # Init QSoundEffect
        current_dir = os.path.dirname(os.path.abspath(__file__))
        sound_file = {
            "LH":"cue_LH.wav",
            "RH":"cue_RH.wav",
            "BH":"cue_BH.wav",
            "F" :"cue_F.wav",
            "SSVEP":"cue_SSVEP.wav",
            "EOG-OPEN":"cue_EOG-OPEN.wav",
            "EOG-CLOSE":"cue_EOG-CLOSE.wav",
            "start":"button04a.wav",
            "end":"button02a.wav"
        }
        self.sound = {}
        for cls, file in sound_file.items():
            self.sound[cls] = QSoundEffect(self)
            image_path = os.path.join(current_dir, "sound", file)
            self.sound[cls].setSource(QUrl.fromLocalFile(image_path))
            self.sound[cls].setVolume(1.0)

    # ---UI Methods---
    def closeEvent(self, event):
        # close CalibWindow while closing MainWindow
        self.calib_win.close()
        event.accept()
    
    def show_calib_window(self):
        self.calib_win.show()
        self.button_show.setDisabled(True)    
    
    def pause(self):
        self.is_pause = True
        self.button_pause.setDisabled(True)
        self.button_start.setDisabled(False)  

    def start(self):
        # send SESSION-begin if session haven't started 
        if not self.session_started:
            self.session_started == True
            self.outlet.push_sample(['SESSION-begin'])
        self.button_start.setDisabled(True)  
        self.button_pause.setDisabled(False)
        if self.is_pause:
            self.is_pause = False
            self.counter.set_parameter(
                count_time = 5,
                msg = "Resume"
            )
            self.counter.start()
            return
        self.process_trial()

    def process_trial(self):
        if self.cur_pointer >= len(self.trials_all):
            return
        if self.is_pause:
            self.calib_win.set_msg("- Pause -\n\npress Start button to resume")
            return
        label, mode = self.trials_all[self.cur_pointer]
        self.start_trial(label, mode)

    # ---MI Related Methods---
    # initiliza MI parameter
    def MI_init(self):
        self.trials_per_class = 48
        self.perform_time = 3.2
        self.eog_perform_time = 3
        self.init_time = 2
        self.rest_time = 2
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

    def start_trial(self, cls, mode):
        self.start_time = time.time()
        self.cur_label = cls

        # if calibration start, count down first
        if mode == "Calibration" and self.cur_mode != "Calibration":
            self.cur_mode = mode
            self.counter.set_parameter(
                count_time = 10,
                msg = "Calibration Start"
            )
            self.counter.start()
            return
        
        self.cur_mode = mode

        # update calib window and msg_label
        if mode == "EOG":
            self.calib_win.set_mode("EOG")
            self.msg_label.setText(self.cur_label)
        elif mode == "Warm-up":
            self.calib_win.set_mode("Warm-up")
            self.msg_label.setText("Warm-up")
        else:
            msg = f"Calibration {self.finished_trial+1} / {self.total_trial_num}"
            self.calib_win.set_mode(msg)
            self.msg_label.setText(msg)
        self.calib_win.set_label(cls)
        self.calib_win.set_cls_img(None)
        self.calib_win.set_msg("+")

        # get perform time
        if cls == "EOG-CLOSE" or cls == "EOG-OPEN":
            perform_time = self.eog_perform_time
        else:
            perform_time = self.perform_time

        self.worker.init_time = self.init_time
        self.worker.perform_time = perform_time
        self.worker.rest_time = self.rest_time
        self.worker.start()

    def process_stage(self, stage):
        if stage == "init":
            # update calib window
            self.calib_win.set_cls_img(None)
            self.calib_win.set_msg("+")
            # play sound
            self.sound[self.cur_label].play()
            # send LSL marker
            self.outlet.push_sample(['trial-begin'])
        elif stage == "perform":
            # update calib window
            self.calib_win.set_cls_img(self.cur_label)
            if self.cur_label not in self.MI_labels:
                self.calib_win.set_msg("+")
            else:
                self.calib_win.set_msg("")
            # play sound
            self.sound['start'].play()
            # send LSL marker
            marker = ""
            if self.cur_label == "Warm-up":
                marker += "Warm-up"
            marker += self.cur_label
            self.outlet.push_sample([marker])
        elif stage == "rest":
            # update calib window
            self.calib_win.set_cls_img(None)
            self.calib_win.set_msg("+")
            # play sound
            self.sound['end'].play()
            # send LSL marker
            self.outlet.push_sample(['trial-begin'])

    def end_trial(self):
        print("trial end")
        self.end_time = time.time()
        print(f"實際執行時間為: {self.end_time - self.start_time} 秒")

        self.cur_pointer += 1
        if self.cur_mode == "Calibration":
            self.finished_trial += 1
            if self.cur_label == "SSVEP":
                self.finished_ssvep += 1

        # update progress bar
        progress_value = (self.cur_pointer / len(self.trials_all)) * 100
        self.progress_bar.setValue(int(progress_value))
        
        # next trial or end the session
        if self.cur_pointer >= len(self.trials_all):
            self.end_session()
        elif self.finished_trial != 0 and self.finished_trial % self.rest_every == 0:
            self.counter.set_parameter(
                count_time = self.rest_duration,
                msg = f"Rest {self.rest_duration} sec",
            )
            self.counter.start()
        else:
            self.process_trial()
            
        
    def end_session(self):
        # Send SESSION-end
        self.outlet.push_sample(['SESSION-end'])
        # count down
        self.counter.set_parameter(
            count_time = 10,
            msg = "Calibration End"
        )
        self.counter.start()

class WorkerThread(QThread):
    trigger_stage = pyqtSignal(str)
    finished = pyqtSignal()

    def __init__(self):
        super().__init__()
        self.init_time = 2
        self.perform_time = 3
        self.rest_time = 2

    def run(self):
        # init stage
        self.trigger_stage.emit("init")
        time.sleep(self.init_time)
        # perform stage
        self.trigger_stage.emit("perform")
        time.sleep(self.perform_time)
        # rest stage
        self.trigger_stage.emit("rest")
        time.sleep(self.rest_time)

        self.finished.emit()

class CounterThread(QThread):
    trigger = pyqtSignal(str)
    finished = pyqtSignal()

    def __init__(self):
        super().__init__()
        self.count_time = 5
        self.msg = "msg"

    def set_parameter(self, count_time, msg):
        self.count_time = count_time
        self.msg = msg

    def run(self):
        for sec in range(self.count_time, 0, -1):
            self.trigger.emit(f'{self.msg}\n\n{sec}')
            time.sleep(1)

        self.finished.emit()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    w = MainWindow()
    w.show()
    app.exec()