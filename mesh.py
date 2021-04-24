#!/usr/bin/env python3
# @author Guilherme Rossi


import sys
import ctypes
import numpy as np
import OpenGL.GL as gl
import OpenGL.GLUT as glut
sys.path.append('lib/')
import utils as ut
from ctypes import c_void_p
import loader
import pywavefront

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

# VARIABLES

# vertices number
vertices_num = 0

# translacao
translacao_x = 0.0
translacao_y = 0.0
translacao_z = 0.0

# rotacao
rotacao_x = 0
rotacao_y = 0
rotacao_z = 0

# escala
escala_x = 0.3
escala_y = 0.3
escala_z = 0.3

# center of obj
cx = 0
cy = 0
cz = 0

lastModel = None
mode = None
visualizacao = "line"
keyboard_key = None

vertices = np.array([], dtype='float32')
scene = np.array([], dtype='float32')

## Vertex shader.
vertex_code = """
#version 330 core
layout (location = 0) in vec3 position;
layout (location = 1) in vec3 normal;

uniform mat4 model;
uniform mat4 view;
uniform mat4 projection;

out vec3 vNormal;
out vec3 fragPosition;

void main()
{
    gl_Position = projection * view * model * vec4(position, 1.0);
    vNormal = normal;
    fragPosition = vec3(model * vec4(position, 1.0));
}
"""

