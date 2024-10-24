from PyQt5.QtWidgets import QApplication, QWidget, QPushButton, QLineEdit,QGridLayout,QScrollArea,  QVBoxLayout, QFileDialog, QLabel, QHBoxLayout, QFrame
from PyQt5.QtGui import QImage, QPixmap
from PyQt5.QtWidgets import QFrame
from PyQt5.QtCore import QTimer
from Monitore import *

class VideoFrameWidget(QWidget):
    def __init__(self, monitore, annotation=False, track_plot=False) -> None:
        super().__init__()

        self.frame_label = QLabel()
        self.frame_label.setFrameStyle(QFrame.Box)
        self.layout = QVBoxLayout()
        self.layout.addWidget(self.frame_label)
        self.setLayout(self.layout)
        self.monitore = monitore
        self.annotation = annotation
        self.track_plot = track_plot


    def update_frame(self, frame):
        annotated_frame, class_0_count = self.monitore.predict(frame, annotation=self.annotation, track_plot=self.track_plot)
        h, w, ch = annotated_frame.shape
        bytes_per_line = w * ch
        qimage = QImage(annotated_frame.data, w, h, bytes_per_line, QImage.Format.Format_RGB888)

        self.frame_label.setPixmap(QPixmap.fromImage(qimage))

class MainWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.init_UI()
        self.video_paths = []
        self.cap = []
        self.timers = []
        self.video_widgets = []
        self.monitore = Monitor()
        self.monitore.load_model()

    def init_UI(self):
        self.setWindowTitle("SecureAI")
        self.setMinimumSize(800, 600)

        # Main layout
        self.main_layout = QHBoxLayout()

        self.right_layout = QVBoxLayout()

        self.video_link_input = QLineEdit()
        self.video_link_input.setPlaceholderText("Type your camera link or upload the video from the button below ")
        self.right_layout.addWidget(self.video_link_input)
        self.video_link_input.returnPressed.connect(self.upload_video_vie_link)

        self.add_video_button = QPushButton("Add videos", self)
        self.add_video_button.clicked.connect(self.upload_video_vie_button)
        self.right_layout.addWidget(self.add_video_button)

        self.scroll_area = QScrollArea(self)
        self.scroll_area_widget = QWidget()
        self.scroll_area.setWidget(self.scroll_area_widget)
        self.scroll_area.setWidgetResizable(True)

        self.grid_layout = QGridLayout(self.scroll_area_widget)

        self.right_layout.addWidget(self.scroll_area)

        self.main_layout.addLayout(self.right_layout)  # 80% space for the right panel


        self.setLayout(self.main_layout)
        self.setWindowTitle('Tracking App')


    def upload_video_vie_button(self):
        video_files, _ = QFileDialog.getOpenFileNames(self, "Open video file", '', "Video Files (*.mp4 *.avi *.mov)")
        if video_files:
            self.upload_video(video_files=video_files)
        
    def upload_video_vie_link(self):
        video_file = self.video_link_input.text()
        if video_file:
            self.upload_video(video_files=[video_file])
            self.video_link_input.clear()

    def upload_video(self, video_files):
        prev_len = len(self.cap)

        self.video_paths.extend(video_files)
        i = prev_len
        for  _, video in enumerate(self.video_paths[prev_len:]):

            self.cap.append(cv2.VideoCapture(video))
            self.cap.append(cv2.VideoCapture(video))
            self.cap.append(cv2.VideoCapture(video))

            if self.cap[-1].isOpened():
                frame_widget = VideoFrameWidget(self.monitore, True)
                row = len(self.video_widgets) // 3 
                col = len(self.video_widgets) % 3
                self.grid_layout.addWidget(frame_widget, row, col)
                self.video_widgets.append(frame_widget)

                frame_widget = VideoFrameWidget(self.monitore, False)

                row = len(self.video_widgets) // 3   
                col = len(self.video_widgets) % 3
                self.video_widgets.append(frame_widget)

                self.grid_layout.addWidget(frame_widget, row, col)


                frame_widget = VideoFrameWidget(self.monitore,False, track_plot=True)

                row = len(self.video_widgets) // 3   
                col = len(self.video_widgets) % 3
                self.video_widgets.append(frame_widget)

                self.grid_layout.addWidget(frame_widget, row, col)


                self.timers.append(QTimer())
                self.timers[-1].timeout.connect(lambda idx = i :self.update_frame(idx))
                self.timers[-1].start(30) 
            
            i += 3

                


    def update_frame(self, index):
        if self.cap[index] and self.cap[index].isOpened():
            ret, frame = self.cap[index].read()
            if ret:

                # Annotatio frame
                frame_widget = self.video_widgets[index]
                if frame_widget:
                    frame_widget.update_frame(frame)

                # Original frame
                frame_widget = self.video_widgets[index+1]
                if frame_widget:
                    frame_widget.update_frame(frame)

                # tracking frame
                frame_widget = self.video_widgets[index+2]
                if frame_widget:
                    frame_widget.update_frame(frame)
            else:
                self.timers[index].stop()
                self.cap[index].release()

    def closeEvent(self, event):
        if self.cap:
            for cap in self.cap:
                cap.release()
        event.accept()
