import csv
from ctypes.wintypes import COLORREF
import sys
import numpy as np
import cv2
import os
from PIL import Image
from typing import List, Tuple
from aruco.aruco import Aruco

NUM_ID_CANDIDATES = 100
ARUCO_PX_DIMS = 300
BORDER_BITS = 3
N_ANGLE_MARKS = 19

OPT_IMAGE_WIDTH = 640
OPT_IMAGE_HEIGHT = 480

DICTIONARIES = set()
# DICTIONARIES.add(cv2.aruco.DICT_4X4_50)
# DICTIONARIES.add(cv2.aruco.DICT_4X4_100)
# DICTIONARIES.add(cv2.aruco.DICT_4X4_250)
DICTIONARIES.add(cv2.aruco.DICT_4X4_1000)
# DICTIONARIES.add(cv2.aruco.DICT_5X5_50)
# DICTIONARIES.add(cv2.aruco.DICT_5X5_100)
# DICTIONARIES.add(cv2.aruco.DICT_5X5_250)
DICTIONARIES.add(cv2.aruco.DICT_5X5_1000)
# DICTIONARIES.add(cv2.aruco.DICT_6X6_50)
# DICTIONARIES.add(cv2.aruco.DICT_6X6_100)
# DICTIONARIES.add(cv2.aruco.DICT_6X6_250)
DICTIONARIES.add(cv2.aruco.DICT_6X6_1000)
# DICTIONARIES.add(cv2.aruco.DICT_7X7_50)
# DICTIONARIES.add(cv2.aruco.DICT_7X7_100)
# DICTIONARIES.add(cv2.aruco.DICT_7X7_250)
DICTIONARIES.add(cv2.aruco.DICT_7X7_1000)

MATRIX_COEFFICIENTS = np.array([[1367.14, 0, 973.89], [0, 1368.28, 526.45], [0, 0, 1]])

