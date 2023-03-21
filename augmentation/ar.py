# v0 - calculates the homography from scratch at each step
import cv2
import numpy as np
import augmentation.aruco_module as aruco
from augmentation.obj import OBJ 
from aruco.aruco import Aruco
from math import dist, sqrt

from typing import Tuple, List

DEFAULT_COLOR = (158, 5, 81)

def augment_aruco(image: np.array, aruco: Aruco, obj: OBJ, scale: int = 1) -> np.array:
	""" Projects an Augmented Reality OBJ on the Aruco surface in the image. Args:
		* `image`: Input image to augment 
		* `aruco`: Intance of detected ArUco (Aruco Class)
		* `obj`: Intance of 3D OBJ model to augment.
		* `resize`: Resize factor (1 by default to adjust aruco bounds)

		Returns the image with augmented 3D model.
	"""
	aruco_center = aruco.center()
	aruco_center.append(0) # Adds z
	extrinsic_matrix = np.identity(3) # Camera effects already taken into account in aruco rotation estimation
	# Calculates the intricics matrix
	intrinsic_matrix = compose_intrisic_matrix(aruco.rotation,aruco_center)
	# Calculates the projection matrix
	projection_matrix = compose_projection_matrix(extrinsic_matrix,intrinsic_matrix)
	faces_points = []
	faces_colors = []
	autoscale_factor = calculate_autoscale_factor(aruco.corners)
	# Checks if obj has image or mtl texture
	mtl = hasattr(obj,'materials')
	for face in obj.faces:
		points = np.array(face['points'], dtype=float)
		# Resizing
		points = resize_object(points,scale*autoscale_factor)
		# Projection
		points = np.array([project_3d_point(point,projection_matrix) for point in points])
		# Appends projected face points
		faces_points.append(points)
		try:
			if mtl:
				# Gets the material color (diffuse color) #TODO: Explore new ways to get a more aprox color
				color = obj.materials[face['material']]['diffuse_color']
			else:
				vertices_colors = face['colors']
				# Gets the average value of each BRG
				average_blue = sum([vertices_colors[i][0] for i in range(0,len(face["colors"]))])/len(face["colors"])
				average_green = sum([vertices_colors[i][1] for i in range(0,len(face["colors"]))])/len(face["colors"])
				average_red = sum([vertices_colors[i][2] for i in range(0,len(face["colors"]))])/len(face["colors"])
				# Face color as the sum of each average BRG coord
				color = [int(average_blue), int(average_green), int(average_red)]
		except KeyError:
			color = DEFAULT_COLOR # Face color not defined
		faces_colors.append(color)
	# Orders obj faces from nearest to furthest
	reference_point = project_3d_point([0,0,0],projection_matrix)[0]
	reference_point = [0,0,0]
	# reference_point = [aruco_center[0],aruco_center[1],1000]
	faces_points, faces_colors = order_faces(reference_point,faces_points,faces_colors)
	faces_points = _remove_z_coords(faces_points)
	# Draws obj faces
	[cv2.fillConvexPoly(image, np.int32(face_points), faces_colors[i]) for i,face_points in enumerate(faces_points)]
	# for i,face_points in enumerate(faces_points):
	# 	cv2.fillConvexPoly(image, np.int32(face_points), faces_colors[i])
	# 	cv2.imshow("camera",image)
	# 	cv2.waitKey(1000)
	return image

def project_3d_point(point: List[Tuple[int, int, int]], projection_matrix: List[Tuple[int, int, int]]) -> List[Tuple[int, int]]:
	""" TODO: Include description."""
	# Extended point coordinates: from (x,y,z) to (x,y,z,1) to fit the projection matrix product
	ext_point = np.append(np.array(point),1)
	# Proyected point
	projected_point = np.array([np.dot(projection_matrix,ext_point)])
	return projected_point 

