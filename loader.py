import numpy as np


class ObjLoader:

    def load_model(file):
        maiorX = -99.0
        menorX = +99.0
        maiorY = -99.0
        menorY = +99.0
        maiorZ = -99.0
        menorZ = +99.0

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
                        i = 0
                        for d in values[1:]:

                            if i == 0:
                                if float(d) >= maiorX:
                                    maiorX = float(d)
                                if float(d) <= menorX:
                                    menorX = float(d)
                            elif i == 1:
                                if float(d) >= maiorY:
                                    maiorY = float(d)
                                if float(d) <= menorY:
                                    menorY = float(d)
                            elif i == 2:
                                if float(d) >= maiorZ:
                                    maiorZ = float(d)
                                if float(d) <= menorZ:
                                    menorZ = float(d)
                            i = i + 1

                            temp_vec3.append(float(d))
                        vertex_positions.append(temp_vec3)
                    #elif values[0] == 'vt':
                    #    for d in values[1:]:
                    #        temp_vec2.append(float(d))
                    #    vertex_textcoords.append(temp_vec2)
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
                                    #elif i == 1:
                                    #    vertex_position_textcoord.append(int(v)-1)
                                    elif i == 2:
                                        vertex_position_normal.append(int(v)-1)

                                i = i + 1

                line = f.readline()

        center = np.array([(maiorX + menorX) / 2, (maiorY + menorY) / 2, (maiorZ + menorZ) / 2], dtype='float32')
        i = 0
        while i < len(vertex_position_indices):
            #vertices = np.append(vertices, vertex_positions[vertex_position_indices[i]])
            vertices = np.append(vertices, vertex_positions[vertex_position_indices[i]] - center)

            vertices = np.append(vertices, vertex_normals[vertex_position_normal[i]])

            #vertices = np.append(vertices, vertex_textcoords[vertex_position_textcoord[i]])

            i = i + 1

        #with np.printoptions(threshold=np.inf):
            #print (vertices)

        return vertices