import cv2
import os
import numpy
import h5py
import datetime
import silx.gui.qt as qt

class CameraInit:
    """Class for capturing frames from a camera and storing them in an h5 dataset."""
    def __init__(self, initial_size):
        self.frame_index = 0
        self.dataset_size = initial_size
        self.camera_port = 0
        self.on_resize = None

        # Check for a config file and load the camera port
        if os.path.exists("camera_config.txt"):
            with open("camera_config.txt", "r") as f:
                self.camera_port = int(f.readline())
                f.close()
        else:
            qt.QMessageBox.warning(None, "Camera Config Error", "Failed to load camera configuration. "+
                                    "Check if the camera_config.txt file exists. Always use Camera Setup and Launch menu to "+
                                    "configure the camera settings and launch the camera.")

        # Callback for resizing the dataset
        self.cache_folder = "cacheimg"
        os.makedirs(self.cache_folder, exist_ok=True)
        
        # Open the camera
        self.cap = cv2.VideoCapture(self.camera_port)
        if not self.cap.isOpened():
            qt.QMessageBox.warning(None, "Camera Error", "Failed to open camera. Check if it is connected."+
                                   " It may be caused by a wrong port configuration. For integrated camera "+
                                   "use 0, for virtual camera or external camera use 1 or higher. -1 is reserved for "+
                                   "automatic assignment but works only on certain OS. Check the Camera Setup and Launch"+
                                   " menu for more information.")
            return

        # Check for a config file
        if os.path.exists("camera_config.txt"):
            with open("camera_config.txt", "r") as f:
                self.camera_port = int(f.readline())
                self.cap.set(cv2.CAP_PROP_FPS, int(f.readline()))
                self.cap.set(cv2.CAP_PROP_AUTO_EXPOSURE, int(f.readline()))
                self.cap.set(cv2.CAP_PROP_EXPOSURE, int(f.readline()))
                self.cap.set(cv2.CAP_PROP_GAIN, int(f.readline()))
                self.cap.set(cv2.CAP_PROP_BRIGHTNESS, int(f.readline()))
                self.cap.set(cv2.CAP_PROP_CONTRAST, int(f.readline()))
                self.cap.set(cv2.CAP_PROP_SATURATION, int(f.readline()))
                self.cap.set(cv2.CAP_PROP_HUE, int(f.readline()))
                self.cap.set(cv2.CAP_PROP_SHARPNESS, int(f.readline()))
                self.cap.set(cv2.CAP_PROP_GAMMA, int(f.readline()))
                self.cap.set(cv2.CAP_PROP_WHITE_BALANCE_BLUE_U, int(f.readline()))
                self.cap.set(cv2.CAP_PROP_BACKLIGHT, int(f.readline()))
                self.cap.set(cv2.CAP_PROP_ZOOM, int(f.readline()))
                self.cap.set(cv2.CAP_PROP_FOCUS, int(f.readline()))
                self.cap.set(cv2.CAP_PROP_AUTOFOCUS, int(f.readline()))
                self.cap.set(cv2.CAP_PROP_WB_TEMPERATURE, int(f.readline()))
                self.cap.set(cv2.CAP_PROP_FOURCC, int(f.readline()))
                self.cap.set(cv2.CAP_PROP_AUTO_WB, int(f.readline()))
                self.cap.set(cv2.CAP_PROP_TEMPERATURE, int(f.readline()))
                self.cap.set(cv2.CAP_PROP_TRIGGER, int(f.readline()))
                self.cap.set(cv2.CAP_PROP_TRIGGER_DELAY, int(f.readline()))
                f.close()
        else:
            qt.messageQtMessageBox.warning(None, "Camera Config Error", "Failed to load camera configuration. "+
                                    "Check if the camera_config.txt file exists. Always use Camera Setup and Launch menu to "+
                                    "configure the camera settings and launch the camera.")
        
        # test frame capture and set the frame size
        ret, frame = self.cap.read()
        if not ret:
            qt.QMessageBox.warning(None, "Camera Error", "Failed to capture frame. Check if the camera is connected.")
            return
        
        # Convert to grayscale
        frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        height, width = frame.shape

        # Create a new h5 dataset
        self.h5_file = h5py.File(
            os.path.join(self.cache_folder, f"dataset_{datetime.datetime.now().strftime('%d-%m-%Y_%H-%M-%S')}.h5"), "w")

        # Preallocate initial dataset size
        self.image_dataset = self.h5_file.create_dataset(
            "arrays",
            shape=(self.dataset_size, height, width),
            maxshape=(None, height, width),
            dtype=numpy.float32,
            chunks=(10, height, width),
            )

    def capture_frame(self):
        """ Capture a frame from the camera and store it in the dataset. """
        ret, fr = self.cap.read()
        if not ret:
            print("Failed to capture frame.")
            return
        
        # Convert to grayscale
        fr = cv2.cvtColor(fr, cv2.COLOR_BGR2GRAY)
        
        #used 64bit float to normalize the image with high precision
        nfr = fr.astype(numpy.float32)
        #!!!normalization should be voluntary, implement later: cv2.normalize(fr, None, 0, 255, cv2.NORM_MINMAX, dtype=cv2.CV_64F)

        # If dataset is full, expand by 1000 frames
        if self.frame_index >= self.dataset_size:
            new_size = int(self.dataset_size + 1000)
            print(f"Resizing dataset from {self.dataset_size} to {new_size} frames...")
            self.image_dataset.resize(new_size, axis=0)
            self.dataset_size = new_size  # Update dataset size
            # Notify via the callback if set
            if self.on_resize is not None:
                self.on_resize(self.image_dataset)

        # Store frame
        self.image_dataset[self.frame_index] = nfr
        self.frame_index += 1

        return nfr

        # Display - not needed because it is replaced with direct connection to silx plot
        #display_img = (nfr / 255.0).astype(np.float32)
        #cv2.imshow("Grayscale Image", display_img)
        
        #if cv2.waitKey(1) & 0xFF == ord('q'):
        #    self.cleanup()

    def cleanup(self):
        self.cap.release()
        self.h5_file.close()
        cv2.destroyAllWindows()

    def getFPS(self):
        """ Returns the FPS setting of the camera. """
        return self.cap.get(cv2.CAP_PROP_FPS)
 
    def getCurrentFrame(self):
        """ Returns the current frame index. """
        return (self.frame_index-2)