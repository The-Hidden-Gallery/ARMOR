from abc import ABC, abstractmethod

class CameraModule(ABC):
    """ Abstract camera module class (superclass in Camera Module hierarchy). This class provides abstract method definitions 
        for implementation in each camera subclass, regardless of the camera hardware model used in Board. """

    @abstractmethod
    def get_frame(self) -> None:
        """ Gets and returns a frame from camera."""
        pass

    @abstractmethod
    def show_image(self) -> None:
        """ Displays an image."""
        pass

    @abstractmethod
    def close_all_images(self) -> None:
        """ Closes all image show windows. """
        pass

    @abstractmethod
    def close_image(self) -> None:
        """ Closes the image window with the specified name. """
        pass
