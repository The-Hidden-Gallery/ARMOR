import cv2
import numpy as np
from configuration.configuration import Configuration
from camera.camera_module import CameraModule
import pyrealsense2 as rs2
# import screeninfo

D435_WIDTH = 1280
D435_HEIGHT = 720
FRAMERATE = 30

class D435NotFoundError(Exception):
    """ No D435 camera device was found."""

class D435(CameraModule):
    """ IntelRealsense© camera module class for D435 model. Subclass of CameraModule. """

    def __init__(self):
        """ Camera initial configuration and pipeline creation. """
        super().__init__()
        # Video source setting
        self._source = int(Configuration.get_config_param("Camera","source"))
        # Selects the output screen monitor
        self._screen = screeninfo.get_monitors()[self._source]
        # Checks if a D435 Camera is connected
        try:
            # Creates a interactive instance to communicate with the camera
            self._pipeline = rs2.pipeline()
            # Gets the default configuration for pipelines
            self._config = rs2.config()
            # Sets the stream type, camera resolution and format
            self._config.enable_stream(rs2.stream.color, D435_WIDTH, D435_HEIGHT, rs2.format.bgr8, FRAMERATE)
            # Starts the pipeline streaming with the configuration added
            self._pipeline.start(self._config)
        except RuntimeError:
            # Raises a D435 not found error
            raise D435NotFoundError

    def __del__(self) -> None:
        """ Deletes the camera instance and stops the pipeline streaming."""
        try:
            # Stops the pipeline streaming
            self._pipeline.stop()
        except RuntimeError:
            pass

    def get_frame(self) -> np.ndarray:
        """ Reads the lastest frame from the D435 camera and returns it as a Numpy array. """
        # Waits until there is a frame in the pipeline
        got = True
        while got:
            try:
                frame = self._pipeline.wait_for_frames()
                got = False
            except RuntimeError:
                got = True
        # Extract color frame 
        color_frame = frame.get_color_frame()
        # Converts the color frame to a numpy array
        color_frame = np.asanyarray(color_frame.get_data())
        # Returns the color frame
        return color_frame
    
    def show_image(self, disp_name: str, image: np.ndarray) -> None:
        """  Displays in a new window named as indicated the image given. """
        # Shows the resulting frame
        cv2.imshow(disp_name,image)
        cv2.moveWindow(disp_name,int(self._screen.x/2)-1,int(self._screen.y/2)-1)
        cv2.waitKey(1) # Waits 1ms

    def close_all_images(self) -> None:
        """ Closes all image show windows. """
        # Closes all image windows
        cv2.destroyAllWindows()

    def close_image(self, disp_name: str) -> None:
        """ Closes the image window with the specified name. """
        # Closes all image windows
        cv2.destroyWindow(disp_name)