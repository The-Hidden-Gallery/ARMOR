# from configuration.configuration import Configuration
from aruco.aruco_detector import ArucoDetection
from camera.camera_controller import Camera
from augmentation.renderer import Renderer

from typing import Tuple, List
import numpy as np

from time import time
import cv2

from augmentation.aruco_tracker import ArucoTracker 

MOVING_AVERAGE = False

def moving_average_rotation(latest_rotation: Tuple[int, int, int], rotations: List[Tuple[int, int, int]], length: int = 5) -> Tuple[Tuple[int, int, int], List[Tuple[int, int, int]]]:
    """ Performs the moving average of Aruco rotation. Args: 
        * `latest_rotation`: Last aruco rotation value.
        * `rotations`: Array of last array rotations
        * `length`: Target length of rotations array.
        Returns moving average rotation value of marker and updated rotation array
    """
    # Adds latest value
    rotations.append(latest_rotation)
    # Takes only the last length values
    if len(rotations) > length: 
        rotations = rotations[-length:]
    # Calculates the average
    avg_rx = sum([rotation[0] for rotation in rotations])/len(rotations) # X rotation
    avg_ry = sum([rotation[1] for rotation in rotations])/len(rotations) # Y rotation
    avg_rz = sum([rotation[2] for rotation in rotations])/len(rotations) # Z rotation
    return np.array([avg_rx, avg_ry, avg_rz]), rotations


if __name__ == "__main__":

    obj_map_path = "C:\\Users\\egeah\\ArN-ethwork\\augmentation\\objs.json"
    renderer = Renderer(obj_map_path,preload=False)
    print("[ARN-Ethwork]: OBJs loaded")

    camera = Camera()
    print("[ARN-Ethwork]: Camera ON")

    # rotations = {} # Initial rotations array

    tracker = ArucoTracker()

    resize_factor = 4

    while True:

        frame_time = time()

        image = camera.get_frame()

        if image is not None: 
            
            # arucos = ArucoDetection.detect(image,marker_length=0.06)
            arucos = ArucoDetection.detect(image,dictionaries=[3],marker_length=0.06,optimized=True)

            if arucos:
                image = ArucoDetection.draw_detected_markers(image, arucos)

                renderer.render(image,arucos)

                try:
                    cv2.putText(image, f"Frame rate:{round(1/(time()-frame_time),0)}",(10,40),fontFace=cv2.FONT_HERSHEY_SIMPLEX,fontScale=1,color=(0,255,255),thickness=2,lineType=cv2.LINE_AA)
                except ZeroDivisionError:
                    pass

                if cv2.waitKey(1) & 0xFF == ord('l'):
                    renderer.set_active_animation("dict3id15#0","launch")
                    print("Launching...")

                elif cv2.waitKey(1) & 0xFF == ord('r'):
                    renderer.set_active_animation("dict3id15#0","default")
                    print("Default")

                elif cv2.waitKey(1) & 0xFF == ord('f'):
                    print("Freeze")
                    renderer.freeze()

            image = cv2.resize(image, (0, 0), fx=3/4, fy=3/4)
            camera.show_image("camera",image)