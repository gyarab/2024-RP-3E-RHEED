import cv2
import os

# Create a cache folder if it doesn't exist
cache_folder = "cacheimg"
os.makedirs(cache_folder, exist_ok=True)

# Load image from USB interface camera
cap = cv2.VideoCapture(0)
ret, frame = cap.read()

# Convert image to grayscale
gray_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

# Display the color image
cv2.imshow("Color Image", frame)
cv2.waitKey(0)

# Display the grayscale image
cv2.imshow("Grayscale Image", gray_frame)
cv2.waitKey(0)

# Save both color and grayscale images in the cache folder
cv2.imwrite(os.path.join(cache_folder, "color_image.jpg"), frame)
cv2.imwrite(os.path.join(cache_folder, "grayscale_image.jpg"), gray_frame)

# Release the camera and close all windows
cap.release()
cv2.destroyAllWindows()