class ArucoDetection():
    """ Aruco detector class."""

    @staticmethod
    def detect(image: np.ndarray, dictionaries: List[cv2.aruco_Dictionary] = None, marker_length: float = 0.02, matrix_coefficients: List[Tuple[float, float, float]] = MATRIX_COEFFICIENTS, distortion_coefficients: Tuple[float, float, float, float, float] = np.zeros((1, 5)), optimized: bool = False) -> List[Aruco]:
        """ 
            Performs an Aruco detection on input image, and returns the markers found from the different dictionaries indicated. Params:
            * image: Input image
            * dictionaries: Arcuo dictionaries to detect. If `None` then it runs for all posible dictionaries
            * marker_length: Aproximate length of physical Aruco marker in meters
            * matrix_coefficients: Matrix of Camera coefficients. If `None` then uses default `MATRIX_COEFFICIENTS` value (not recomended)
            * distortion_coefficients: Distorsion coefficients array, by default all values are set to zero. 
            * optimized: Optimizes the aruco detection by reducing input image and rescaling the output detected markers locations. 
        """
        # Aruco array initialization
        arucos = []
        # Checks predefined dictionaries 
        if not dictionaries: 
            dictionaries = DICTIONARIES
        # Creates aruco params
        if dictionaries:
            aruco_params = cv2.aruco.DetectorParameters_create()
        if optimized:
            # Reduces input image resolution
            height, width, _ = image.shape
            resize_factor = 1.0
            if height > OPT_IMAGE_HEIGHT and width > OPT_IMAGE_WIDTH:
                resize_factor = min(OPT_IMAGE_HEIGHT/height, OPT_IMAGE_WIDTH/width)
                image = cv2.resize(image, (0, 0), fx=resize_factor, fy=resize_factor)
        # Iterates for each aruco dictionary
        for dictionary in dictionaries:
            aruco_dict = cv2.aruco.Dictionary_get(dictionary)
            # Detection of all arucos in the image
            (aruco_corners, aruco_ids, rejected) = cv2.aruco.detectMarkers(image, aruco_dict, parameters=aruco_params)
            if optimized:
                aruco_corners = [corner/resize_factor for corner in aruco_corners]
            for i in range(0,len(aruco_corners)):
                # Estimation of each marker pose
                rotation, translation, markerpoints = cv2.aruco.estimatePoseSingleMarkers(aruco_corners[i], marker_length, matrix_coefficients, distortion_coefficients)
                arucos.append(Aruco(aruco_corners[i][0], rotation[0][0], translation[0][0], dictionary, aruco_ids[i][0]))
        return arucos

    @staticmethod
    def draw_detected_markers(image: np.ndarray, arucos: List[Aruco], marker_length: float = 0.02, matrix_coefficients: List[Tuple[float, float, float]] = MATRIX_COEFFICIENTS, distortion_coefficients: Tuple[float, float, float, float, float] = np.zeros((1, 5)), draw_bounds: bool = True, draw_axis: bool = True, draw_ids: bool = True) -> np.ndarray:
        """ Draws a representation of the detected information of the edges and axes of each ArUco marker.
            * Draws an enclosing rectangle fitted to the boundaries of each marker. (`draw_bounds` must be `True`)
            * Draws the x,y,z set of vectors is drawn on each markers's surfaces. (`draw_axis` must be `True`)
        """
        # Copies the image
        output_image = image.copy()
        for aruco in arucos:
            if draw_bounds:
                # Draws an enclosing rectangle fitted to the markers boundaries
                output_image = cv2.aruco.drawDetectedMarkers(output_image, [np.array([aruco.corners])], np.array([aruco.id])) if draw_ids else cv2.aruco.drawDetectedMarkers(output_image, [np.array([aruco.corners])])
            if draw_axis:
                # Draws the axis of the x,y,z set vectors on markers's surfaces
                output_image = cv2.aruco.drawAxis(output_image, matrix_coefficients, distortion_coefficients, aruco.rotation, aruco.translation, marker_length/2)
        return output_image

    @staticmethod
    def generate_markers(num_markers, markers_name):
        '''
        Generate markers. Check previous markers already generated by reading
        a '.csv'. Update the '.csv' with IDs already used. Save markers as
        '.png'

        Parameters:

        num_markers: (int) markers to be generated
        '''

        # Extract the ids already used and generate a vector with id candidates
        marker_ids = Aruco._extract_ids()
        id_candiates = np.arange(NUM_ID_CANDIDATES)

        for i in range(num_markers):

            # Extract the values in id_candiates that are not in marker_ids
            difference_ids = np.setdiff1d(id_candiates, marker_ids)
            new_id = difference_ids[0]

            # Create the ArUco marker
            canvas = np.zeros((ARUCO_PX_DIMS, ARUCO_PX_DIMS, 1), dtype="uint8")
            cv2.aruco.drawMarker(Aruco.DICT, new_id,
                                 ARUCO_PX_DIMS, canvas, BORDER_BITS)

            # Add white border (so the detector can detect 4 corners)
            yellow = [255, 255, 255]
            canvas = cv2.copyMakeBorder(
                canvas, 50, 50, 50, 50, cv2.BORDER_CONSTANT, value=yellow)

            # Show and save the marker
            if not os.path.exists(sys.path[0] + '\\' + markers_name):
                os.makedirs(sys.path[0] + '\\' + markers_name)
            marker_file_name = sys.path[0] + '\\' + markers_name + \
                '\\' + markers_name + '_Point_' + str(i+1) + '.png'
            cv2.imwrite(marker_file_name, canvas)
            cv2.imshow("ArUCo Marker", canvas)
            cv2.waitKey(0)

            marker_ids.append(new_id)

        Aruco._update_ids(marker_ids, markers_name)

    @staticmethod
    def _detect(image, matrix_flag, distortion_flag, display=False):
        '''
        Show graphic info from ArUco Marker

        Parameters:

        - image
        - matrix_flag (Bool): In case camera matrix is available
        - distortion_flag (Bool): In case distortion coefficients are available
        '''

        matrix_coefficients = np.zeros((3, 3))
        distortion_coefficients = np.zeros((1, 5))

        height, width = image.shape[:2]

        # Custom camera matrix
        if matrix_flag:
            matrix_coefficients[0] = [1367.14, 0, 973.89]
            matrix_coefficients[1] = [0, 1368.28, 526.45]
            matrix_coefficients[2] = [0, 0, 1]

        # Custom distortion coefficients
        if distortion_flag:
            distortion_coefficients[0][0] = 0
            distortion_coefficients[0][1] = 0
            distortion_coefficients[0][2] = 0
            distortion_coefficients[0][3] = 0
            distortion_coefficients[0][4] = 0

        # BGR to Gray
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

        # Marker detection parameters
        arucoParams = cv2.aruco.DetectorParameters_create()

        # Detection
        if matrix_flag or distortion_flag:
        # if matrix_flag or distortion_flag:
            corners, ids, rejected_img_points = cv2.aruco.detectMarkers(gray, Aruco.DICT, parameters=arucoParams,cameraMatrix=matrix_coefficients, distCoeff=distortion_coefficients)
        else:
            corners, ids, rejected_img_points = cv2.aruco.detectMarkers(
                image, Aruco.DICT, parameters=arucoParams)

        # Determine names for ids
        Point_name = []
        if np.all(ids is not None):
            for i in range(0, len(ids)):
                Point_name.append(Aruco._extract_name(ids[i]))

        # Determine the center and the name of each aruco
        if np.all(ids is not None):
            # Determine centers of each Aruco
            pm = []
            for i in range(0, len(ids)):
                pm_1 = (corners[i][0][0] + corners[i][0][2])/2
                pm_2 = (corners[i][0][1] + corners[i][0][3])/2
                pm.append((pm_1 + pm_2)/2)

        # Iterate in markers
        rvec = []
        tvec = []
        # If there are markers found by detector
        if np.all(ids is not None) and display:
            markerPoints = []
            for i in range(0, len(ids)):
                # Estimate pose of each marker and return the values rvec (rotation) and tvec (translation)
                rvec_tmp, tvec_tmp, markerPoints_tmp = cv2.aruco.estimatePoseSingleMarkers(
                    corners[i], 0.02, matrix_coefficients, distortion_coefficients)
                rvec.append(rvec_tmp)
                tvec.append(tvec_tmp)
                markerPoints.append(markerPoints_tmp)

            # Draw A square around the markers
            for i in range(0, len(ids)):
                try:
                    mark_color = Aruco.COLORS[ids[i][0]]
                except IndexError:
                    mark_color = (150,150,150)
                aruco_contour = np.array([(int(corners[i][0][j][0]),int(corners[i][0][j][1])) for j in range(0,4)])
                cv2.drawContours(image,[aruco_contour],0,mark_color,thickness=4)

            # # Draw Axis
            # for i in range(0, len(ids)):
            #     cv2.aruco.drawAxis(image, matrix_coefficients,
            #                        distortion_coefficients, rvec[i], tvec[i], 0.01)
            
            # Draw Point name
            for i in range(0, len(ids)):
                txt_mrg_x = 9*len(Point_name[i]) # Text x margin
                corners_y_coords = [int(corners[i][0][j][1]) for j in range(0,len(corners[0][0]))]
                height = max(corners_y_coords) - min(corners_y_coords) # Height
                txt_mrg_y = 8*int(image.shape[1]/image.shape[0]) + int(height/2) # Text y margin
                org = (int(pm[i][0])-txt_mrg_x,int(pm[i][1])-txt_mrg_y)
                name = Point_name[i]
                font = cv2.FONT_HERSHEY_SIMPLEX
                fontScale = 1
                try:
                    mark_color = Aruco.COLORS[ids[i][0]]
                except IndexError:
                    mark_color = (150,150,150)
                thickness = 2
                image = cv2.putText(image, name, org, font, fontScale, mark_color, thickness, cv2.LINE_AA)
        if display:
            return corners, ids, Point_name, image, tvec
        else:
            return corners, ids, Point_name

    @staticmethod
    def _extract_ids() -> list:
        '''
        Return an array with the IDs in the '.csv'
        '''

        # Gets the path of angle mark ids CVS file
        angle_marks_csv_path = f"{sys.path[0]}\\angle_marks.cvs"
        marker_ids = []
        try:
            with open(angle_marks_csv_path, 'r') as csv_file:
                reader = csv.reader(csv_file)
                for i, row in enumerate(reader):
                    if i == 0:
                        # Header
                        pass
                    else:
                        try: 
                            marker_ids.append(int(row[0][0]))
                        except IndexError:
                            pass
        except NameError:
            print('Marker ID not found')

        return marker_ids

    @staticmethod
    def _extract_name(marker_id):
        '''
        Return an string with the Point vinculated to an IDs in the '.csv'
        '''

        # Gets the path of angle mark ids CVS file
        angle_marks_csv_path = f"{sys.path[0]}\\angle_marks.csv"
        name = 'NA'
        try:
            with open(angle_marks_csv_path, 'r') as csv_file:
                reader = csv.reader(csv_file)
                for i, row in enumerate(reader):
                    if i == marker_id + 1:
                        full_row = row[0]
                        name = full_row.split("-")[1:][0]
        except NameError:
            print('Marker ID not found')

        return name

    @staticmethod
    def _update_ids(marker_ids, markers_name):
        '''
        Update the '.csv' with IDs
        '''
        # Gets the path of angle mark ids CVS file
        angle_marks_csv_path = f"{sys.path[0]}\\angle_marks.cvs"
        try:
            with open(angle_marks_csv_path) as f:
                lines = sum(1 for line in f)
        except:
            lines = 0

        with open(angle_marks_csv_path, 'a', newline='') as file:
            writer = csv.writer(file)
            if lines == 0:
                writer.writerow(["ID"])
                for i in range(lines, len(marker_ids)):
                    writer.writerow(
                        [str(marker_ids[i]) + '-' + markers_name + '_Point_' + str(i+1)])
            else:
                for i in range(lines-1, len(marker_ids)):
                    writer.writerow(
                        [str(marker_ids[i]) + '-' + markers_name +
                         '_Point_' + str(i + 1 - (lines - 1))])

    @staticmethod
    def white_bg_square(img):
        "return a white-background-color image having the img in exact center"
        size = (max(img.size),)*2
        layer = Image.new('RGB', size, (255, 255, 255))
        layer.paste(img, tuple(
            map(lambda x: (x[0]-x[1])/2, zip(size, img.size))))
        return layer

    @staticmethod
    def augment_aruco(bbox: List[Tuple], image: np.ndarray, aug_image: np.ndarray) -> np.ndarray:
        """ Places an augmented image on the surface of each detected aruco and returns the marked image."""
        # Creates a copy of the image proportioned
        image_copy = image.copy()
        # Sets each of the image corners from aruco's bounding box
        top_left = (int(bbox[0][0][0]),int(bbox[0][0][1]))
        top_right = (int(bbox[0][1][0]),int(bbox[0][1][1]))
        bottom_right = (int(bbox[0][2][0]),int(bbox[0][2][1]))
        bottom_left = (int(bbox[0][3][0]),int(bbox[0][3][1]))
        # Gets the augment image dimension
        h, w, _ = aug_image.shape
        # Creates a vector with the corners cordinates (destination pts)
        aruco_pts = np.array([top_left,top_right,bottom_right,bottom_left])
        # Creates the augment image corner's array (source pts)
        aug_image_pts = np.float32([[0,0],[w,0],[w,h],[0,h]])
        # Calculates thehomography matrix between both array points
        matrix, _ = cv2.findHomography(aug_image_pts,aruco_pts)
        # Applies the perspective transformation to an image
        marked_image = cv2.warpPerspective(aug_image,matrix,(image.shape[1],image.shape[0]))
        # Draws a black convex polygon on the aruco surface
        cv2.fillConvexPoly(image_copy,aruco_pts.astype(int),(0,0,0))
        # Overlaps the marked image with the original one
        marked_image += image_copy
        # Returns the image with the aug image
        return marked_image
