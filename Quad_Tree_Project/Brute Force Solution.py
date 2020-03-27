import pygame
import sys
import random
def two_range_overlap(low1, high1, low2, high2):
    if high2 > high1:
        if low1 <= low2 <= high1:
            return True
        else:
            return False

    # elif high1 > high2 or high1 == high2 (Just a note of the cases)
    else:
        if low2 <= low1 <= high2:
            return True
        else:
            return False


class Rect:
    def __init__(self, x, y, w, h, dx, dy):
        self.x = x
        self.y = y
        self.w = w
        self.h = h
        self.color = (0,0,0)
        self.dx = dx
        self.dy = dy

    def draw(self, screen):
        pygame.draw.rect(screen, self.color, (self.x, self.y, self.w, self.h))

    def update(self, screen_w, screen_h, collisions):
        self.x += self.dx
        self.y += self.dy

        if self.x < 0:
            self.dx *= -1
        elif self.x + self.w > screen_w:
            self.dx *= -1

        if self.y < 0:
            self.dy *= -1
        elif self.y + self.h > screen_h:
            self.dy *= -1

        self.collision_check(collisions)

    def collision_check(self, collisions):

            low1_x, high1_x = self.x, self.x + self.w
            low1_y, high1_y = self.y, self.y + self.h
            for collision in collisions:
                y_flag = True
                x_flag = True

                low2_x, high2_x = collision.x, collision.x + collision.w
                if two_range_overlap(low1_x, high1_x, low2_x, high2_x):
                    x_flag = False

                low2_y, high2_y = collision.y, collision.y + collision.h
                if two_range_overlap(low1_y, high1_y, low2_y, high2_y):
                    y_flag = False

                if not x_flag and not y_flag:
                    self.color = (255, 0, 0)
                    break


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
rects = []
for i in range(1000):
    dx, dy = random.randrange(-5,5), random.randrange(-5,5)
    x, y = random.randrange(1, screen.w), random.randrange(1, screen.h)
    rects.append(Rect(x, y, 10, 10, dx, dy))

while True:
    screen.fill()

    # Clear out history of past iterations
    for rect in rects:
        rect.color = (0,0,0)

    # Begin collision detection
    for i in range(len(rects)):
        collisions = []
        for j in range(len(rects)):
            if i != j:
                collisions.append(rects[j])

        rect = rects[i]
        rect.update(screen.w, screen.h, collisions)

    for rect in rects:
        rect.draw(screen.screen)

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

            rects.append(Rect(mx, my, 10, 10, dx, dy))
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_e:
                # Adjust player position
                mx, my = pygame.mouse.get_pos()
                dx, dy = 0, 0

                rects.append(Rect(mx, my, 20, 20, dx, dy))


    pygame.display.update()
    clock.tick(70)  # Fps (Don't know why/how it does it)

    # pygame.draw.aaline(screen.screen, (0,0,0), (0, screen.w/2), (screen.h, screen.w/2))
    # pygame.draw.aaline(screen.screen, (0,0,0), (screen.h/2, 0), (screen.h/2, screen.w))
