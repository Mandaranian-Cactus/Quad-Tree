import pygame
import sys
import Quad_Tree_Project
import random


class Window:
    def __init__(self, w, h):
        self.w = w
        self.h = h
        self.screen = pygame.display.set_mode((self.w, self.h))

    def fill(self):
        self.screen.fill((255, 255, 255))


screen = Window(600, 600)
pygame.init()
clock = pygame.time.Clock()
quad_tree = Quad_Tree_Project.Quad_tree(0,0,screen.w, screen.h,0)
rects = []
for i in range(700):
    dx, dy = random.randrange(-3,3), random.randrange(-3,3)
    x, y = random.randrange(1, screen.w - 10), random.randrange(1, screen.h - 10)
    rects.append(Quad_Tree_Project.Rect(x, y, 10, 10, dx, dy))

while True:
    screen.fill()

    quad_tree.clear()
    for rect in rects:
        quad_tree.insert(rect)

    # Clear out history of past iterations
    for rect in rects:
        rect.color = (0,0,0)

    # Begin collision detection
    for rect in rects:
        collisions = quad_tree.retrieve([], rect)
        collisions.remove(rect)  # Remove the rectangle being checked
        rect.update(screen.w, screen.h, collisions)

    for rect in rects:
        rect.draw(screen.screen)

    quad_tree.draw_trees(screen.screen)

    # Check inputs
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            sys.exit()
        if event.type == pygame.MOUSEBUTTONDOWN:
            # Adjust player position
            mx, my = pygame.mouse.get_pos()
            dx, dy = 0, 0
            while dx == 0 or dy == 0:  # Not the best condition but works
                dx, dy = random.randrange(-2, 2), random.randrange(-2, 2)

            rects.append(Quad_Tree_Project.Rect(mx, my, 10, 10, dx, dy))
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_e:
                # Adjust player position
                mx, my = pygame.mouse.get_pos()
                dx, dy = 0, 0

                rects.append(Quad_Tree_Project.Rect(mx, my, 20, 20, dx, dy))


    pygame.display.update()
    clock.tick(70)  # Fps (Don't know why/how it does it)

    # pygame.draw.aaline(screen.screen, (0,0,0), (0, screen.w/2), (screen.h, screen.w/2))
    # pygame.draw.aaline(screen.screen, (0,0,0), (screen.h/2, 0), (screen.h/2, screen.w))
