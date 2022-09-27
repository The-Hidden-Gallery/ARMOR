from configuration.configuration import Configuration
from aruco.aruco_detector import ArucoDetection
from camera.camera_controller import Camera
import cv2

if __name__ == "__main__":
    camera = Camera()

    while True:
        image = camera.get_frame()
        if image is not None: 
            # camera.show_image("camera",image)
            arucos = ArucoDetection.detect(image)
            output = ArucoDetection.draw(image, arucos)
            if arucos:  
                camera.show_image("camera",output)
            else:
                camera.show_image("camera",image)