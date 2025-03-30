import silx.gui.qt as qt
import cv2

class CameraMenuWindow(qt.QMainWindow):
    def __init__(self):
        super().__init__()

        # Force the window not to fullscreen
        self.setWindowFlags(qt.Qt.Tool)
        self.setWindowTitle("Camera Setup and Launch")
        self.resize(600, 400)

        # Check if the camera_config.txt file is empty
        with open("camera_config.txt", "r") as f:
            if f.read() == "":
                # Save default config
                with open("camera_config.txt", "w") as f:
                    f.write(f"{24}\n")
                    f.write(f"{1}\n")
                    f.write(f"{0}\n")
                    f.write(f"{0}\n")
                    f.write(f"{0}\n")
                    f.write(f"{0}\n")
                    f.write(f"{0}\n")
                    f.write(f"{0}\n")
                    f.write(f"{0}\n")
                    f.write(f"{0}\n")
                    f.write(f"{0}\n")
                    f.write(f"{0}\n")
                    f.write(f"{0}\n")
                    f.write(f"{0}\n")
                    f.write(f"{0}\n")
                    f.write(f"{0}\n")
                    f.write(f"{0}\n")
                    f.write(f"{0}\n")
                    f.write(f"{0}\n")
                    f.write(f"{0}\n")
                    f.write(f"{0}\n")
                    f.write(f"{0}\n")
                    f.close()
        f.close()

        # Load the config values from the src/opencv_capture file
        self.config_values = self.load_config_values()

        # Create the main widget
        main_widget = qt.QWidget(self)
        self.setCentralWidget(main_widget)

        # Create layout
        layout = qt.QGridLayout()
        main_widget.setLayout(layout)

        # Create labels and input fields for each config value
        row = 0
        col = 0
        for field, value in self.config_values.items():
            label = qt.QLabel(field, self)
            layout.addWidget(label, row, col)

            input_field = qt.QLineEdit(str(value), self)
            layout.addWidget(input_field, row, col+1)

            if col == 2:
                col = 0
                row += 1
            else:
                col += 2

        # Create a button to save the updated config values
        save_button = qt.QPushButton("Save and Launch Camera", self)
        save_button.clicked.connect(self.save_config_values)
        layout.addWidget(save_button, row, col)

    def load_config_values(self):
        config_values = {}
        with open('camera_config.txt', 'r') as f:
            config_values["FPS"] = int(f.readline())
            config_values["Auto Exposure"] = int(f.readline())
            config_values["Exposure"] = int(f.readline())
            config_values["Gain"] = int(f.readline())
            config_values["Brightness"] = int(f.readline())
            config_values["Contrast"] = int(f.readline())
            config_values["Saturation"] = int(f.readline())
            config_values["Hue"] = int(f.readline())
            config_values["Sharpness"] = int(f.readline())
            config_values["Gamma"] = int(f.readline())
            config_values["White Balance Blue U"] = int(f.readline())
            config_values["Backlight"] = int(f.readline())
            config_values["Zoom"] = int(f.readline())
            config_values["Focus"] = int(f.readline())
            config_values["Autofocus"] = int(f.readline())
            config_values["WB Temperature"] = int(f.readline())
            config_values["FourCC"] = int(f.readline())
            config_values["Auto WB"] = int(f.readline())
            config_values["Temperature"] = int(f.readline())
            config_values["Trigger"] = int(f.readline())
            config_values["Trigger Delay"] = int(f.readline())
            config_values["Auto WB"] = int(f.readline())
            f.close()

        return config_values
    
    def save_config_values(self):
        config_values = self.config_values
        with open('camera_config.txt', 'w') as f:
            f.write(f"{config_values.get('FPS')}\n")
            f.write(f"{config_values.get('Auto Exposure')}\n")
            f.write(f"{config_values.get('Exposure')}\n")
            f.write(f"{config_values.get('Gain')}\n")
            f.write(f"{config_values.get('Brightness')}\n")
            f.write(f"{config_values.get('Contrast')}\n")
            f.write(f"{config_values.get('Saturation')}\n")
            f.write(f"{config_values.get('Hue')}\n")
            f.write(f"{config_values.get('Sharpness')}\n")
            f.write(f"{config_values.get('Gamma')}\n")
            f.write(f"{config_values.get('White Balance Blue U')}\n")
            f.write(f"{config_values.get('Backlight')}\n")
            f.write(f"{config_values.get('Zoom')}\n")
            f.write(f"{config_values.get('Focus')}\n")
            f.write(f"{config_values.get('Autofocus')}\n")
            f.write(f"{config_values.get('WB Temperature')}\n")
            f.write(f"{config_values.get('FourCC')}\n")
            f.write(f"{config_values.get('Auto WB')}\n")
            f.write(f"{config_values.get('Temperature')}\n")
            f.write(f"{config_values.get('Trigger')}\n")
            f.write(f"{config_values.get('Trigger Delay')}\n")
            f.write(f"{config_values.get('Auto WB')}\n")
            f.close()
        self.close()

        return config_values
