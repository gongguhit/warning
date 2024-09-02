from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QLabel
from PyQt5.QtCore import pyqtSignal, QObject, Qt
from PyQt5.QtGui import QImage, QPixmap
import cv2

class Communicate(QObject):
    update_status = pyqtSignal(str)

class MainWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Face Recognition")
        self.setGeometry(100, 100, 800, 600)

        # Layout and widgets
        self.layout = QVBoxLayout()
        self.status_label = QLabel("Safe")
        self.status_label.setAlignment(Qt.AlignCenter)
        self.layout.addWidget(self.status_label)

        self.video_label = QLabel()
        self.layout.addWidget(self.video_label)

        self.setLayout(self.layout)

        # Communication object for threading
        self.comm = Communicate()
        self.comm.update_status.connect(self.update_status)

    def update_status(self, text):
        self.status_label.setText(text)

    def update_frame(self, frame):
        # Convert the frame to a QImage
        rgb_image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        h, w, ch = rgb_image.shape
        bytes_per_line = ch * w
        qt_image = QImage(rgb_image.data, w, h, bytes_per_line, QImage.Format_RGB888)
        pixmap = QPixmap.fromImage(qt_image)
        self.video_label.setPixmap(pixmap.scaled(640, 480, Qt.KeepAspectRatio))

def run_gui():
    app = QApplication([])
    window = MainWindow()
    window.show()
    return app, window

