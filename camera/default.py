from camera.camera_module import CameraModule
from configuration.configuration import Configuration
import cv2
import numpy
# import screeninfo

class VideoCaptureError(Exception):
    """ Video capture configuration failed """

class VideoDeviceNotFoundError(Exception):
    """ Video device not found."""

class DefaultCamera(CameraModule):
    """ OpenCV2 default videocapture module class. Subclass of CameraModule. """

    def __init__(self) -> None:
        """ Camera initialization. Gets the video source and sets a video capture. """
        super().__init__()
        # Sets the VideoCapture
        try: 
            # Video source setting
            self._source = int(Configuration.get_config_param("Camera","source"))
            self._videoCapture = cv2.VideoCapture(self._source)
            # self._screen = screeninfo.get_monitors()[self._source]
            # Gets the camera resolution parameters
            width_res = int(Configuration.get_config_param("Camera","width"))
            height_res = int(Configuration.get_config_param("Camera","height"))
            # Sets the resolution of display
            self._videoCapture.set(cv2.CAP_PROP_FRAME_WIDTH,width_res)
            self._videoCapture.set(cv2.CAP_PROP_FRAME_HEIGHT,height_res)
            # Check whether the video capture was opened correctly
            if self._videoCapture.isOpened():
                print("[Camera Module]:  Found video device.")
            else:
                raise VideoDeviceNotFoundError
        except:
            raise VideoCaptureError

    def __del__(self) -> None:
        """ Interrupts the video capture. """
        # Closes all image windows
        self.close_all_images()
        # Interrupts the video capture
        self._videoCapture.release()
        print("[Camera Module]:  Closed video device.")

    def get_frame(self) -> numpy.ndarray:
        """ Reads the lastest frame from the video capture and returns it as a Numpy array. """
        # Gets the frame
        retval, frame = self._videoCapture.read()
        # Returns image
        return frame
    
    def show_image(self, disp_name: str, image: numpy.ndarray) -> None:
        """  Displays the image given using cv2 module. """
        # Display the resulting frame
        cv2.imshow(disp_name,image)
        # cv2.moveWindow(disp_name,int(self._screen.x/2)-1,int(self._screen.y/2)-1)
        cv2.waitKey(1) # Waits 1ms

    def close_all_images(self) -> None:
        """ Closes all image show windows. """
        # Closes all image windows
        cv2.destroyAllWindows()

    def close_image(self, disp_name: str) -> None:
        """ Closes the image window with the specified name. """
        # Closes all image windows
        cv2.destroyWindow(disp_name)