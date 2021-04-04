#!/usr/bin/env python3

## @file projection3.py
# Applies a perspective projection to draw a cube and a pyramid.
# 
# @author Ricardo Dutra da Silva


import sys
import ctypes
import numpy as np
import OpenGL.GL as gl
import OpenGL.GLUT as glut
sys.path.append('../lib/')
import utils as ut
from ctypes import c_void_p
import loader
import pywavefront
import sys
import keyboard

## Window width.
win_width  = 600
## Window height.
win_height = 600

## Program variable.
program = None
## Vertex array object.
VAO1 = None
## Vertex buffer object.
VBO1 = None
## Vertex array object.
VAO2 = None
## Vertex buffer object.
VBO2 = None

## Pyramid x angle
px_angle = 0.0
## Pyramid x angle increment
px_inc = 0.01
## Pyramid y angle
py_angle = 0.0
## Pyramid y angle increment
py_inc = 0.02

## Cube x angle
cx_angle = 0.0
## Cube x angle increment
cx_inc = 0.01
## Cube y angle (orbit)
cy_angle = 0.0
## Cube y angle increment
cy_inc = 0.03
## Cube z angle
cz_angle = 0.0
## Cube z angle increment
cz_inc = 0.02

mode = None
visualizacao = "line"
keyboard_key = None

vertices = np.array([], dtype='float32')
scene = np.array([], dtype='float32')

## Vertex shader.
vertex_code = """
#version 330 core
layout (location = 0) in vec3 position;
layout (location = 1) in vec3 color;
layout (location = 2) in vec3 normals;
layout (location = 3) in vec2 text_coord;

out vec3 vColor;

uniform mat4 model;
uniform mat4 view;
uniform mat4 projection;

void main()
{
    gl_Position = projection * view * model * vec4(position, 1.0);
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

    # Define view matrix.
    view = ut.matTranslate(0.0, 0.0, -3.0)

    # Retrieve location of view variable in shader.
    loc = gl.glGetUniformLocation(program, "view");
    # Send matrix to shader.
    gl.glUniformMatrix4fv(loc, 1, gl.GL_FALSE, view.transpose())
    
    # Define projection matrix.
    projection = ut.matPerspective(np.radians(60.0), win_width/win_height, 0.1, 100.0)

    # Retrieve location of projection variable in shader.
    loc = gl.glGetUniformLocation(program, "projection");
    # Send matrix to shader.
    gl.glUniformMatrix4fv(loc, 1, gl.GL_FALSE, projection.transpose())


    # Cube.
    gl.glBindVertexArray(VAO1)

    # Define model matrix.
    S = ut.matScale(0.3, 0.3, 0.3)
    Rx = ut.matRotateX(np.radians(cx_angle))
    Ry = ut.matRotateY(np.radians(cy_angle))
    Rz = ut.matRotateZ(np.radians(cz_angle))
    T  = ut.matTranslate(0.0, 0.0, -2.0)
    model = np.matmul(Rz,S)
    model = np.matmul(Rx,model)
    model = np.matmul(T,model)
    model = np.matmul(Ry,model)
    model = np.matmul(T,model)

    # Retrieve location of model variable in shader.
    loc = gl.glGetUniformLocation(program, "model");
    # Send matrix to shader.
    gl.glUniformMatrix4fv(loc, 1, gl.GL_FALSE, model.transpose())

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
    global mode
    global visualizacao

    if key == b'\x1b'or key == b'q':
        sys.exit( )
    if key == b'v':
        if visualizacao == "line":
            gl.glPolygonMode(gl.GL_FRONT_AND_BACK, gl.GL_FILL)
            visualizacao = "fill"
        elif visualizacao == "fill":
            gl.glPolygonMode(gl.GL_FRONT_AND_BACK, gl.GL_LINE)
            visualizacao = "line"
    if key == b't':
        mode = 't'
    if key == b'r':
        mode = 'r'
    if key == b'e':
        mode = 'e'


    glut.glutPostRedisplay()

def SpecialInput(key, x, y):
    global keyboard_key
    global mode

    if key == glut.GLUT_KEY_UP:
        if mode == 't':

        elif mode == 'r':

        elif mode == 'e':

    elif key == glut.GLUT_KEY_DOWN:
        if mode == 't':

        elif mode == 'r':

        elif mode == 'e':

    elif key == glut.GLUT_KEY_LEFT:
        if mode == 't':

        elif mode == 'r':

        elif mode == 'e':

    elif key == glut.GLUT_KEY_RIGHT:
        if mode == 't':

        elif mode == 'r':

        elif mode == 'e':


## Idle function.
#
# Called continuously.
def idle():
    global cx_angle
    global cy_angle
    global cz_angle

    
    cx_angle = cx_angle+cx_inc if (cx_angle+cx_inc) < 360.0 else (360.0-cx_angle+cx_inc)
    cy_angle = cy_angle+cy_inc if (cy_angle+cy_inc) < 360.0 else (360.0-cy_angle+cy_inc)
    cz_angle = cz_angle+cz_inc if (cz_angle+cz_inc) < 360.0 else (360.0-cz_angle+cz_inc)

    glut.glutPostRedisplay()


## Init vertex data.
#
# Defines the coordinates for vertices, creates the arrays for OpenGL.
def initData():

    # Uses vertex arrays.
    global VAO1
    global VBO1
    global VAO2
    global VBO2
    global scene
    global vertices

    if len(sys.argv) == 1:
        vertices = loader.ObjLoader.load_model('cube.obj').astype('float32')
    else:
        vertices = loader.ObjLoader.load_model(str(sys.argv[1])).astype('float32')

    # Vertex array.
    VAO1 = gl.glGenVertexArrays(1)
    gl.glBindVertexArray(VAO1)

    # Vertex buffer
    VBO1 = gl.glGenBuffers(1)
    gl.glBindBuffer(gl.GL_ARRAY_BUFFER, VBO1)
    gl.glBufferData(gl.GL_ARRAY_BUFFER, vertices.nbytes, vertices, gl.GL_STATIC_DRAW)

    # Set attributes.
    gl.glVertexAttribPointer(0, 3, gl.GL_FLOAT, gl.GL_FALSE, 6*vertices.itemsize, None)
    gl.glEnableVertexAttribArray(0)
    gl.glVertexAttribPointer(1, 3, gl.GL_FLOAT, gl.GL_FALSE, 6*vertices.itemsize, c_void_p(3*vertices.itemsize))
    gl.glEnableVertexAttribArray(1)

    # Unbind Vertex Array Object.
    gl.glBindVertexArray(0)

    # Enable depth test.
    gl.glEnable(gl.GL_DEPTH_TEST);

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

    glut.glutInit()
    glut.glutInitContextVersion(3, 3);
    glut.glutInitContextProfile(glut.GLUT_CORE_PROFILE);
    glut.glutInitDisplayMode(glut.GLUT_DOUBLE | glut.GLUT_RGBA | glut.GLUT_DEPTH)
    glut.glutInitWindowSize(win_width,win_height)
    glut.glutCreateWindow('Perspective Projection')

    # Init vertex data for the triangle.
    initData()
    
    # Create shaders.
    initShaders()

    glut.glutReshapeFunc(reshape)
    glut.glutDisplayFunc(display)
    glut.glutKeyboardFunc(keyboard)
    glut.glutIdleFunc(idle);
    glut.glutSpecialFunc(SpecialInput)

    glut.glutMainLoop()

if __name__ == '__main__':
    main()
