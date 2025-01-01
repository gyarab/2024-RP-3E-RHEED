from qtpy.QtWidgets import QVBoxLayout, QGraphicsScene, QGraphicsView
from qtpy.QtMultimediaWidgets import QVideoWidget
from qtpy.QtCore import QRectF


class VideoArea:
    def __init__(self):
        # Initialize video widget
        self.video_widget = QVideoWidget()
        self.video_widget.setMinimumSize(500, 300)
        self.video_widget.setStyleSheet("background-color: black;")
        self.video_widget.hide()

        # Initialize graphics scene and view
        self.scene = QGraphicsScene()
        self.graphics_view = QGraphicsView(self.scene)
        self.graphics_view.setSceneRect(QRectF(0, 0, 700, 500))
        self.graphics_view.setStyleSheet("background-color: gray;")

    def create_video_layout(self):
        # Create and return a layout for the video area
        video_layout = QVBoxLayout()
        video_layout.addWidget(self.video_widget)
        video_layout.addWidget(self.graphics_view)
        return video_layout
