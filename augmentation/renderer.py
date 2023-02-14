import json
import os
import pathlib
from typing import Dict, List, Any, Tuple
import glob

from aruco.aruco import Aruco
import augmentation.ar as ar
from augmentation.obj import OBJ

from augmentation.aruco_tracker import ArucoTracker

from time import time
import cv2

DEFAULT_OBJ = OBJ(os.path.join(str(pathlib.Path(__file__).parent.resolve()),"models","default","default.obj"),os.path.join(str(pathlib.Path(__file__).parent.resolve()),"models","default","default.png")) # TODO: Change default OBJ

class Renderer(): 
    """ OBJ Render Controller. """

    def __init__(self, obj_map_path: str, preload: bool = True, tracker: bool = True) -> None:
        # Gets OBJ map
        self._obj_map = self._read_obj_map(obj_map_path)
        # Preloading of all objs (optional)
        self.objs = {}
        if preload: 
            self._preload_OBJs()
        # Creates aruco register
        self.register = {}
        # Aruco tracker
        self.tracker = ArucoTracker() if tracker else None

    def load_OBJ(self, model: str, texture: str = None) -> None:
        """ Loads a OBJ in Renderer. Args:
            * model: Name of folder containing .obj files
            * texture: Name of texture file with extension (.png, .jpg, etc...), located at `model` folder
            If `texture` tag is set to "untextured" OBj will be loaded without texture
            Returns the OBJ. 
        """
        # Gets model and texture paths
        model_path = os.path.join(str(pathlib.Path(__file__).parent.resolve()),"models",model)
        texture_path = os.path.join(str(pathlib.Path(__file__).parent.resolve()),"models",model,texture) if texture is not None else None
        # For each .obj file in parent folder
        for frame, obj_path in enumerate(glob.glob(os.path.join(model_path,"*.obj"))):
            # Checks if OBJ is already registered
            try:
                obj = self.objs[model] # OBJ already created and registered
                try:
                    obj = self.objs[model][texture][frame] # OBJ already created and registered
                except KeyError:
                    # Create and register OBJ
                    obj = OBJ(obj_path,texture_path)
                    self.objs[model][texture].append(obj)
                except IndexError:
                    # Create OBJ and register new model frame
                    obj = OBJ(obj_path,texture_path)
                    self.objs[model][texture].append(obj)
            except KeyError:
                # Create and register OBJ
                obj = OBJ(obj_path,texture_path)
                self.objs[model] = {texture: [obj]}

    def _preload_OBJs(self) -> None:
        """ Preloads all OBJ. """
        # Iterate for all aruco dictionaries registered in obj map
        for dictionary in self._obj_map:
            # Iterate for all ids of registered dictionaries
            for id in self._obj_map[dictionary]:
                try:
                    # Standard OBJ loading
                    self.load_OBJ(self._obj_map[dictionary][id]["model"],self._obj_map[dictionary][id]["texture"]) 
                except KeyError:
                    # OBJ with no texture declared
                    self.load_OBJ(self._obj_map[dictionary][id]["model"],None) 

    def _read_obj_map(self, obj_map_path: str) -> Dict[str, Dict[str, Dict[str, str]]]:
        """ Returns JSON OBJ map at indicated path as dict. """
        return json.load(open(obj_map_path))

    def get_OBJ(self, uid: str) -> OBJ:
        """ Returns the corresponding OBJ of Aruco with input UID. Params:
            * uid: unique ID of aruco. Format: 'dict{dictionary}id{Aruco id}#{nonce}' 
        """
        # Gets aruco info from uid
        dictionary = uid.split("id")[0].replace("dict","")
        id = uid.split("id")[1].split("#")[0]
        try:
            # Object frame number
            frame = self.register[uid]
        except KeyError:
            # UID not registered
            frame = 0
        # OBJ
        try:
            # Gets the model (if exists)
            model = self._obj_map[dictionary][id]["model"]
            # Gets the texture (if exists)
            try:
                texture = self._obj_map[dictionary][id]["texture"]
            except KeyError:
                # OBJ has no texture
                texture = None 
            # Gets the corresponding OBJ
            try:
                obj = self.objs[model][texture][frame]
            except KeyError:
                # OBJ not previously loaded -> Loads the OBJ
                obj = self.load_OBJ(model,texture)
            # Updates frame count
            self.register[uid] = frame + 1 if frame < len(self.objs[model][texture])-1 else 0
        except KeyError:
            # OBJ model not found -> Using default OBJ
            obj = DEFAULT_OBJ
        return obj

    def update_register(self, arucos: List[Aruco]) -> List[Tuple[str,Aruco]]:
        """ Recieves a list of arucos and updates the register. Params:
            * arucos: Array of Arucos.\n
        Returns updated register entries (list). 
        """
        if self.tracker:
            # Gets the tracked updates
            updates = self.tracker.update(arucos)
        else:
            # No tracker
            updates = [(f"dict{aruco.dictionary}id{aruco.id}#0", aruco) for aruco in arucos]
        return updates

    def render(self, image: Any, arucos: List[Aruco]) -> None:
        """  TODO: Explanation. """
        # Updates register
        updates = self.update_register(arucos)
        times = [] # TODO: Remove after debug
        for (uid, aruco) in updates:
            # Gets corresponding OBJ
            obj = self.get_OBJ(uid)
            # OBJ augmentation
            subaugment_time = ar.augment_aruco(image,aruco,obj)[1]
        if len(times):
            avg_render_time = 1000*sum(times)/(len(times))
            # cv2.putText(image,f"Avg. ms/render: {round(avg_render_time, 2)}",(10,40),fontFace=cv2.FONT_HERSHEY_SIMPLEX,fontScale=1,color=(0,255,255),thickness=2,lineType=cv2.LINE_AA)
            # cv2.putText(image,f"Total Render (ms): {round(1000*sum(times), 2)}",(10,80),fontFace=cv2.FONT_HERSHEY_SIMPLEX,fontScale=1,color=(0,255,255),thickness=2,lineType=cv2.LINE_AA)