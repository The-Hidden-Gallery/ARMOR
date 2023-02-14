from typing import Dict, List, Any
from aruco.aruco import Aruco

from math import dist

class ArucoTracker():
    """ ArUco Tracker class. Constructor params:
        * max_frames_missing: Max number of consecutive frames that an Aruco can be missing before being deleted from register. (default: `3`)
        * max_distance: Max aruco distance to be detected as the same, in consecutive frames
    """

    def __init__(self, max_frames_missing: int = 5, max_distance: int = 5000) -> None:
        # Aruco register
        self._register = {}
        # Max consecutive frames missing
        self.MAX_FRAMES_MISSING = max_frames_missing
        # Max aruco distance to be detected as the same, in consecutive frames
        self.MAX_DISTANCE = max_distance

    def register(self) -> Dict:
        """ Returns the actual Aruco register. """
        return self._register

    def delete(self, uid: int) -> None: 
        """ Removes Aruco with the specified UID from register. Params:
            * uid: Unique ID of Aruco entity. 
        """
        try:
            # Removes aruco from register
            self._register.pop(uid)
        except KeyError:
            pass

    def registered_uids(self, ascending: bool = True) -> List[str]:
        """ Returns all the registered uids. """
        uids = list(self._register.keys())
        uids.sort() if ascending else uids.sort(reverse=True)
        return uids

    def _generate_new_uid(self, aruco: Aruco) -> str:
        """ Generates a uid for a new Aruco. 
        
        The UID is set based on three pieces of information: Aruco dictionary (A), Aruco ID (B) and a number nonce (C) -> dictAidB#C
        (Ex: `dict3id0#0` is the output for first aruco registered of dictionary 3 and ID 0. )
        """
        uids = self.registered_uids()
        uids = [uid for uid in uids if f"dict{aruco.dictionary}id{aruco.id}" in uid]
        if len(uids):
            # UID of Last Aruco added (same dictionary and ID)
            nonce = int(uids[-1].split("#")[1])+1
        else:
            # No Aruco with same dict and id is currently at register
            nonce = 0
        return f"dict{aruco.dictionary}id{aruco.id}#{nonce}" 

    def update(self, arucos: List[Aruco]) -> Dict[str, Any]:
        """ Updates the Tracker register with input list of Arucos. Params:
            * arucos: Array of Arucos. \n
            Returns the updated register entries."""
        updates = []
        # CASE A: No Aruco was recieved
        if not len(arucos):
            # Increases the count of frames missing for all registered arucos
            uids = self.registered_uids()
            for uid in uids:
                self._register[uid]["missing_frames"] += 1
                # If count number exceeds max that Aruco is deleted from register
                if self._register[uid]["missing_frames"] > self.MAX_FRAMES_MISSING:
                    self.delete(uid)
        else:
        # CASE B: Aruco list is not empty
            # CASE B_1: Register is empty
            if not len(self._register):
                # Registra los nuevos objetos detectados en este frame
                for aruco in arucos:
                    # Creates a new uid for Aruco
                    uid = self._generate_new_uid(aruco)
                    # Registers the auco
                    self._register[uid] = {"missing_frames": 0, "aruco": aruco}
                    updates.append((uid, aruco))
            # CASE B_2: Register is not empty
            else:
                # Gets a list of all registered Arucos
                uids = self.registered_uids()
                distances = [] # Appended as (distance,"i->uid")
                for i, aruco in enumerate(arucos):
                    for uid in uids:
                        # Checks if Arucos with same dict and id are registered
                        if uid.split("#")[0] == f"dict{aruco.dictionary}id{aruco.id}":
                            # Calculates the linear distance between the aruco recieved and the one registered 
                            distance = round(dist(aruco.center(),self._register[uid]["aruco"].center()),3)
                            distances.append([distance, f"{i}->{uid}"])
                # Ordering distances array (ascending)
                distances.sort(key=lambda x: x[0])
                # List of arucos pending to be updated or registered
                pending_arucos = arucos.copy()
                # List of UIDs updated
                updated_uids = []
                # Updates the registered with found arucos
                for distance in distances:
                    # Aruco is close enough
                    aruco = arucos[int(distance[1].split("->")[0])] # aruco 
                    uid = distance[1].split("->")[1] # uid of registered aruco
                    if aruco in pending_arucos and uid not in updated_uids and distance[0] <= self.MAX_DISTANCE: 
                        # Updates register
                        self._register[uid]["aruco"] = aruco
                        self._register[uid]["missing_frames"] = 0 # Reset count
                        # Deletes aruco from pending list
                        pending_arucos.remove(aruco)
                        updated_uids.append(uid)
                        updates.append((uid, aruco))
                # The arucos that have not been yet updated are registered as new ones
                for aruco in pending_arucos:
                    uid = self._generate_new_uid(aruco) # Creates a new uid for Aruco
                    # Registers the auco
                    self._register[uid] = {"missing_frames": 0, "aruco": aruco}
                    updates.append((uid, aruco))
                # Increases the count of not updated registers
                uids = self.registered_uids()
                for uid in uids:
                    if uid not in updated_uids:
                        self._register[uid]["missing_frames"] += 1
                        # If count number exceeds max that Aruco is deleted from register
                        if self._register[uid]["missing_frames"] > self.MAX_FRAMES_MISSING:
                            self.delete(uid)
        # Returns the updated register
        return updates