## Fragment shader.
fragment_code = """
#version 330 core

in vec3 vNormal;
in vec3 fragPosition;

out vec4 fragColor;

uniform vec3 objectColor;
uniform vec3 lightColor;
uniform vec3 lightPosition;
uniform vec3 cameraPosition;

void main()
{
    float ka = 0.5;
    vec3 ambient = ka * lightColor;

    float kd = 0.8;
    vec3 n = normalize(vNormal);
    vec3 l = normalize(lightPosition - fragPosition);
    
    float diff = max(dot(n,l), 0.0);
    vec3 diffuse = kd * diff * lightColor;

    float ks = 1.0;
    vec3 v = normalize(cameraPosition - fragPosition);
    vec3 r = reflect(-l, n);

    float spec = pow(max(dot(v, r), 0.0), 3.0);
    vec3 specular = ks * spec * lightColor;

    vec3 light = (ambient + diffuse + specular) * objectColor;
    fragColor = vec4(light, 1.0);
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
    view = ut.matTranslate(0.0, 0.0, -6.0)

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

    # object.
    gl.glBindVertexArray(VAO1)

    # Define model matrix.
    S = ut.matScale(escala_x, escala_y, escala_z)

    Rx = ut.matRotateX(np.radians(rotacao_x))
    Ry = ut.matRotateY(np.radians(rotacao_y))
    Rz = ut.matRotateZ(np.radians(rotacao_z))

    T  = ut.matTranslate(translacao_x, translacao_y, translacao_z)

    TcentroNeg = ut.matTranslate(translacao_x-cx, translacao_y-cy, translacao_z-cz)
    #Tcentro = ut.matTranslate(cx, cy, cz)
    Tzero = ut.matTranslate(0.0, 0.0, 0.0)

    Tz = ut.matTranslate(translacao_x, translacao_y, -translacao_z)
    Ty = ut.matTranslate(translacao_x, -translacao_y, translacao_z)
    Tx = ut.matTranslate(-translacao_x, translacao_y, translacao_z)

    model = np.matmul(TcentroNeg, S)

    model = np.matmul(Tx, model)
    model = np.matmul(Rx, model)

    model = np.matmul(Tz, model)
    model = np.matmul(Rz, model)

    model = np.matmul(Ty, model)
    model = np.matmul(Ry, model)

    model = np.matmul(T, model)

    # Retrieve location of model variable in shader.
    loc = gl.glGetUniformLocation(program, "model");
    # Send matrix to shader.
    gl.glUniformMatrix4fv(loc, 1, gl.GL_FALSE, model.transpose())

    # Object color.
    loc = gl.glGetUniformLocation(program, "objectColor")
    gl.glUniform3f(loc, 0.5, 0.1, 0.1)
    # Light color.
    loc = gl.glGetUniformLocation(program, "lightColor")
    gl.glUniform3f(loc, 1.0, 1.0, 1.0)
    # Light position.
    loc = gl.glGetUniformLocation(program, "lightPosition")
    gl.glUniform3f(loc, 0.0, 0.0, 0.0)
    # Camera position.
    loc = gl.glGetUniformLocation(program, "cameraPosition")
    gl.glUniform3f(loc, 0.0, 0.0, 0.0)

    gl.glDrawArrays(gl.GL_TRIANGLES, 0, vertices_num)

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

    global translacao_z
    global rotacao_z
    global escala_z

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

    if key == b'a':
        if mode == 't': # tranlacao postiva em z
            translacao_z = translacao_z + 0.2
        elif mode == 'r':  # rotacao positiva em z
            rotacao_z = rotacao_z + 20 if (rotacao_z + 20) < 360.0 else (rotacao_z + 20 - 360.0)
        elif mode == 'e':  # escala positiva em z
            escala_z = escala_z + 0.2

    elif key == b'd':
        if mode == 't': # tranlacao negativa em z
            translacao_z = translacao_z - 0.2
        elif mode == 'r': # rotacao negativa em z
            rotacao_z = rotacao_z - 20 if (rotacao_z - 20) < 0 else (360.0 + rotacao_z - 20)
        elif mode == 'e':  # escala negativa em z
            escala_z = escala_z - 0.2 if (escala_z - 0.2) > 0.0 else escala_z

    glut.glutPostRedisplay()

def SpecialInput(key, x, y):
    global keyboard_key
    global mode

    global translacao_x
    global translacao_y

    global rotacao_x
    global rotacao_y

    global escala_x
    global escala_y

    if key == glut.GLUT_KEY_UP:
        if mode == 't': # translacao positiva em y
            translacao_y = translacao_y + 0.2
        elif mode == 'r': # rotacao positiva em x
            rotacao_x = rotacao_x + 20 if (rotacao_x + 20) < 360.0 else (rotacao_x + 20 - 360.0)
        elif mode == 'e':  # escala positiva em y
            escala_y = escala_y + 0.2

    elif key == glut.GLUT_KEY_DOWN:
        if mode == 't': # translacao negativa em y
            translacao_y = translacao_y - 0.2
        elif mode == 'r': # rotacao negativa em x
            rotacao_x = rotacao_x - 20 if (rotacao_x - 20) < 0 else (360.0 + rotacao_x - 20)
        elif mode == 'e':  # escala negativa em y
            escala_y = escala_y - 0.2 if (escala_y - 0.2) > 0.0 else escala_y

    elif key == glut.GLUT_KEY_LEFT:
        if mode == 't': # translacao negativa em x
            translacao_x = translacao_x - 0.2
        elif mode == 'r': # rotacao negativa em y
            rotacao_y = rotacao_y - 20 if (rotacao_y - 20) < 0 else (360.0 + rotacao_y - 20)
        elif mode == 'e':  # escala negativa em x
            escala_x = escala_x - 0.2 if (escala_x - 0.2) > 0.0 else escala_x

    elif key == glut.GLUT_KEY_RIGHT:
        if mode == 't': # translacao positiva em x
            translacao_x = translacao_x + 0.2
        elif mode == 'r':  # rotacao positiva em y
            rotacao_y = rotacao_y + 20 if (rotacao_y + 20) < 360.0 else (rotacao_y + 20 - 360.0)
        elif mode == 'e':  # escala positiva em x
            escala_x = escala_x + 0.2

    glut.glutPostRedisplay()

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
    global scene
    global vertices
    global vertices_num
    global cx
    global cy
    global cz

    if len(sys.argv) == 1:
        vertices = loader.ObjLoader.load_model('cube.obj').astype('float32')
    else:
        vertices = loader.ObjLoader.load_model(str(sys.argv[1])).astype('float32')

    quo = len(vertices)/6
    x = 0
    y = 0
    z = 0
    i = 0
    while i < len(vertices):
        x = x + vertices[i]
        y = y + vertices[i+1]
        z = z + vertices[i+2]

        i = i + 3

    cx = x/quo
    cy = y/quo
    cz = z/quo

    vertices_num = (len(vertices)/6).__int__()

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

    print("-----------------------------------------------------------")
    print("Alternar entre Fill e Wireframe: 'v'")
    print("Modo Translação: 't'")
    print("\t →  : deslocamento positivo em X")
    print("\t ←  : deslocamento negativo em X")
    print("\t ↑  : deslocamento positivo em Y")
    print("\t ↓  : deslocamento negativo em Y")
    print("\t'a' : deslocamento positivo em Z")
    print("\t'd' : deslocamento negativo em Z")

    print("Modo Rotação: 'r'")
    print("\t ↑  : rotação positivo em X")
    print("\t ↓  : rotação negativo em X")
    print("\t →  : rotação positivo em Y")
    print("\t ←  : rotação negativo em Y")
    print("\t'a' : rotação positivo em Z")
    print("\t'd' : rotação negativo em Z")

    print("Modo Escala: 'e'")
    print("\t →  : fator positivo em X")
    print("\t ←  : fator negativo em X")
    print("\t ↑  : fator positivo em Y")
    print("\t ↓  : fator negativo em Y")
    print("\t'a' : fator positivo em Z")
    print("\t'd' : fator negativo em Z")
    print("-----------------------------------------------------------")

    glut.glutInit()
    glut.glutInitContextVersion(3, 3);
    glut.glutInitContextProfile(glut.GLUT_CORE_PROFILE);
    glut.glutInitDisplayMode(glut.GLUT_DOUBLE | glut.GLUT_RGBA | glut.GLUT_DEPTH)
    glut.glutInitWindowSize(win_width,win_height)
    glut.glutCreateWindow('Trabalho 1')

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
