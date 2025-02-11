import pyPOACamera
import numpy as np
import cv2
import time

class PlayerOneCamera:
    def __init__(self):

        self.camera_id = None
        self.camera_opened = False

        self.image_format = pyPOACamera.POAImgFormat.POA_RAW16
        self.image_size = (3008, 3008)
        self.gain = 0
        self.offset = 0
        self.integration_time = 1000

        self.red = 100
        self.green = 100
        self.blue = 100

        self.binning = 1


    def initialize_camera(self) -> None:
        """
        Initializes the camera by finding and opening the first available camera.
        """
        camera_count = pyPOACamera.GetCameraCount()
        if camera_count < 1:
            raise RuntimeError("No cameras found.")

        error, camera_properties = pyPOACamera.GetCameraProperties(0)
        if error != pyPOACamera.POAErrors.POA_OK:
            raise RuntimeError("Failed to get camera properties.")

        self.camera_id = camera_properties.cameraID

        error = pyPOACamera.OpenCamera(self.camera_id)
        if error != pyPOACamera.POAErrors.POA_OK:
            raise RuntimeError("Failed to open the camera.")

        error = pyPOACamera.InitCamera(self.camera_id)
        if error != pyPOACamera.POAErrors.POA_OK:
            raise RuntimeError("Failed to initialize the camera.")

        self.camera_opened = True

    def _configure_camera(self) -> None:

        if not self.camera_opened:
            raise RuntimeError("Camera not initialized.")
        
        # Nevim jestli je tohle ten nejlepsi zpusob jak to udelat
        config = [
            (lambda: pyPOACamera.SetImageFormat(self.camera_id, self.image_format), "Image format"),
            (lambda: pyPOACamera.SetImageSize(self.camera_id, self.image_size[0], self.image_size[1]), "Image size"),
            (lambda: pyPOACamera.SetGain(self.camera_id, self.gain, False), "Gain"),
            (lambda: pyPOACamera.SetConfig(self.camera_id, pyPOACamera.POAConfig.POA_OFFSET, self.offset, False), "Offset"),
            (lambda: pyPOACamera.SetConfig(self.camera_id, pyPOACamera.POAConfig.POA_WB_R, self.red, False), "White balance red"),
            (lambda: pyPOACamera.SetConfig(self.camera_id, pyPOACamera.POAConfig.POA_WB_G, self.green, False), "White balance green"),
            (lambda: pyPOACamera.SetConfig(self.camera_id, pyPOACamera.POAConfig.POA_WB_B, self.blue, False), "White balance blue"),
            (lambda: pyPOACamera.SetImageBin(self.camera_id, self.binning), "Binning"),
            (lambda: pyPOACamera.SetExp(self.camera_id, self.integration_time, False), "Integration time"),
        ]
        
        for setting,tag in config:
            error = setting()
            if error != pyPOACamera.POAErrors.POA_OK:
                raise RuntimeError(f"Failed to configure {tag}")


    def close_camera(self) -> None:

        if self.camera_opened:
            pyPOACamera.CloseCamera(self.camera_id)
            self.camera_opened = False

    def capture_image(self) -> np.ndarray:
        """
        Captures a single image from the camera.
        Returns:
            numpy.ndarray: Captured image.
        """

        self._configure_camera()

        if not self.camera_opened:
            raise RuntimeError("Camera not initialized.")

        pyPOACamera.StartExposure(self.camera_id, True)

        while True:
            error, camera_state = pyPOACamera.GetCameraState(self.camera_id)
            if camera_state == pyPOACamera.POACameraState.STATE_OPENED:
                break

        error, is_ready = pyPOACamera.ImageReady(self.camera_id)
        if not is_ready:
            raise RuntimeError("Image not ready.")

        error, image = pyPOACamera.GetImage(self.camera_id, 1000)
        if error != pyPOACamera.POAErrors.POA_OK:
            raise RuntimeError("Failed to capture image.")

        return image

    def capture_video(self,output_file, duration=10) -> None:

        self._configure_camera()

        if not self.camera_opened:
            raise RuntimeError("Camera not initialized.")

        pyPOACamera.StartExposure(self.camera_id, False)

        width, height = pyPOACamera.GetImageSize(self.camera_id)[1:]
        img_size = pyPOACamera.ImageCalcSize(height, width, pyPOACamera.POAImgFormat.POA_RAW8)
        buffer = np.zeros(img_size, dtype=np.uint8)

        start_time = time.time()
        with open(output_file, "wb") as f:
            while time.time() - start_time < duration:
                error, is_ready = pyPOACamera.ImageReady(self.camera_id)
                if is_ready:
                    pyPOACamera.GetImageData(self.camera_id, buffer, 1000)
                    f.write(buffer)

        pyPOACamera.StopExposure(self.camera_id)



