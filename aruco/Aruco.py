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