def compose_intrisic_matrix(rotation_vectors: List[Tuple[int,int,int]], translation_vector: Tuple[int,int,int]) -> List[Tuple[int,int,int]]:
	""" Combines the rotation and translation vectors to generate the intrisic matrix of augmentation object. Args:
		* `rotation`: Input image to augment 
		* `translation_vector`: tranlation vector (xyz offset)

		Returns a 3x4 matrix with the following structure:
		
		rot11 rot12 rot13 trx \n
		rot11 rot12 rot13 try \n
		rot11 rot12 rot13 trz
	"""
	intrinsic_matrix = []
	rotation_vectors = np.array([rotation_vectors[0],rotation_vectors[1],rotation_vectors[2]])
	# Converts the 1x3 rotation vector into a 3x3 rotation matrix using Rodriges Jacobian function
	rotation_matrix = cv2.Rodrigues(rotation_vectors)[0]
	for i in range(0,3):
		intrinsic_matrix.append([rotation_matrix[i][0], rotation_matrix[i][1], rotation_matrix[i][2], translation_vector[i]])
	return intrinsic_matrix

def compose_projection_matrix(extrinsic_matrix: List[Tuple[int,int,int]], intrinsic_matrix: List[Tuple[int,int,int]]) -> List[Tuple[int,int,int]]:
	""" Calculates the projection matrix as the product of extrinsic and intrinsic matrices. Args:
		* `extrinsic_matrix`: World-to-Camera system coordinate Transformation 3x3 Matrix.
		* `intrinsic_matrix`: Camera-to-Pixel 3x4 Transformation matrix.
		
		Returns a 3x4 matrix. 
	"""
	return np.dot(np.float64(extrinsic_matrix), np.float64(intrinsic_matrix))

def resize_object(face_points: List[Tuple[int,int,int]], scale: int = 1) -> List[Tuple[int,int,int]]:
	""" Resizes the face to adjust the model to the Aruco bounds. Args:
		* `face`: Object face
		* `scale`: Resize factor (1 by default)
	"""
	return face_points*scale

def calculate_autoscale_factor(aruco_corners: List[Tuple[int,int]]) -> float:
	""" Returns the scaling size of Aruco marker. Used to address the autoescaling obj in marker bounds.Args:
		* `aruco_corners`: List of Aruco's corners
	"""
	# Finds the x and y distance between each corners peers
	return max([max(abs(aruco_corners[i]-aruco_corners[i-1])) for i in range(0,len(aruco_corners))])

def order_faces(reference: Tuple[int,int,int], faces_points: List[List[Tuple[int,int,int]]], faces_colors: List[List[Tuple[int,int,int]]]) -> List[List[Tuple[int,int,int]]]:
	""" Recommened before drawing. Orders object's faces by distance to reference point. Args:
		* 'reference`: Reference point (x,y,z)
		* `faces_points`: List of faces's points
		* `faces_colors`: List of faces's colors

		Returns the input arrays ordered from nearest to furthest. 
	"""
	distances = []
	# Calculates the centroid point of each face
	for face_points in faces_points:
		centroid = [0,0,0]
		for face_point in face_points:
			centroid += face_point[0]
		centroid = centroid/len(face_points) # Centroid point
		# Distance between centroid and reference point
		distance = dist(reference, centroid)
		distances.append(distance)
	# Gets the ordered indexes by distance (nearest->last element)
	order = np.argsort(distances)
	ordered_faces_point = [faces_points[i] for i in order]
	ordered_faces_colors = [faces_colors[i] for i in order]
	return (np.array(ordered_faces_point,dtype=object), ordered_faces_colors)

def _remove_z_coords(faces_points):
	_faces_points = []
	for face_points in faces_points:
		_faces_point = []
		for face_point in face_points:
			face_point = face_point[0][0:2]
			_faces_point.append(face_point)
		_faces_point = np.array(_faces_point)
		_faces_points.append(_faces_point)
	return np.array(_faces_points,dtype=object)