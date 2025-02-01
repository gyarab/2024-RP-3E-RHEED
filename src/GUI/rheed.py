from qtpy.QtWidgets import (
    QMainWindow, QVBoxLayout, QHBoxLayout, QWidget,
    QPushButton, QGroupBox, QGraphicsEllipseItem, QGraphicsRectItem, QLabel, QSlider
)
from qtpy.QtCore import Qt, QRectF, QTimer
from qtpy.QtGui import QBrush, QColor, QPen
from GUI.shape_item import CustomShapeItem, CustomEllipseItem
from GUI.video_area import VideoArea
from camera.camera_util import CameraInit


class Rheed(QMainWindow):
    
    def __init__(self):
        self.WIDTH = 720
        self.HEIGHT = 1280
        self.DATASET_BATCH_SIZE = 1000

        super().__init__()
        self.setWindowTitle("Rheed Application")
        self.setGeometry(100, 100, 1200, 800)  # WindowSize

        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        main_layout = QHBoxLayout(central_widget)

        # Video/Camera Controls
        left_toolbar = self.create_left_toolbar()
        main_layout.addLayout(left_toolbar, stretch=1)

        # Video/Live Feed + shapes
        self.video_area = VideoArea()  # Use the separated VideoArea class
        main_layout.addLayout(self.video_area.create_video_layout(), stretch=3)

        # Graph + Buttons
        self.right_sidebar = self.create_right_sidebar()
        main_layout.addLayout(self.right_sidebar, stretch=2)

        # Variables initialization
        self.scene_shapes = []
        self.used_color_indices = []  # No color-repeating
        self.color_palette = [
            ("Red", QColor(255, 0, 0)),
            ("Green", QColor(0, 255, 0)),
            ("Blue", QColor(0, 0, 255)),
            ("Yellow", QColor(255, 255, 0)),
            ("Cyan", QColor(0, 255, 255)),
            ("Magenta", QColor(255, 0, 255)),
            ("White", QColor(255, 255, 255)),
            ("Black", QColor(0, 0, 0)),
            ("Purple", QColor(128, 0, 128)),
        ]

    def create_left_toolbar(self):
        self.left_layout = QVBoxLayout()

        # Camera buttons
        buttons = [
            ("Init Camera Stream", self.init_camera),
            ("Stop Camera Stream", self.stop_camera),
            ("STOP", self.stop_video),
            ("Load Video", self.load_video),
            ("Play Video", self.play_video),
            ("Pause Video", self.pause_video),
        ]

        for text, func in buttons:
            button = QPushButton(text)
            button.clicked.connect(func)
            self.left_layout.addWidget(button)

        # ShapeEditor
        self.shape_editor = QGroupBox("Shape Editor")
        self.shape_editor_layout = QVBoxLayout(self.shape_editor)

        # Diameter
        self.diameter_slider = self.create_slider("Diameter", 50, 300, self.update_shape_diameter)
        self.shape_editor_layout.addLayout(self.diameter_slider)

        # Angle
        self.angle_slider = self.create_slider("Angle", 0, 360, self.update_shape_angle)
        self.shape_editor_layout.addLayout(self.angle_slider)

        # Rectangle Width
        self.width_slider = self.create_slider("Width", 50, 300, self.update_rectangle_width)
        self.shape_editor_layout.addLayout(self.width_slider)

        # Rectangle Height
        self.height_slider = self.create_slider("Height", 50, 300, self.update_rectangle_height)
        self.shape_editor_layout.addLayout(self.height_slider)


        # Adding to layout
        self.shape_editor.hide()
        self.left_layout.addWidget(self.shape_editor)

        self.left_layout.addStretch()
        return self.left_layout

    def create_right_sidebar(self):
        right_layout = QVBoxLayout()

        # Graph
        self.graph_area = QLabel("Graph Display Area")
        self.graph_area.setStyleSheet("background-color: white; border: 1px solid black;")
        self.graph_area.setFixedHeight(200)
        right_layout.addWidget(self.graph_area)

        # "New" Button
        self.new_button = QPushButton("New")
        self.new_button.clicked.connect(self.add_new_rectangle)
        right_layout.addWidget(self.new_button)

        self.shape_menu_container = QVBoxLayout()
        right_layout.addLayout(self.shape_menu_container)

        right_layout.addStretch()
        return right_layout

    def add_new_rectangle(self):
        # Rectangle creation
        color_name, color_value = self.get_unique_random_color()
        x, y = 50, 50  # Default position
        width, height = 100, 50  # Default size

        # Non-stacking rectangles
        while self.is_position_occupied(x, y, width, height):
            x += 120
            if x + width > self.video_area.graphics_view.width():
                x = 50
                y += 70

        rect_item = CustomShapeItem(QRectF(x, y, width, height), color_value, self)
        rect_item.setData(0, color_name)

        self.video_area.scene.addItem(rect_item)
        self.scene_shapes.append(rect_item)
        self.add_shape_menu(color_name, color_value, rect_item)

    def add_shape_menu(self, color_name, color_value, shape_item):
        shape_menu = QHBoxLayout()

        color_box = QLabel()
        color_box.setFixedSize(20, 20)
        color_box.setStyleSheet(f"background-color: {color_value.name()}; border: 1px solid black;")

        analyze_button = QPushButton("Analyze")
        analyze_button.clicked.connect(lambda: self.open_analyze_window(color_name))

        shape_menu.addWidget(color_box)
        shape_menu.addWidget(QLabel(f"{color_name}"))
        shape_menu.addWidget(analyze_button)
        self.shape_menu_container.addLayout(shape_menu)


    def open_analyze_window(self, color_name):
        # New window pop-up
        self.analyze_window = QWidget()
        self.analyze_window.setWindowTitle(f"Graph Analysis for {color_name}")
        self.analyze_window.setGeometry(200, 200, 600, 400)

        layout = QVBoxLayout(self.analyze_window)
        graph_label = QLabel(f"Graph for Shape: {color_name}")
        graph_label.setStyleSheet("background-color: white; border: 1px solid black;")
        layout.addWidget(graph_label)

        self.analyze_window.show()

    def convert_to_rectangle(self, shape_item):

        current_rect = shape_item.sceneBoundingRect()
        
        self.video_area.scene.removeItem(shape_item)

        new_rectangle = CustomShapeItem(QRectF(current_rect), shape_item.color, self)
        new_rectangle.setBrush(QBrush(QColor(shape_item.color)))
        new_rectangle.setPen(QPen(Qt.black, 2))
        new_rectangle.setFlags(QGraphicsRectItem.ItemIsMovable | QGraphicsRectItem.ItemIsSelectable)

        self.video_area.scene.addItem(new_rectangle)

        if shape_item in self.scene_shapes:
            self.scene_shapes.remove(shape_item)
        self.scene_shapes.append(new_rectangle)

        self.selected_shape = new_rectangle
        self.shape_editor.show()
        self.show_rectangle_sliders()

    def convert_to_kruhova(self, shape_item):
        current_rect = shape_item.sceneBoundingRect()

        self.video_area.scene.removeItem(shape_item)

        new_ellipse = QGraphicsEllipseItem(current_rect)
        new_ellipse.setBrush(QBrush(QColor(shape_item.color)))
        new_ellipse.setPen(QPen(Qt.black, 2))
        new_ellipse.setStartAngle(0)
        new_ellipse.setSpanAngle(90 * 16)
        new_ellipse.setFlags(QGraphicsEllipseItem.ItemIsMovable | QGraphicsEllipseItem.ItemIsSelectable)
        new_ellipse = CustomEllipseItem(current_rect, shape_item.color, self)
        self.video_area.scene.addItem(new_ellipse)

        self.scene_shapes.remove(shape_item)
        self.scene_shapes.append(new_ellipse)

        self.selected_shape = new_ellipse
        self.shape_editor.show()
        self.show_kruhova_sliders()


    def delete_shape(self, shape_item):
        if shape_item in self.scene_shapes:
            self.video_area.scene.removeItem(shape_item)
            self.scene_shapes.remove(shape_item)

    def show_rectangle_sliders(self):
        # Show width and height sliders, hide diameter and angle sliders
        self.width_slider.itemAt(0).widget().show()
        self.width_slider.itemAt(1).widget().show()
        self.height_slider.itemAt(0).widget().show()
        self.height_slider.itemAt(1).widget().show()

        self.diameter_slider.itemAt(0).widget().hide()
        self.diameter_slider.itemAt(1).widget().hide()
        self.angle_slider.itemAt(0).widget().hide()
        self.angle_slider.itemAt(1).widget().hide()

    def show_kruhova_sliders(self):
        # Opposite of previous
        self.diameter_slider.itemAt(0).widget().show()
        self.diameter_slider.itemAt(1).widget().show()
        self.angle_slider.itemAt(0).widget().show()
        self.angle_slider.itemAt(1).widget().show()

        self.width_slider.itemAt(0).widget().hide()
        self.width_slider.itemAt(1).widget().hide()
        self.height_slider.itemAt(0).widget().hide()
        self.height_slider.itemAt(1).widget().hide()


    def get_unique_random_color(self):
        # Unique color
        available_colors = [
            (name, color) for idx, (name, color) in enumerate(self.color_palette)
            if idx not in self.used_color_indices
        ]

        if not available_colors:  # Reset if all used
            self.used_color_indices.clear()
            available_colors = self.color_palette

        color_name, color_value = available_colors[0]
        self.used_color_indices.append(self.color_palette.index((color_name, color_value)))
        return color_name, color_value

    def is_position_occupied(self, x, y, width=100, height=50):
        for shape in self.scene_shapes:
            shape_rect = shape.sceneBoundingRect()
            if (
                x < shape_rect.right() and x + width > shape_rect.left() and
                y < shape_rect.bottom() and y + height > shape_rect.top()
            ):
                return True  # Overlap detected
        return False

    def create_slider(self, label_text, min_value, max_value, callback):
        layout = QVBoxLayout()
        label = QLabel(f"{label_text}: {min_value}")
        slider = QSlider(Qt.Horizontal)
        slider.setRange(min_value, max_value)
        slider.valueChanged.connect(lambda value: self.update_slider_label(label, label_text, value))
        slider.valueChanged.connect(callback)
        layout.addWidget(label)
        layout.addWidget(slider)
        return layout

    def update_slider_label(self, label, text, value):
        # Value update
        label.setText(f"{text}: {value}")

    def update_shape_diameter(self, value):
        if self.selected_shape:
            rect = self.selected_shape.rect()
            center = rect.center()
            new_rect = QRectF(center.x() - value / 2, center.y() - value / 2, value, value)
            self.selected_shape.setRect(new_rect)

    def update_shape_angle(self, value):
        if self.selected_shape:
            self.selected_shape.setSpanAngle(value * 16)

    def update_rectangle_width(self, value):
        if isinstance(self.selected_shape, CustomShapeItem):
            rect = self.selected_shape.rect()
            new_rect = QRectF(rect.x(), rect.y(), value, rect.height())
            self.selected_shape.setRect(new_rect)

    def update_rectangle_height(self, value):
        if isinstance(self.selected_shape, CustomShapeItem):
            rect = self.selected_shape.rect()
            new_rect = QRectF(rect.x(), rect.y(), rect.width(), value)
            self.selected_shape.setRect(new_rect)

    def init_camera(self):
        print("Camera Stream Initialized.")
        self.camera_instance = CameraInit(self.WIDTH, self.HEIGHT, self.DATASET_BATCH_SIZE)

        self.video_timer = QTimer(self)
        self.video_timer.timeout.connect(self.camera_instance.capture_frame)
        self.video_timer.start(30)  # ~30 FPS

    def stop_camera(self):
        print("Camera Stream Stopped.")
        if self.video_timer:
            self.video_timer.stop()
        if self.camera_instance:
            self.camera_instance.cleanup()
    
    #placeholder functions
    def load_video(self): print("Load Video.")
    def stop_video(self): print("Video Stopped.")
    def play_video(self): print("Video Playing.")
    def pause_video(self): print("Video Paused.")
