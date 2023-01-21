import cv2
from typing import Tuple
from math import dist

class OBJ(): 
    """ OBJ (.obj) class. Constructor params:
        * obj_path: Absolute path to .obj file
        * texture_path: Path of texture image (eg. png, jpg)
        * normalise: Obtain normalised OBJ (recommended)
        * normalised_axis: Axis to perform object normalization
    """
    
    def __init__(self, obj_path: str, texture_path: str = None, normalise: bool = True, normalised_axis: str = "XY"):
        if texture_path is not None:
            # Reads texture img from path
            self.texture = cv2.imread(texture_path)
        # Inializaction of arrays
        self._vertices = []
        self._texture_coordinates = []
        self._vertices_normals = []
        self.faces = []
        # Iterates for each line of .obj file
        for line in open(obj_path, "r"):
            if line.startswith("#"):
                # jumps to the next line, `#` is a comment or an empty line
                continue
            
            if line.startswith("v "):
                # `v` means that line defines an object's geometic vertices, with (x, y, z), optional w coordinate is omitted
                self._vertices.append([float(i) for i in line.split()[1:4]])

            elif line.startswith("vt "):
                # `vt` stands for texture coordinates, in (u, [v, w]) coordinates, with values between 0 and 1. v, w is omitted
                self._texture_coordinates.append([float(i) for i in line.split()[1:3]])

            elif line.startswith("vn "):
                # `vn` stands for vertex normal vectors, in (x,y,z) coordinates
                self._vertices_normals.append([float(i) for i in line.split()[1:3]])

            elif line.startswith("f "):
                # `f` Faces are defined using lists of vertex, texture and normal indices in the format vertex_index/texture_index/normal_index for which each
                #  index starts at 1 and increases corresponding to the order in which the referenced element was defined. Polygons such as quadrilaterals can be 
                # defined by using more than three indices.
                vertex_points = []
                vertex_colors = []
                vertex_normals = [] 
                for i in line.split()[1:]:
                    # Iterates for each index within a line f v1/vt1/vn1 ->(1) v2/vt2/vn2 ->(2)  v3/vt3/vn3 ->(3)
                    elements = i.split('/') # Elements of the index
                    vertex_points.append(self._get_vertex_point(int(elements[0]))) # Adds the first element (vertex point)
                    try:
                        # Checks if texture exists
                        if len(elements) > 1 and elements[1]:
                            # second element of index not ""
                            vertex_colors.append(self._get_vertex_color(int(elements[1]))) # Adds the second element (texture coordinate)
                    except AttributeError:
                        pass
                    if len(elements) > 2:
                        vertex_normals.append(self._get_vertex_normals(int(elements[2]))) # Adds the second element (normal vector)
                # Every face has at least 3 pts
                face = {'points': vertex_points}
                if vertex_colors:
                    face['colors'] = vertex_colors
                if vertex_normals:
                    face['normals'] = vertex_normals
                # Adds obj face 
                self.faces.append(face)
        # Object normalization
        if normalise:
            self.normalise(normalised_axis)

    def _get_vertex_point(self, vertex_index: int) -> Tuple[int, int, int]:
        """ 
            Returns the (x,y,z) coordinates of that vertex. Params:
            * vertex_index: Integer index that indicates where in the vertex points array are the coordinates.
        """ 
        return self._vertices[vertex_index-1]

    def _get_vertex_color(self, texture_coordinates_index: int) -> Tuple[int, int, int]:
        """ 
            Returns the color values in BGR format of pixel located at the texture coordinates. Params:
            * texture_coordinates_index: Integer index that indicates where in the texture coordinates array are the relative texture coordinates.
        """
        # Relative texture coordinates
        u, v = self._texture_coordinates[texture_coordinates_index-1]
        h, w, _ = self.texture.shape
        # Absolute coordinates of pixel
        x, y = [round(h*(1-v)),round(w*u)]
        # Texture coordinate checking
        if x < 0:
            x = 0
        elif x >= w:
            x = w-1
        if y < 0:
            y = 0
        elif y >= h:
            y = h-1
        return [int(self.texture[x][y][i]) for i in range(0,3)]
            
    def _get_vertex_normals(self, vertex_normal_index: int) -> Tuple[int, int, int]:
        """ 
            Returns the (u,v,w) normal vectors of that vertex. Params:
            * vertex_normal_index: Integer index that indicates where in the vertex normals array are the coordinates.
        """
        return self._vertices_normals[vertex_normal_index-1]

    def _furthest_point(self, normalised_axis):
        """ Finds furthest point from object center. """
        max_distance = 0
        for face in self.faces:
            points = face['points']
            for point in points:
                if normalised_axis == "XY":
                    distance = dist(point[0:2],[0,0])
                elif normalised_axis == "XYZ":
                    distance = dist(point[0:3],[0,0,0])
                if distance > max_distance:
                    max_distance = distance
        return max_distance

    def normalise(self, normalised_axis) -> None:
        """ Adjusts object's scale to fit in one-unit-side cube. """
        norm = self._furthest_point(normalised_axis)
        for i, face in enumerate(self.faces):
            points = face['points']
            norm_points = []
            for point in points:
                norm_point = [coord/norm for coord in point]
                norm_points.append(norm_point)
            self.faces[i]['points'] = norm_points