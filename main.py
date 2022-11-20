# from configuration.configuration import Configuration
from aruco.aruco_detector import ArucoDetection
from camera.camera_controller import Camera
from augmentation.object import OBJ 
import augmentation.ar as ar

from typing import Tuple, List
import numpy as np

from math import dist

from time import time
import cv2

MOVING_AVERAGE = False

def furthest_point(obj: OBJ, flag: str = "XYZ"):
    max_distance = 0
    for face in obj.faces:
        points = face['points']
        for point in points:
            if flag == "XY":
                distance = dist(point[0:2],[0,0])
            elif flag == "XYZ":
                distance = dist(point[0:3],[0,0,0])
            if distance > max_distance:
                max_distance = distance
    return max_distance

def normalize_obj_points(obj):
    norm = furthest_point(obj)
    for i, face in enumerate(obj.faces):
        points = face['points']
        norm_points = []
        for point in points:
            norm_point = [coord/norm for coord in point]
            norm_points.append(norm_point)
        obj.faces[i]['points'] = norm_points
    return obj

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

    fox_obj_path = "C:\\Users\\egeah\\ArN-ethwork\\augmentation\\models\\fox.obj"
    fox_texture_path = "C:\\Users\\egeah\\ArN-ethwork\\augmentation\\models\\fox_texture.png"
    fox = OBJ(fox_obj_path,fox_texture_path)
    fox = normalize_obj_points(fox)

    cube_obj_path = "C:\\Users\\egeah\\ArN-ethwork\\augmentation\\models\\cube.obj"
    cube_texture_path = "C:\\Users\\egeah\\ArN-ethwork\\augmentation\\models\\cube_texture.png"
    cube = OBJ(cube_obj_path,cube_texture_path)
    cube = normalize_obj_points(cube)

    camera = Camera()

    rotations = {} # Initial rotations array

    rendered_objs = 0
    times = []

    while True:
        image = camera.get_frame()
        if image is not None: 
            # camera.show_image("camera",image)
            arucos = ArucoDetection.detect(image,marker_length=0.06)
            image = ArucoDetection.draw_detected_markers(image, arucos)
            for aruco in arucos:
                init_time = time() # Render Info
                # Moving average
                if MOVING_AVERAGE:
                    try:
                        av_rotation, _rotations = moving_average_rotation(aruco.rotation,rotations[aruco.id])
                    except KeyError:
                        av_rotation, _rotations = moving_average_rotation(aruco.rotation,[])
                    aruco.rotation = av_rotation
                    rotations[aruco.id] = _rotations
                # Aruco augmentation
                if aruco.dictionary == 3 and aruco.id == 5:
                    ar.augment_aruco(image,aruco,cube)
                else:
                    ar.augment_aruco(image,aruco,fox)
                end_time = time()
                times.append(time()-init_time)
            if len(times):
                avg_time_render_ms = 1000*sum(times)/(len(times))
                cv2.putText(image,f"Avg. ms/render: {round(avg_time_render_ms, 2)}",(10,50),fontFace=cv2.FONT_HERSHEY_SIMPLEX,fontScale=1,color=(0,0,0),thickness=2,lineType=cv2.LINE_AA)
                last_time_render_ms = 1000*(end_time-init_time)
                cv2.putText(image,f"Last. ms/render: {round(last_time_render_ms, 2)}",(10,100),fontFace=cv2.FONT_HERSHEY_SIMPLEX,fontScale=1,color=(0,0,0),thickness=2,lineType=cv2.LINE_AA)
            cv2.putText(image,f"Objs rendered: {len(times)}",(10,150),fontFace=cv2.FONT_HERSHEY_SIMPLEX,fontScale=1,color=(0,0,0),thickness=2,lineType=cv2.LINE_AA)
            camera.show_image("camera",image)
        