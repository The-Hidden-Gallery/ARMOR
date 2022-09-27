from camera.camera_module import CameraModule
from camera.default import DefaultCamera
from camera.D435 import D435
from camera.L515 import L515, L515NotFoundError
from configuration.configuration import Configuration
import numpy

class Camera:
    """ Controller class for Board camera module. """

    def __init__(self) ->  None:
        model_name = Configuration.get_config_param('Camera','model')
        # Creates an instance of the correspondent simulation module
        self._module = self._get_module(model_name)

    def _get_module(self, model_name: str) -> CameraModule:
        """ Creates and returns an instance of the type of module specified"""
        # The camera module instance to create depends on the module name indicated
        if model_name == 'IRSL515':
            try:
                # Intel RS L515 camera module
                return L515()
            except L515NotFoundError:
                return DefaultCamera()
        elif model_name == 'IRSD435':
            # Intel RS D435 camera module
            return D435()
        else:
            # Default option 
            return DefaultCamera()
        
    def __del__(self) -> None:
        """ Interrupts the video capture. """

    def get_frame(self) -> numpy.ndarray:
        """ Reads the lastest frame from the video capture and returns it as a Numpy array. """
        # Indicates the module to get an image
        return self._module.get_frame()
    
    def show_image(self, disp_name: str, image: numpy.ndarray) -> None:
        """  Displays the indicated image. """
        # Indicates the module to show an image
        self._module.show_image(disp_name,image)

    def close_all_images(self) -> None:
        """ Closes all image show windows. """
        self._module.close_all_images()

    def close_image(self, disp_name: str) -> None:
        """ Closes the image window with the specified name. """
        self._module.close_image(disp_name)
