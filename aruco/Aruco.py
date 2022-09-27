import cv2
from typing import List, Tuple 

class Aruco:
    '''OpenCV ArUco markers class.'''

    def __init__(self, corners: List[Tuple[float, float]], rotation: float, translation: float, dictionary: cv2.aruco_Dictionary, id: int) -> None:
        # List of coordinates (x, y) of the aruco marker
        self._corners = corners
        # Aruco rotation vector
        self._rotation = rotation
        # Aruco translation vector
        self._translation = translation
        # Dictionary of Arcuo (ej:cv2.aruco.DICT_4X4_50)
        self._dictionary = dictionary
        # Aruco id (ej: 0, 1, 2...)
        self._id = id

    @property
    def corners(self) -> List[Tuple[float, float]]:
        return self._corners

    @corners.setter
    def corners(self, corners: List[Tuple[float, float]]) -> None:
        self._corners = corners

    @property
    def rotation(self) -> float:
        return self._rotation

    @rotation.setter
    def rotation(self, rotation: float) -> None:
        self._rotation = rotation

    @property
    def translation(self) -> float:
        return self._translation

    @translation.setter
    def translation(self, translation: float) -> None:
        self._translation = translation

    @property
    def dictionary(self) -> cv2.aruco_Dictionary:
        return self._dictionary

    @dictionary.setter
    def dictionary(self, dictionary: cv2.aruco_Dictionary) -> None:
        self._dictionary = dictionary

    @property
    def id(self) -> int:
        return self._id
    
    @id.setter
    def id(self, int) -> None:
        self._id = int