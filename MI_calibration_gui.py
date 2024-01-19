import sys

from PyQt5.QtWidgets import (
    QApplication,
    QLabel,
    QMainWindow,
    QPushButton,
    QVBoxLayout,
    QWidget,
)

from phase1.bci_draw_phase1.calibrationWindow import CalibWindow


# main window for controlling clibration window
class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Control Panel")
        self.calib_win = CalibWindow()

        l = QVBoxLayout()

        # button1: initialize calibration window
        self.button1 = QPushButton("Show")
        self.button1.clicked.connect(
            lambda checked: self.toggle_window(self.calib_win)
        )
        l.addWidget(self.button1)

        # button2: pause calibration
        self.started = False
        self.is_pause = False
        self.button2 = QPushButton("Start")
        self.button2.clicked.connect(self.toggle_pause)
        l.addWidget(self.button2)

        # button3: for test
        self.button3 = QPushButton("Test")
        self.button3.clicked.connect(self.test)
        l.addWidget(self.button3)

        w = QWidget()
        w.setLayout(l)
        self.setCentralWidget(w)

    def toggle_window(self, window):
        if window.isVisible():
            window.hide()
            self.button1.setText('Show')
        else:
            window.show()
            self.button1.setText('Hide')
    
    def toggle_pause(self):
        if not self.started:
            self.calib_win.start()
            self.started = True
            self.button2.setText('Resume' if self.is_pause else 'Pause')
            return

        self.is_pause = not self.is_pause
        if self.is_pause:
            self.calib_win.pause()
        else:
            self.calib_win.resume()
        self.button2.setText('Resume' if self.is_pause else 'Pause')

    def test(self):
        self.calib_win.set_class("LH")


if __name__ == "__main__":
    app = QApplication(sys.argv)
    w = MainWindow()
    w.show()
    app.exec()