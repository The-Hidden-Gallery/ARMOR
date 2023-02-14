import cv2
from typing import List, Tuple 

class Aruco:
    '''OpenCV ArUco markers class.'''

    def __init__(self, corners: List[Tuple[float, float]], rotation: float, translation: float, dictionary: cv2.aruco_Dictionary, id: int) -> None:
        # List of coordinates (x, y) of the aruco marker
        self.corners = corners
        # Aruco rotation vector
        self.rotation = rotation
        # Aruco translation vector
        self.translation = translation
        # Dictionary of Arcuo (ej:cv2.aruco.DICT_4X4_50)
        self.dictionary = dictionary
        # Aruco id (ej: 0, 1, 2...)
        self._id = id

    @property
    def id(self) -> int:
        return self._id
    
    @id.setter
    def id(self, int) -> None:
        self._id = int

    def center(self) -> Tuple[int,int]:
        """ Returns the estimation of the center of aruco. Args:
            * `aruco_corners`: List of Aruco's corners
        """
        x_coords = [corner[0] for corner in self.corners]
        y_coords = [corner[1] for corner in self.corners]
        # Center as diference between max and min value
        x_center = (max(x_coords)+min(x_coords))/2
        y_center = (max(y_coords)+min(y_coords))/2
        return [x_center, y_center]