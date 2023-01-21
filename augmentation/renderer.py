import json
import os
import pathlib
from typing import Dict, List, Any

from aruco.aruco import Aruco
import augmentation.ar as ar
from augmentation.obj import OBJ

DEFAULT_OBJ = OBJ(os.path.join(str(pathlib.Path(__file__).parent.resolve()),"models","fox.obj")) # TODO: Change default OBJ

class Renderer(): 
    """ OBJ Render Controller. """

    def __init__(self, obj_map_path: str, preload: bool = True) -> None:
        # Gets OBJ map
        self._obj_map = self._read_obj_map(obj_map_path)
        # Preloading of all objs (optional)
        self.objs = {}
        if preload: 
            self._preload_OBJs()

    def load_OBJ(self, model: str, texture: str) -> OBJ:
        """ Loads a OBJ in Renderer. Args:
            * model: Name of OBJ file with extension (.obj)
            * texture: Name of texture file with extension (.png, .jpg, etc...)
            Returns the OBJ. 
        """
        # Gets model and texture paths
        model_path = os.path.join(str(pathlib.Path(__file__).parent.resolve()),"models",model)
        texture_path = os.path.join(str(pathlib.Path(__file__).parent.resolve()),"models",texture)
        # Checks if OBJ is already registered
        try:
            obj = self.objs[model] # OBJ already created and registered
            try:
                obj = self.objs[model][texture] # OBJ already created and registered
            except KeyError:
                # Create and register OBJ
                obj = OBJ(model_path,texture_path)
                self.objs[model][texture] = obj
        except KeyError:
            # Create and register OBJ
            obj = OBJ(model_path,texture_path)
            self.objs[model] = {texture: obj}
        return obj

    def _preload_OBJs(self) -> None:
        """ Preloads all OBJ. """
        # Iterate for all aruco dictionaries registered in obj map
        for dictionary in self._obj_map:
            # Iterate for all ids of registered dictionaries
            for id in self._obj_map[dictionary]:
                self.load_OBJ(self._obj_map[dictionary][id]["model"],self._obj_map[dictionary][id]["texture"]) # OBJ loading

    def _read_obj_map(self, obj_map_path: str) -> Dict[str, Dict[str, Dict[str, str]]]:
        """ Returns JSON OBJ map at indicated path as dict. """
        return json.load(open(obj_map_path))

    def get_aruco_OBJ(self, aruco: Aruco) -> OBJ:
        """ Returns the corresponding OBJ of an Aruco. """
        try:
            # Gets the corresponding model and texture of aruco
            model = self._obj_map[str(aruco.dictionary)][str(aruco.id)]["model"]
            texture = self._obj_map[str(aruco.dictionary)][str(aruco.id)]["texture"]
            try:
                # Gets the OBJ
                obj = self.objs[model][texture]
            except KeyError:
                # Loads the OBJ
                obj = self.load_OBJ(model,texture)
        except KeyError:
            # OBJ not found
            obj = DEFAULT_OBJ
        return obj

    def render(self, image: Any, arucos: List[Aruco]) -> None:
        """  TODO: Explanation. """
        for aruco in arucos: 
            # Gets the corresponding model and texture of aruco
            obj = self.get_aruco_OBJ(aruco)
            # OBJ augmentation
            ar.augment_aruco(image,aruco,obj)