#!/usr/bin/env python3

## @file transform.py
#  Applies geometric transformations to a rectangle.
# 
#  Applies scale, rotation and translation to a rectangle.
#
# @author Ricardo Dutra da Silva


import sys
import ctypes
import numpy as np
import OpenGL.GL as gl
import OpenGL.GLUT as glut
sys.path.append('../lib/')
import utils as ut
import loader
from ctypes import c_void_p
import pywavefront


## Window width.
win_width  = 800
## Window height.
win_height = 600

## Program variable.
program = None
## Vertex array object.
VAO = None
## Vertex buffer object.
VBO = None

#obj file
vertices = []

## Vertex shader.
vertex_code = """
#version 330 core
layout (location = 0) in vec3 position;
layout (location = 1) in vec3 color;

out vec3 vColor;

uniform mat4 model;

void main()
{
    gl_Position = model * vec4(position, 1.0);
    vColor = color;
}
"""

## Fragment shader.
fragment_code = """
#version 330 core

in vec3 vColor;
out vec4 FragColor;

void main()
{
    FragColor = vec4(vColor, 1.0f);
} 
"""

## Drawing function.
#
# Draws primitive.
def display():

    gl.glClearColor(0.2, 0.3, 0.3, 1.0)
    gl.glClear(gl.GL_COLOR_BUFFER_BIT | gl.GL_DEPTH_BUFFER_BIT)

    gl.glUseProgram(program)
    gl.glBindVertexArray(VAO)

    # Translation. 
    T = ut.matTranslate(0, 0, 0)
    # Rotation around z-axis.
    Ry = ut.matRotateZ(np.radians(45.0))
    Rz = ut.matRotateX(np.radians(75.0))
    # Scale.
    S = ut.matScale(1, 1, 1)

    # M = T*R*S. 
    M = T.dot(Rz).dot(Ry).dot(S)

    # Retrieve location of tranform variable in shader.
    loc = gl.glGetUniformLocation(program, "model");
    # Send matrix to shader.
    gl.glUniformMatrix4fv(loc, 1, gl.GL_FALSE, M.transpose())

    gl.glDrawArrays(gl.GL_TRIANGLES, 0, 36)

    glut.glutSwapBuffers()


## Reshape function.
# 
# Called when window is resized.
#
# @param width New window width.
# @param height New window height.
def reshape(width,height):

    win_width = width
    win_height = height
    gl.glViewport(0, 0, width, height)
    
    glut.glutPostRedisplay()


## Keyboard function.
#
# Called to treat pressed keys.
#
# @param key Pressed key.
# @param x Mouse x coordinate when key pressed.
# @param y Mouse y coordinate when key pressed.
def keyboard(key, x, y):

    global type_primitive

    if key == b'\x1b'or key == b'q':
        sys.exit( )
    if key == b'1':
        gl.glPolygonMode(gl.GL_FRONT_AND_BACK, gl.GL_LINE)
    if key == b'2':
        gl.glPolygonMode(gl.GL_FRONT_AND_BACK, gl.GL_FILL)

    glut.glutPostRedisplay()


