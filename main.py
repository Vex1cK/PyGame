import pygame
import sys
import math
import os
import random

pygame.init()
size = width, height = 1920, 1080  # касаемо экрана
screen = pygame.display.set_mode(size)

emenies = pygame.sprite.Group()  # создание групп спрайтов
walls = pygame.sprite.Group()
boxes = pygame.sprite.Group()
guns = pygame.sprite.Group()
player_bullets = pygame.sprite.Group()
all_sprites = pygame.sprite.Group()

moving_up, moving_down, moving_left, moving_right, shooting = False, False, False, False, False
movesCoords = {"UP": [0, -5], "DOWN": [0, 5], "LEFT": [-5, 0], "RIGHT": [5, 0]}
world_pos = 0
frames_count = 0
bullet_speed = 12
pos = (860, 440)


def rot_center(image, angle):  # поворот картинки
    loc = image.get_rect().center
    rot_sprite = pygame.transform.rotate(image, angle)
    rot_sprite.get_rect().center = loc
    return rot_sprite


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


class Example(pygame.sprite.Sprite):  # пример спрайта и работы функции position
    image = load_image('ex.jfif')

    def __init__(self, group):
        super().__init__(group)
        self.image = Example.image
        self.rect = self.image.get_rect()


class Player(pygame.sprite.Sprite):  # класс игрока
    image = load_image('player_calm.png')
    player_reverse = False

    def __init__(self, group):
        super().__init__(group)
        self.image = Player.image
        self.image = pygame.transform.scale(self.image, (200, 200))
        self.rect = self.image.get_rect()

    def update(self):
        if any((moving_up, moving_down, moving_left, moving_right)):
            if world_pos == 1:
                self.image = load_image('player_moving_1.png')
                self.image = pygame.transform.scale(self.image, (200, 200))
                if self.player_reverse is True:
                    self.image = pygame.transform.flip(self.image, True, False)
            else:
                self.image = load_image('player_moving_2.png')
                self.image = pygame.transform.scale(self.image, (200, 200))
                if self.player_reverse is True:
                    self.image = pygame.transform.flip(self.image, True, False)
            move = [0, 0]
            if moving_up:
                move[0] += movesCoords['UP'][0]
                move[1] += movesCoords['UP'][1]
            if moving_down:
                move[0] += movesCoords['DOWN'][0]
                move[1] += movesCoords['DOWN'][1]
            if moving_left:
                move[0] += movesCoords['LEFT'][0]
                move[1] += movesCoords['LEFT'][1]
            if moving_right:
                move[0] += movesCoords['RIGHT'][0]
                move[1] += movesCoords['RIGHT'][1]
            self.move(*move)
        else:
            self.image = load_image('player_calm.png')
            self.image = pygame.transform.scale(self.image, (200, 200))
            if self.player_reverse is True:
                self.image = pygame.transform.flip(self.image, True, False)

    def move(self, mx, my):
        self.rect = self.rect.move(mx, my)


class M4(pygame.sprite.Sprite):  # класс валыны
    image = pygame.transform.scale(load_image('M4.png'), (200, 200))

    def __init__(self, group):
        super().__init__(group)
        self.image = M4.image
        self.image = pygame.transform.scale(self.image, (200, 200))
        self.rect = self.image.get_rect()
        self.rect.center = player.rect.center

    def update(self, mouse_pos):
        self.x_mouse = mouse_pos[0]
        self.y_mouse = mouse_pos[1]
        self.self_x = self.rect.center[0]
        self.self_y = self.rect.center[1]
        self.sight_x = self.self_x - self.x_mouse
        self.sight_y = self.y_mouse - self.self_y
        if self.sight_x == 0:
            self.sight_x = 0.001
        self.tg = self.sight_y / self.sight_x

        self.angle = math.degrees(math.atan(self.tg))
        if self.sight_x > 0:
            self.image = pygame.transform.flip(M4.image, True, False)
            self.image = rot_center(self.image, self.angle)
            self.rect = self.image.get_rect()
            self.rect.center = player.rect.center
            player.player_reverse = True
        else:
            self.image = rot_center(M4.image, self.angle)
            self.rect = self.image.get_rect()
            self.rect.center = player.rect.center
            player.player_reverse = False


class P_Bullet(pygame.sprite.Sprite):  # класс пули
    image = load_image('bullet.png')
    kd = 7
    kdNow = 0

    def __init__(self, pos):
        if P_Bullet.kdNow >= P_Bullet.kd:
            super().__init__(player_bullets)
            self.image = P_Bullet.image
            self.rect = self.image.get_rect()
            self.rect.center = player.rect.center
            self.x_mouse = pos[0]
            self.y_mouse = pos[1]
            self.self_x = self.rect.center[0]
            self.self_y = self.rect.center[1]
            self.sight_x = self.x_mouse - self.self_x
            self.sight_y = self.y_mouse - self.self_y
            self.speed = (self.sight_x ** 2 + self.sight_y ** 2) ** (1 / 2)
            if self.speed == 0:
                self.speed = 0.01

            self.vx = bullet_speed * self.sight_x / self.speed * 2
            self.vy = bullet_speed * self.sight_y / self.speed * 2
            self.rect = self.rect.move(self.vx, self.vy)
            self.vx /= 2
            self.vy /= 2
            P_Bullet.kdNow = 0
        else:
            P_Bullet.kdNow += 1

    def update(self):
        self.rect = self.rect.move(self.vx, self.vy)


class Camera:
    # зададим начальный сдвиг камеры
    def __init__(self):
        self.dx = 0
        self.dy = 0

    # сдвинуть объект obj на смещение камеры
    def apply(self, obj):
        obj.rect.x += self.dx
        obj.rect.y += self.dy

    # позиционировать камеру на объекте target
    def update(self, target):
        self.dx = -(target.rect.x + target.rect.w // 2 - width // 2)
        self.dy = -(target.rect.y + target.rect.h // 2 - height // 2)


player = Player(all_sprites)
gun = M4(guns)
clock = pygame.time.Clock()
camera = Camera()
ex = Example(all_sprites)

while True:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            terminate()

        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_w:
                moving_up = True
            if event.key == pygame.K_s:
                moving_down = True
            if event.key == pygame.K_a:
                moving_left = True
            if event.key == pygame.K_d:
                moving_right = True

        if event.type == pygame.KEYUP:
            if event.key == pygame.K_w:
                moving_up = False
            if event.key == pygame.K_s:
                moving_down = False
            if event.key == pygame.K_a:
                moving_left = False
            if event.key == pygame.K_d:
                moving_right = False

        if event.type == pygame.MOUSEMOTION:
            pos = event.pos
            gun.update(pos)

        if event.type == pygame.MOUSEBUTTONDOWN:
            shooting = True

        if event.type == pygame.MOUSEBUTTONUP:
            shooting = False

    camera.update(player)
    for sprite in all_sprites:
        camera.apply(sprite)

    if shooting:
        bullet = P_Bullet(pos)
        try:
            a = bullet.rect
            all_sprites.add(bullet)
        except AttributeError:
            pass
    else:
        P_Bullet.kdNow += 1

    frames_count += 1  # счетчик, использую для цикличной смены анимаций, например ходьба
    if (frames_count // 5) % 2 == 1:
        world_pos = 1
    else:
        world_pos = 0

    screen.fill("Black")

    all_sprites.update()
    player_bullets.update()
    gun.update(pos)

    player_bullets.draw(screen)
    all_sprites.draw(screen)
    guns.draw(screen)

    pygame.display.flip()
    clock.tick(60)
