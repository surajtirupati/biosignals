import pygame
from pygame.locals import *
from OpenGL.GL import *
from OpenGL.GLU import *
import numpy as np


def draw_cylinder(radius, height, slices):
    quadric = gluNewQuadric()
    gluCylinder(quadric, radius, radius, height, slices, 1)


def draw_sphere(radius, slices, stacks):
    quadric = gluNewQuadric()
    gluSphere(quadric, radius, slices, stacks)


def draw_cube(size):
    glBegin(GL_QUADS)

    # Front face
    glVertex3f(-size, -size, size)
    glVertex3f(size, -size, size)
    glVertex3f(size, size, size)
    glVertex3f(-size, size, size)

    # Back face
    glVertex3f(-size, -size, -size)
    glVertex3f(-size, size, -size)
    glVertex3f(size, size, -size)
    glVertex3f(size, -size, -size)

    # Top face
    glVertex3f(-size, size, -size)
    glVertex3f(-size, size, size)
    glVertex3f(size, size, size)
    glVertex3f(size, size, -size)

    # Bottom face
    glVertex3f(-size, -size, -size)
    glVertex3f(size, -size, -size)
    glVertex3f(size, -size, size)
    glVertex3f(-size, -size, size)

    # Right face
    glVertex3f(size, -size, -size)
    glVertex3f(size, size, -size)
    glVertex3f(size, size, size)
    glVertex3f(size, -size, size)

    # Left face
    glVertex3f(-size, -size, -size)
    glVertex3f(-size, -size, size)
    glVertex3f(-size, size, size)
    glVertex3f(-size, size, -size)

    glEnd()


def draw_finger(base_x, base_y, base_z, finger_length, finger_radius, num_joints):
    joint_length = finger_length / num_joints

    for i in range(num_joints):
        glPushMatrix()
        if i == 0:
            glTranslatef(base_x, base_y, base_z)
        else:
            glTranslatef(0, 0, joint_length)
        draw_cylinder(finger_radius, joint_length, 32)
        glTranslatef(0, 0, joint_length)
        draw_sphere(finger_radius, 32, 32)
        glPopMatrix()

def draw_hand():
    # Palm (simple cube)
    glPushMatrix()
    glScalef(1.5, 0.3, 0.8)  # Adjusted scaling for a more realistic palm
    draw_cube(1)
    glPopMatrix()

    # Finger properties
    finger_length = 1.8
    finger_radius = 0.15
    num_fingers = 5
    num_joints = 3
    finger_spacing = 0.6
    base_y = 0.5  # Base y-coordinate for fingers
    base_z_offset = 0.5  # Z offset for better attachment

    # Adjusted base_x positions for better finger spacing
    base_x_positions = [-0.9, -0.45, 0.0, 0.45, 0.9]

    for i in range(num_fingers):
        base_x = base_x_positions[i]
        base_z = base_z_offset
        draw_finger(base_x, base_y, base_z, finger_length, finger_radius, num_joints)

def main():
    pygame.init()
    display = (800, 600)
    pygame.display.set_mode(display, DOUBLEBUF | OPENGL)
    gluPerspective(45, (display[0] / display[1]), 0.1, 50.0)
    glTranslatef(0.0, 0.0, -5)

    rotation_angle_x = 0
    rotation_angle_y = 0
    rotate = True

    clock = pygame.time.Clock()

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                quit()
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    rotation_angle_x = 0  # Reset rotation angles when stopping rotation
                    rotation_angle_y = 0

        keys = pygame.key.get_pressed()

        if rotate:
            if keys[pygame.K_LEFT]:
                rotation_angle_y -= 1
            if keys[pygame.K_RIGHT]:
                rotation_angle_y += 1
            if keys[pygame.K_UP]:
                rotation_angle_x -= 1
            if keys[pygame.K_DOWN]:
                rotation_angle_x += 1

        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)

        glRotatef(rotation_angle_x, 1, 0, 0)
        glRotatef(rotation_angle_y, 0, 1, 0)

        draw_hand()
        pygame.display.flip()
        clock.tick(60)


if __name__ == "__main__":
    main()
