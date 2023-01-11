import pygame
import sys
import os
import random
import math


pygame.init()
size = width, height = 600, 600  # касаемо экрана
screen = pygame.display.set_mode(size)

def terminate():
    pygame.quit()
    sys.exit()


def load_image(name, colorkey=None):  # загрузка картинки
    fullname = os.path.join('data', name)
    if not os.path.isfile(fullname):
        print(f"Файл с изображением '{fullname}' не найден")
        sys.exit()
    image = pygame.image.load(fullname)
    if colorkey is not None:
        image = image.convert()
        if colorkey == -1:
            colorkey = image.get_at((0, 0))
        image.set_colorkey(colorkey)
    else:
        image = image.convert_alpha()
    return image

a = [1,2,3,4]
a.append(5)
print(a)

while True:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            terminate()
    pygame.display.flip()
