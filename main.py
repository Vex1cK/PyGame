import pygame
import sys
import math
import os
import random

pygame.init()
pygame.font.init()
size = width, height = 1920, 1080  # касаемо экрана
screen = pygame.display.set_mode(size)

emenies = pygame.sprite.Group()  # создание групп спрайтов
walls = pygame.sprite.Group()
boxes = pygame.sprite.Group()
guns = pygame.sprite.Group()
barrels = pygame.sprite.Group()
player_bullets = pygame.sprite.Group()
flors = pygame.sprite.Group()
player_group = pygame.sprite.Group()
all_gropus = [flors, walls, boxes, barrels, emenies, player_group, player_bullets, guns]

moving_up, moving_down, moving_left, moving_right, shooting = False, False, False, False, False
movesCoords = {"UP": [0, -5], "DOWN": [0, 5], "LEFT": [-5, 0], "RIGHT": [5, 0]}
world_pos = 0
frames_count = 0
bullet_speed = 12
player_accuracy = 1
reload_timer = 0
reload_time = 120

mag = 30
ammo = 120
pos = (860, 440)
viewBoard = [[0] * 8 for _ in range(8)]


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
            self.vx *= 3
            self.vy *= 3
            self.rect = self.rect.move(self.vx, self.vy)
            self.vx /= 4
            self.vy /= 4
            self.vx += random.choice(range(0 - player_accuracy, player_accuracy))
            self.vy += random.choice(range(0 - player_accuracy, player_accuracy))
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


class Flor(pygame.sprite.Sprite):
    image = pygame.transform.scale(load_image("flor.png"), (250, 250))

    def __init__(self, x, y):
        super().__init__(flors)
        self.image = Flor.image
        self.rect = self.image.get_rect()
        self.rect.x, self.rect.y = x, y


class Board():
    def __init__(self):
        for i in range(8):
            for j in range(8):
                viewBoard[i][j] = Flor((j - 4) * 250, (i - 4) * 250)

        self.playerNowX, self.playerNowY = 4, 4
        self.playerOldX, self.playerOldY = 4, 4

    def update(self):
        r = True
        for i in range(len(viewBoard)):
            for j in range(len(viewBoard[i])):
                fl = viewBoard[i][j]
                if fl.rect.x < player.rect.centerx < fl.rect.x + 250 and \
                        fl.rect.y < player.rect.centery < fl.rect.y + 250:
                    self.playerOldX, self.playerOldY = self.playerNowX, self.playerNowY
                    self.playerNowX, self.playerNowY = j, i
                    r = False
                    break
            if not r:
                break
        if (self.playerNowX, self.playerNowY) != \
                (self.playerOldX, self.playerOldY):
            move = (
                self.playerNowX - self.playerOldX,
                self.playerNowY - self.playerOldY
            )
            if move[0] == 1:
                for i in range(len(viewBoard)):
                    viewBoard[i] = viewBoard[i][1:] + [viewBoard[i][0]]
                    viewBoard[i][-1].rect.x = viewBoard[i][-2].rect.x + 250
                    self.playerNowX += 1
            elif move[0] == -1:
                for i in range(len(viewBoard)):
                    viewBoard[i] = [viewBoard[i][-1]] + viewBoard[i][:-1]
                    viewBoard[i][0].rect.x = viewBoard[i][1].rect.x - 250
                    self.playerNowX -= 1
            if move[1] == 1:
                viewBoard[:] = viewBoard[1:] + [viewBoard[0]]
                for fl in viewBoard[-1]:
                    fl.rect.y = viewBoard[-2][1].rect.y + 250
                self.playerNowY += 1
            elif move[1] == -1:
                viewBoard[:] = [viewBoard[-1]] + viewBoard[:-1]
                for fl in viewBoard[0]:
                    fl.rect.y = viewBoard[1][1].rect.y - 250
                self.playerNowY -= 1


player = Player(player_group)  # спрайты
gun = M4(guns)
clock = pygame.time.Clock()
camera = Camera()
ex = Example(emenies)
board = Board()

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
            if event.key == pygame.K_r and reload_timer == 0:
                reload_timer += 1

        if event.type == pygame.MOUSEMOTION:
            pos = event.pos
            gun.update(pos)

        if event.type == pygame.MOUSEBUTTONDOWN:
            shooting = True

        if event.type == pygame.MOUSEBUTTONUP:
            shooting = False

    camera.update(player)
    for group in all_gropus:
        for sprite in group:
            camera.apply(sprite)

    if reload_timer > reload_time:
        reload_timer = 0
        if ammo >= 30:
            ammo -= 30
            mag = 30
        else:
            mag = ammo
            ammo = 0
    elif reload_timer > 0:
        reload_timer += 1

    if shooting:
        if mag > 0 and reload_timer == 0:
            bullet = P_Bullet(pos)
            try:
                a = bullet.rect
                mag -= 1
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
    for group in all_gropus:
        if not group is guns:
            group.update()
    guns.update(pos)
    board.update()

    for group in all_gropus:
        group.draw(screen)

    mag_font = pygame.font.Font(None, 200)
    if mag >= 10:
        mag_info = mag_font.render(str(mag), True, (240, 240, 240))
        screen.blit(mag_info, (1500, 900))
    else:
        mag_info = mag_font.render(str(mag), True, (240, 40, 40))
        screen.blit(mag_info, (1585, 900))

    ammo_font = pygame.font.Font(None, 125)
    if ammo > 30:
        ammo_info = ammo_font.render(str(ammo), True, (220, 220, 220))
    else:
        ammo_info = ammo_font.render(str(ammo), True, (220, 20, 20))
    screen.blit(ammo_info, (1700, 925))
    pygame.draw.rect(screen, (150, 150, 150), pygame.Rect((1670, 900), (20, 120)))
    if reload_timer == 0:
        pygame.draw.rect(screen, (240, 240, 240), pygame.Rect((1670, 900), (20, 120)))
    else:
        pygame.draw.rect(screen, (240, 240, 240), pygame.Rect((1670, 900), (20, reload_timer)))

    pygame.display.flip()
    clock.tick(60)
