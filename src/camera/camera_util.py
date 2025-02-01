import cv2
import os
import numpy as np
import h5py
import datetime

class CameraInit:
    def __init__(self, width, height, initial_size):
        self.width = width
        self.height = height
        self.frame_index = 0
        self.dataset_size = initial_size  # Initial allocation size
        
        self.cache_folder = "cacheimg"
        os.makedirs(self.cache_folder, exist_ok=True)
        
        self.cap = cv2.VideoCapture(0)
        if not self.cap.isOpened():
            print("Failed to open camera.")
            return
        
        self.h5_file = h5py.File(
            os.path.join(self.cache_folder, f"dataset_{datetime.datetime.now().strftime('%d-%m-%Y_%H-%M-%S')}.h5"), "w")

        # **Preallocate initial dataset size**
        self.image_dataset = self.h5_file.create_dataset(
            "arrays",
            shape=(self.dataset_size, self.width, self.height),  # Preallocate space
            maxshape=(None, self.width, self.height),  # Allow unlimited frames
            dtype=np.uint16,
            chunks=(10, self.width, self.height)  # Optimize for batch writing
        )

    def capture_frame(self):
        ret, frame = self.cap.read()
        if not ret:
            print("Failed to capture frame.")
            return

        fr = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

        #used 64bit float to normalize the image with high precision
        nfr = cv2.normalize(fr, None, 0, 255, cv2.NORM_MINMAX, dtype=cv2.CV_64F)

        # **If dataset is full, expand by 50%**
        if self.frame_index >= self.dataset_size:
            new_size = int(self.dataset_size * 1.5)  # Expand by 50%
            print(f"Resizing dataset from {self.dataset_size} to {new_size} frames...")
            self.image_dataset.resize(new_size, axis=0)
            self.dataset_size = new_size  # Update dataset size

        # Store frame
        self.image_dataset[self.frame_index] = nfr
        self.frame_index += 1

        # Display
        display_img = (nfr / 255.0).astype(np.float32)
        cv2.imshow("Grayscale Image", display_img)
        
        if cv2.waitKey(1) & 0xFF == ord('q'):
            self.cleanup()

    def cleanup(self):
        print(f"Saved {self.frame_index} frames.")
        self.cap.release()
        self.h5_file.close()
        cv2.destroyAllWindows()
