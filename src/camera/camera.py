import cv2
import os
import numpy as np
import h5py
import datetime

class CameraInit:

    def __init__(self):
        self.cache_folder = "cacheimg"
        os.makedirs(self.cache_folder, exist_ok=True)
        self.cap = cv2.VideoCapture(0)
        self.h5_file = h5py.File(os.path.join(self.cache_folder, "array_"+datetime.datetime.now+".h5"), "w")
        self.image_dataset = self.h5_file.create_dataset("arrays", (1000, 840, 840), dtype=np.uint16)

        # Set the camera properties
        self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, 840)
        self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 840)
        self.cap.set(cv2.CAP_PROP_FPS, 1000)
        self.cap.set(cv2.CAP_PROP_AUTO_EXPOSURE, 0.25)
        self.cap.set(cv2.CAP_PROP_EXPOSURE, 0.01) #adjustable by a slider
        self.cap.set(cv2.CAP_PROP_AUTOFOCUS, 0)
        self.cap.set(cv2.CAP_PROP_FOCUS, 0) #adjustable by a slider
        self.cap.set(cv2.CAP_PROP_AUTO_WB, 0)
        self.cap.set(cv2.CAP_PROP_WB_TEMPERATURE, 4500) #adjustable by a slider
        self.cap.set(cv2.CAP_PROP_BRIGHTNESS, 150)
        self.cap.set(cv2.CAP_PROP_CONTRAST, 50)
        self.cap.set(cv2.CAP_PROP_SATURATION, 50)
        self.cap.set(cv2.CAP_PROP_GAIN, 0)

        i = 1

        while i <= 1000:
            ret, frame = self.cap.read()

            # Convert image to grayscale
            fr = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

            # Normalize the brightness of the image
            nfr = cv2.normalize(fr, None, 0, 1.0, cv2.NORM_MINMAX, dtype=cv2.CV_64F)
            
            # Display the grayscale image
            cv2.imshow("Grayscale Image", nfr)
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break

            #cv2.imwrite(os.path.join(cache_folder, "gs_"+str(i)+".jpg"), np.uint16(nfr*255))
            self.image_dataset[i-1] = np.uint16(nfr*255)
            i += 1