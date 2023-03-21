import json
import os
import pathlib
from typing import Dict, List, Any, Tuple
import glob

from aruco.aruco import Aruco
import augmentation.ar as ar
from augmentation.obj import OBJ

from augmentation.aruco_tracker import ArucoTracker

DEFAULT_OBJ = OBJ(os.path.join(str(pathlib.Path(__file__).parent.resolve()),"models","default.obj"),os.path.join(str(pathlib.Path(__file__).parent.resolve()),"models","default.png")) # TODO: Change default OBJ

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
        # Frozen flag -> if True all animations are frozen
        self.frozen = False

    def load_OBJ(self, model: str, animation: str = "default", texture: str = None) -> None:
        """ Loads a OBJ in Renderer. Args:
            * model: Name of parent folder
            * animation: Folder containing .obj files
            * texture: Name of texture file with extension (.png, .jpg, etc...) located in animation folder
        """
        # Gets animation and texture paths
        animation_path = os.path.join(str(pathlib.Path(__file__).parent.resolve()),"models",model,animation)
        texture_path = os.path.join(animation_path,texture) if texture is not None else None
        # For each .obj file in parent folder
        for frame, obj_path in enumerate(glob.glob(os.path.join(animation_path,"*.obj"))):
            # Checks if OBJ is already registered
            if model in self.objs:
                if animation in self.objs[model]:
                    if texture in self.objs[model][animation]:
                        if len(self.objs[model][animation][texture]) < frame:
                            # Adds the new frame to the textured animation of model
                            self.objs[model][animation][texture].append(OBJ(obj_path,texture_path))
                    else:
                        # Create OBJ and regist texture in animation
                        self.objs[model][animation][texture] = [OBJ(obj_path,texture_path)]
                else:
                    # Create OBJ and regist animation in model
                    self.objs[model][animation] = {texture: [OBJ(obj_path,texture_path)]}
            else:
                # Create OBJ and regist model
                self.objs[model] = {animation: {texture: [OBJ(obj_path,texture_path)]}}

    def _preload_OBJs(self) -> None:
        """ Preloads all OBJ. """
        # Iterates for all aruco dictionaries registered in obj map
        for dictionary in self._obj_map:
            # Iterates for all ids of registered dictionaries
            ids = self._obj_map[dictionary]
            for id in ids:
                model = self._obj_map[dictionary][id]["model"] if "model" in self._obj_map[dictionary][id] else None
                if model is not None: 
                    # OBJ Animation
                    animation = self._obj_map[dictionary][id]["animation"] if "animation" in self._obj_map[dictionary][id] else "default"
                    # OBJ Texture
                    texture = self._obj_map[dictionary][id]["texture"] if "texture" in self._obj_map[dictionary][id] else None
                    # OBJ loading
                    self.load_OBJ(model,animation=animation,texture=texture) 

    def _read_obj_map(self, obj_map_path: str) -> Dict[str, Dict[str, Dict[str, str]]]:
        """ Returns JSON OBJ map at indicated path as dict. """
        return json.load(open(obj_map_path))

    def get_aruco_active_animation(self, uid: str) -> str:
        """ Returns the active animation name (str) of the Aruco with given UID. Params:
            * uid : unique ID of aruco. Format: 'dict{dictionary}id{Aruco id}#{nonce}' 
        """ 
        if uid in self.register:
            try:
                # Active animation
                return self.register[uid]["animation"]
            except KeyError:
                # No active animation
                self.set_active_animation(uid,"default")

    def set_active_animation(self, uid: str, animation: str) -> None:
        """ Sets the indicated active animation of Aruco with given UID. Params:
            * uid: unique ID of aruco. Format: 'dict{dictionary}id{Aruco id}#{nonce}' 
            * animation: name tag of new active animation
        """
        if uid in self.register:
            self.register[uid]["animation"] = animation
            # Resets frame count
            self.register[uid]["frame"] = 0

    def get_aruco_OBJ(self, uid: str) -> OBJ:
        """ Returns the corresponding OBJ of Aruco with input UID. Params:
            * uid: unique ID of aruco. Format: 'dict{dictionary}id{Aruco id}#{nonce}' 
        """
        # Gets aruco info from uid
        dictionary = uid.split("id")[0].replace("dict","")
        id = uid.split("id")[1].split("#")[0]
        # Gets current animation
        animation = self.get_aruco_active_animation(uid)
        # Gets obj frame 
        try:
            # Object frame number
            frame = self.register[uid]["frame"]
        except KeyError:
            # UID not registered
            frame = 0
        # OBJ
        try:
            # Model
            model = self._obj_map[dictionary][id]["model"]
            # Gets the texture
            texture = self._obj_map[dictionary][id]["texture"] if "texture" in self._obj_map[dictionary][id] else None
            # Gets the corresponding OBJ
            try:
                obj = self.objs[model][animation][texture][frame]
            except KeyError:
                # OBJ not previously loaded -> Loads the OBJ
                self.load_OBJ(model,animation,texture)
                obj = self.objs[model][animation][texture][frame]
            if not self.frozen:
                # Updates frame count
                self.register[uid]["frame"] = frame + 1 if frame < len(self.objs[model][animation][texture])-1 else 0
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
        # Updates the renderer register
        for (uid, aruco) in updates:
            if uid not in self.register:
                self.register[uid] = {"animation": "default", "frame": 0}
        return updates

    def render(self, image: Any, arucos: List[Aruco]) -> None:
        """  TODO: Explanation. """
        # Updates register
        updates = self.update_register(arucos)
        for (uid, aruco) in updates:
            # Gets corresponding OBJ
            obj = self.get_aruco_OBJ(uid)
            # OBJ augmentation
            ar.augment_aruco(image,aruco,obj)

    def freeze(self) -> None:
        """ Freezes or Unfreezes current animations. """
        self.frozen = not self.frozen