## Init vertex data.
#
# Defines the coordinates for vertices, creates the arrays for OpenGL.
def initData():

    # Uses vertex arrays.
    global VAO
    global VBO

    # Set vertices.
    vertices = np.array([
        # coordinate     color
        #primeira face, fundo
        -0.5, -0.5, -0.5, 0.0, 0.0, 1.0,
         0.5, -0.5, -0.5, 0.0, 0.0, 1.0,
        -0.5,  0.5, -0.5, 0.0, 0.0, 1.0,
         0.5, -0.5, -0.5, 0.0, 0.0, 1.0,
         0.5,  0.5, -0.5, 0.0, 0.0, 1.0,
        -0.5,  0.5, -0.5, 0.0, 0.0, 1.0,
        #segunda face, frente
        -0.5, -0.5,  0.5, 1.0, 0.0, 0.0,
         0.5, -0.5,  0.5, 1.0, 0.0, 0.0,
        -0.5,  0.5,  0.5, 1.0, 0.0, 0.0,
         0.5, -0.5,  0.5, 1.0, 0.0, 0.0,
         0.5,  0.5,  0.5, 1.0, 0.0, 0.0,
        -0.5,  0.5,  0.5, 1.0, 0.0, 0.0,
        #terceira face, esquerda
        -0.5,  0.5,  0.5, 0.0, 1.0, 0.0,
        -0.5, -0.5,  0.5, 0.0, 1.0, 0.0,
        -0.5, -0.5, -0.5, 0.0, 1.0, 0.0,
        -0.5,  0.5,  0.5, 0.0, 1.0, 0.0,
        -0.5,  0.5, -0.5, 0.0, 1.0, 0.0,
        -0.5, -0.5, -0.5, 0.0, 1.0, 0.0,
        #quarta face, direita
         0.5,  0.5,  0.5, 1.0, 1.0, 0.0,
         0.5, -0.5,  0.5, 1.0, 1.0, 0.0,
         0.5, -0.5, -0.5, 1.0, 1.0, 0.0,
         0.5,  0.5,  0.5, 1.0, 1.0, 0.0,
         0.5,  0.5, -0.5, 1.0, 1.0, 0.0,
         0.5, -0.5, -0.5, 1.0, 1.0, 0.0,
        #quinta face, cima
        -0.5,  0.5,  0.5, 0.0, 1.0, 1.0,
        -0.5,  0.5, -0.5, 0.0, 1.0, 1.0,
         0.5,  0.5, -0.5, 0.0, 1.0, 1.0,
         0.5,  0.5,  0.5, 0.0, 1.0, 1.0,
         0.5,  0.5, -0.5, 0.0, 1.0, 1.0,
        -0.5,  0.5,  0.5, 0.0, 1.0, 1.0,
        #sexta face, baixo
        -0.5, -0.5,  0.5, 1.0, 0.0, 1.0,
        -0.5, -0.5, -0.5, 1.0, 0.0, 1.0,
         0.5, -0.5, -0.5, 1.0, 0.0, 1.0,
         0.5, -0.5,  0.5, 1.0, 0.0, 1.0,
         0.5, -0.5, -0.5, 1.0, 0.0, 1.0,
        -0.5, -0.5,  0.5, 1.0, 0.0, 1.0
    ], dtype='float32')

    vertices = np.array([
        0.0, 0.0, 0.0,
        0.0, 0.0, 1.0,
        0.0, 1.0, 0.0,
        0.0, 1.0, 1.0,
        1.0, 0.0, 0.0,
        1.0, 0.0, 1.0,
        1.0, 1.0, 0.0,
        1.0, 1.0, 1.0
    ], dtype = 'float32')

    # Vertex array.
    VAO = gl.glGenVertexArrays(1)
    gl.glBindVertexArray(VAO)

    # Vertex buffer
    VBO = gl.glGenBuffers(1)
    gl.glBindBuffer(gl.GL_ARRAY_BUFFER, VBO)
    gl.glBufferData(gl.GL_ARRAY_BUFFER, vertices.nbytes, vertices, gl.GL_STATIC_DRAW)
    
    # Set attributes.
    gl.glVertexAttribPointer(0, 3, gl.GL_FLOAT, gl.GL_FALSE, 6*vertices.itemsize, None)
    gl.glEnableVertexAttribArray(0)
    gl.glVertexAttribPointer(1, 3, gl.GL_FLOAT, gl.GL_FALSE, 6*vertices.itemsize, c_void_p(3*vertices.itemsize))
    gl.glEnableVertexAttribArray(1)
    
    # Unbind Vertex Array Object.
    gl.glBindVertexArray(0)

## Create program (shaders).
#
# Compile shaders and create programs.
def initShaders():

    global program

    program = ut.createShaderProgram(vertex_code, fragment_code)


## Main function.
#
# Init GLUT and the window settings. Also, defines the callback functions used in the program.
def main():
    global vertices
    vertices = loader.ObjLoader.load_model("cube.obj")

    glut.glutInit()
    glut.glutInitContextVersion(3, 3);
    glut.glutInitContextProfile(glut.GLUT_CORE_PROFILE);
    glut.glutInitDisplayMode(glut.GLUT_DOUBLE | glut.GLUT_RGBA | glut.GLUT_DEPTH);
    
    glut.glutInitWindowSize(win_width,win_height)
    glut.glutCreateWindow('Geometric transformations')
    gl.glEnable(gl.GL_DEPTH_TEST)
    # Init vertex data for the triangle.
    initData()
    
    # Create shaders.
    initShaders()
    
    glut.glutReshapeFunc(reshape)
    glut.glutDisplayFunc(display)
    glut.glutKeyboardFunc(keyboard)

    scene = pywavefront.Wavefront(
        "cube.obj",
        create_materials=True,
        collect_faces=True
    )
    
    print("Faces:", scene.mesh_list[0].faces)
    print("Vertices:", scene.vertices)
    print("Format:", scene.mesh_list[0].materials[0].vertex_format)
    print("Vertices:", scene.mesh_list[0].materials[0].vertices)

    glut.glutMainLoop()
    

if __name__ == '__main__':
    main()
