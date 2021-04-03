import numpy as np


class ObjLoader:

    def load_model(file):
        # v
        vertex_positions = []
        # vt
        vertex_textcoords = []
        # vn
        vertex_normals = []

        # faces
        vertex_position_indices = []
        vertex_position_textcoord = []
        vertex_position_normal = []

        # vertex array
        vertices = np.array([], dtype='float32')

        with open(file, 'r') as f:
            line = f.readline()
            while line:
                values = line.split()
                temp_vec3 = []
                temp_vec2 = []

                if len(values):
                    if values[0] == 'v':
                        for d in values[1:]:
                            temp_vec3.append(float(d))
                        vertex_positions.append(temp_vec3)
                    elif values[0] == 'vt':
                        for d in values[1:]:
                            temp_vec2.append(float(d))
                        vertex_textcoords.append(temp_vec2)
                    elif values[0] == 'vn':
                        for d in values[1:]:
                            temp_vec3.append(float(d))
                        vertex_normals.append(temp_vec3)
                    elif values[0] == 'f':
                        for value in values[1:]:
                            val = value.split('/')

                            i = 0
                            for v in val:
                                if v != '':
                                    if i == 0:
                                        vertex_position_indices.append(int(v)-1)
                                    elif i == 1:
                                        vertex_position_textcoord.append(int(v)-1)
                                    elif i == 2:
                                        vertex_position_normal.append(int(v)-1)

                                i = i + 1

                line = f.readline()

        i = 0
        while i < len(vertex_position_indices):
            vertices = np.append(vertices, vertex_positions[vertex_position_indices[i]])

            colors = np.random.rand(1, 3)

            colors[colors >= 0.5] = 1.0
            colors[colors < 0.5] = 0.0

            #vertices = np.append(vertices, colors)

            #vertices.append(vertex_textcoords[vertex_position_textcoord[i]])

            #vertices = np.append(vertices, vertex_normals[vertex_position_normal[i]])

            i = i + 1

        with np.printoptions(threshold=np.inf):
            print (vertices)

        return vertices