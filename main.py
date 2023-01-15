import pygame
import sys
import math
import os
import random

pygame.init()
pygame.font.init()
pygame.mouse.set_visible(False)
size = width, height = 1920, 1080  # касаемо экрана
screen = pygame.display.set_mode(size)

moving = False

pygame.mixer.music.load('sounds\\BG.mp3')
pygame.mixer.music.set_volume(1.5)
pygame.mixer.music.play()

m4_shot = pygame.mixer.Sound('sounds\\AK.mp3')
m4_shot.set_volume(1.5)
ak_shot = pygame.mixer.Sound('sounds\\M4.mp3')
ak_shot.set_volume(1.5)
walking = pygame.mixer.Sound('sounds\\running.mp3')
walking.set_volume(1.5)
blowing = pygame.mixer.Sound('sounds\\boom.mp3')
blowing.set_volume(1.5)

enemy_bullets = pygame.sprite.Group()
emenies = pygame.sprite.Group()  # создание групп спрайтов
boxes = pygame.sprite.Group()
guns = pygame.sprite.Group()
barrels = pygame.sprite.Group()
player_bullets = pygame.sprite.Group()
flors = pygame.sprite.Group()
adrLineGr = pygame.sprite.Group()
ammoGr = pygame.sprite.Group()
AKS = pygame.sprite.Group()
player_group = pygame.sprite.Group()
messages = pygame.sprite.Group()
carsGr = pygame.sprite.Group()
particles = pygame.sprite.Group()
all_gropus = [flors, boxes, barrels, adrLineGr, ammoGr, carsGr,
              emenies, player_group, player_bullets, enemy_bullets, AKS, guns,
              particles, messages]

moving_up, moving_down, moving_left, \
moving_right, shooting, moving_barrel, haveBarrelMoveMessage = False, False, False, \
                                                               False, False, False, False
barrelMoveMessage = None
movesCoords = {"UP": [0, -5], "DOWN": [0, 5], "LEFT": [-5, 0], "RIGHT": [5, 0]}
movesCoordsMoreSpeed = {"UP": [0, -7], "DOWN": [0, 7], "LEFT": [-7, 0], "RIGHT": [7, 0]}
movesCoordsSlow = {"UP": [0, -2], "DOWN": [0, 2], "LEFT": [-2, 0], "RIGHT": [2, 0]}
world_pos = 0
frames_count = 0
bullet_speed = 12
reload_timer = 0
reload_time = 120
graviti = 0.2

mag = 30
ammo = 120
pos = (860, 440)
viewBoard = [[0] * 11 for _ in range(11)]


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


menu = load_image("Menu.png")
menuExit = load_image("MenuButton0.png")
menuContinue = load_image("MenuButton1.png")


def escMenu():
    pygame.mouse.set_visible(True)
    pygame.init()
    pygame.font.init()
    size = width, height = 1920, 1080  # касаемо экрана
    screen = pygame.display.set_mode(size)

    screen.blit(menu, (0, 0))
    wasClick = False

    run = True
    while run:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
                return 0

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    run = False
                    return 0

            if event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:
                    pos = event.pos
                    if 473 <= pos[0] <= 1448 and 457 <= pos[1] <= 681:
                        screen.blit(menuExit, (0, 0))
                        wasClick = "EXIT"
                    elif 469 <= pos[0] <= 1449 and 713 <= pos[1] <= 941:
                        screen.blit(menuContinue, (0, 0))
                        wasClick = "GO"

            if event.type == pygame.MOUSEBUTTONUP:
                if event.button == 1 and wasClick == 'GO':
                    return pos
                elif event.button == 1 and wasClick == 'EXIT':
                    return wasClick

        pygame.display.flip()


class Player(pygame.sprite.Sprite):  # класс игрока
    image = load_image('player_calm.png')
    player_reverse = False
    health = 100
    adr_timer = 0
    speed = 12
    accuracy = 1
    score = 0

    def __init__(self, group):
        super().__init__(group)
        self.image = Player.image
        self.image = pygame.transform.scale(self.image, (200, 200))
        self.rect = self.image.get_rect()
        self.barrel = None
        self.lastBarrel = None
        self.deadTimer = 120
        self.health = Player.health

    def update(self):
        global movesCoords, movesCoordsMoreSpeed, movesCoordsSlow
        if self.adr_timer > 0:
            if self.adr_timer == 1:
                self.adr_timer -= 1
            self.adr_timer -= 1
            if not self.barrel:
                movesCoords = movesCoordsMoreSpeed.copy()
        if self.adr_timer < 0:
            self.accuracy = 1
            self.speed = 12
            self.adr_timer = 0
            self.health = int(((self.health / 120) * 100) // 1)
            if not moving_barrel:
                movesCoords = {"UP": [0, -5], "DOWN": [0, 5], "LEFT": [-5, 0], "RIGHT": [5, 0]}
                movesCoordsMoreSpeed = {"UP": [0, -7], "DOWN": [0, 7], "LEFT": [-7, 0], "RIGHT": [7, 0]}
                movesCoordsSlow = {"UP": [0, -2], "DOWN": [0, 2], "LEFT": [-2, 0], "RIGHT": [2, 0]}
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
        if self.barrel:
            movesCoords = movesCoordsSlow.copy()
            self.lastBarrel = self.barrel
        else:
            movesCoords = {"UP": [0, -5], "DOWN": [0, 5], "LEFT": [-5, 0], "RIGHT": [5, 0]}
        if self.lastBarrel:
            if not pygame.sprite.collide_mask(self, self.lastBarrel):
                self.lastBarrel = None
        elif self.adr_timer == 0:
            movesCoords = {"UP": [0, -5], "DOWN": [0, 5], "LEFT": [-5, 0], "RIGHT": [5, 0]}
        if self.health <= 0:
            gun.kill()
            self.health = 0
            self.deadTimer -= 1
        if self.deadTimer <= 0:
            self.kill()

    def move(self, mx, my):
        if self.health > 0:
            self.rect = self.rect.move(mx, my)
            chunk = chunks[1][1]
            for sprite in chunk.boxes + chunk.barrels:
                if sprite.alive():
                    if pygame.sprite.collide_mask(self, sprite) and not sprite is self.lastBarrel:
                        sprite.mask = pygame.mask.from_surface(
                            pygame.transform.scale(sprite.image, (
                                sprite.rect.w - 40, sprite.rect.h - 40
                            ))
                        )
                        if pygame.sprite.collide_mask(self, sprite):
                            self.rect = self.rect.move(-mx, -my)
                            sprite.mask = pygame.mask.from_surface(sprite.image)
                            break
                        sprite.mask = pygame.mask.from_surface(sprite.image)


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
    kd = 8
    kdNow = 0
    kdLive = 90

    def __init__(self, pos):
        if P_Bullet.kdNow == 8:
            m4_shot.stop()
        if P_Bullet.kdNow >= P_Bullet.kd:
            super().__init__(player_bullets)
            m4_shot.play()
            self.image = P_Bullet.image
            self.rect = self.image.get_rect()
            self.rect.center = player.rect.center
            self.mask = pygame.mask.from_surface(self.image)
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
            try:
                self.vx += random.choice(range(0 - player.accuracy, player.accuracy))
                self.vy += random.choice(range(0 - player.accuracy, player.accuracy))
            except IndexError:  # При подборе аптечки
                pass
            P_Bullet.kdNow = 0
            self.kdLiveNow = 0
        else:
            P_Bullet.kdNow += 1

    def update(self):
        self.rect = self.rect.move(self.vx, self.vy)
        if self.kdLiveNow < P_Bullet.kdLive:
            self.kdLiveNow += 1
        else:
            self.kill()


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
    image = pygame.transform.scale(load_image("flor.png"), (2000, 2000))

    def __init__(self, x, y):
        super().__init__(flors)
        self.image = Flor.image
        self.rect = self.image.get_rect()
        self.rect.x, self.rect.y = x, y


class BoardFlor():
    def __init__(self):
        for i in range(11):
            for j in range(11):
                viewBoard[i][j] = Flor((j - 5) * 2000, (i - 5) * 2000)

        self.playerNowX, self.playerNowY = 5, 5
        self.playerOldX, self.playerOldY = 5, 5

    def update(self):
        r = True
        for i in range(len(viewBoard)):
            for j in range(len(viewBoard[i])):
                fl = viewBoard[i][j]
                if fl.rect.x < player.rect.centerx < fl.rect.x + 2000 and \
                        fl.rect.y < player.rect.centery < fl.rect.y + 2000:
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
                    viewBoard[i][-1].rect.x = viewBoard[i][-2].rect.x + 2000
                    self.playerNowX += 1
            elif move[0] == -1:
                for i in range(len(viewBoard)):
                    viewBoard[i] = [viewBoard[i][-1]] + viewBoard[i][:-1]
                    viewBoard[i][0].rect.x = viewBoard[i][1].rect.x - 2000
                    self.playerNowX -= 1
            if move[1] == 1:
                viewBoard[:] = viewBoard[1:] + [viewBoard[0]]
                for fl in viewBoard[-1]:
                    fl.rect.y = viewBoard[-2][1].rect.y + 2000
                self.playerNowY += 1
            elif move[1] == -1:
                viewBoard[:] = [viewBoard[-1]] + viewBoard[:-1]
                for fl in viewBoard[0]:
                    fl.rect.y = viewBoard[1][1].rect.y - 2000
                self.playerNowY -= 1


class Message(pygame.sprite.Sprite):
    def __init__(self, imageName):
        super().__init__(messages)
        self.image = load_image(imageName)
        self.rect = self.image.get_rect()
        self.rect.x, self.rect.y = player.rect.x + 80, player.rect.y - 50


class Box(pygame.sprite.Sprite):
    image = pygame.transform.scale(load_image("box.png"), (200, 200))

    def __init__(self, x=None, y=None):
        super().__init__()
        randomValue = random.randint(100, 200)
        self.image = pygame.transform.scale(Box.image, (randomValue, randomValue))
        if random.choice((1, 0)) == 1:
            self.image = pygame.transform.flip(self.image, True, False)
        self.rect = self.image.get_rect()
        self.mask = pygame.mask.from_surface(self.image)
        self.hp = 5
        if x and y:
            self.rect.x, self.rect.y = x, y

    def update(self):
        if pygame.sprite.spritecollide(self, player_bullets, False):
            for blt in player_bullets:
                if pygame.sprite.collide_mask(self, blt):
                    blt.kill()
                    if self.hp <= 0:
                        pass
                    else:
                        self.hp -= 1
                        self.rect = self.rect.move(random.randint(-2, 3), random.randint(-2, 3))
                    break
        if self.hp <= 0:
            if random.randint(0, 12) > 9:
                Ammo(x=self.rect.x, y=self.rect.y)
            else:
                if random.randint(0, 12) > 9:
                    Adrinaline(x=self.rect.x, y=self.rect.y)
            player.score += 20
            boxes.remove(self)
            self.kill()
            for _ in range(random.choice(range(7, 9))):
                BoxParticles((self.rect.x, self.rect.y),
                             *[random.choice([-6, -5, -4, -3, 3, 4, 5, 6]) for __ in range(2)])


class BoxParticles(pygame.sprite.Sprite):
    pieces = [load_image(f"boxParticl{i}.png") \
              for i in range(1, 6)]

    def __init__(self, pos, dx, dy):
        super().__init__(particles)
        self.image = random.choice(self.pieces)
        self.rect = self.image.get_rect()
        self.velocity = [dx, dy]
        self.rect.x, self.rect.y = pos
        self.gravity = graviti
        self.live = 32

    def update(self):
        self.velocity[1] += self.gravity
        self.rect.x += self.velocity[0]
        self.rect.y += self.velocity[1]
        self.live -= 1
        if self.live <= 0:
            self.kill()


class Barrel(pygame.sprite.Sprite):
    image = pygame.transform.scale(load_image("barrel.png"), (200, 200))
    boom = load_image('boom.png')
    timer = 50
    k = 1

    def __init__(self, x=None, y=None, chunk=None):
        super().__init__()
        if random.choice((1, 0)) == 1:
            self.image = pygame.transform.flip(self.image, True, False)
        self.rand = random.choice((4, 3, 2, 1, 0))
        if self.rand == 1:
            self.image = rot_center(self.image, 90)
        elif self.rand == 2:
            self.image = rot_center(self.image, 270)
        self.rect = self.image.get_rect()
        self.mask = pygame.mask.from_surface(self.image)
        self.hp = 2
        self.timer = 50
        self.haveMoved = False
        if x and y:
            self.rect.x, self.rect.y = x, y
        if chunk:
            self.chunk = chunk
        else:
            self.chunk = None

    def update(self):
        global movesCoords, movesCoordsSlow, haveBarrelMoveMessage, barrelMoveMessage
        if self.timer == 49:
            blowing.play()
            for _ in range(random.choice(range(14, 19))):
                BarrelParticles((self.rect.centerx - 15, self.rect.centery - 15),
                                *[random.choice([-8, -7, -6, -5, 5, 6, 7, 8]) for __ in range(2)])
        if self.hp <= 0:
            if self.haveMoved:
                self.haveMoved = False
                player.barrel = None
            self.timer -= 1
            if self.timer == 49:
                self.chunk.barrels.pop(self.chunk.barrels.index(self))
            if self.timer <= 80:
                self.center = self.rect.center
                self.image = pygame.transform.scale(self.boom, (round(600 * self.k ** 2), round(600 * self.k ** 2)))
                self.rect = self.image.get_rect()
                self.mask = pygame.mask.from_surface(self.image)
                self.rect.center = self.center
                self.k -= 0.02
                if self.timer == 48:
                    for box in boxes:
                        if pygame.sprite.collide_mask(box, self):
                            box.hp = 0
                if self.timer == 40:
                    for barrel in barrels:
                        if not barrel is self:
                            if pygame.sprite.collide_mask(barrel, self):
                                barrel.hp = 0
                # if self.timer == 41:
                #     for car in carsGr:
                #         if pygame.sprite.collide_mask(car, self):
                #             car.hp = 0
        else:
            if pygame.sprite.collide_mask(self, player) and moving_barrel:
                if player.barrel is None or player.barrel is self:
                    if not self.haveMoved:
                        if self.chunk:
                            ind = self.chunk.barrels.index(self)
                            del self.chunk.barrels[ind]
                            self.chunk = None
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
                    self.haveMoved = True
                    player.barrel = self
                    self.move(*move)
            elif self.haveMoved:
                self.haveMoved = False
                player.barrel = None
                self.chunk = chunks[1][1]
                self.chunk.barrels.append(self)
            if pygame.sprite.collide_mask(self, player) and \
                    not moving_barrel:
                if not haveBarrelMoveMessage:
                    haveBarrelMoveMessage = True
                    barrelMoveMessage = Message("barrelMove.png")
        if self.hp == 0 and pygame.sprite.collide_mask(self, player) and self.timer == 48:
            player.health -= 48

        if pygame.sprite.spritecollide(self, emenies, False) and self.timer == 49:
            for guy in emenies:
                if pygame.sprite.collide_mask(self, guy):
                    guy.hp -= 50

        if self.timer <= 0:
            player.score += 50
            self.kill()

        if pygame.sprite.spritecollide(self, player_bullets, False):
            for blt in player_bullets:
                if pygame.sprite.collide_mask(self, blt):
                    blt.kill()
                    if self.hp <= 0:
                        pass
                    else:
                        self.hp -= 1
                        self.rect = self.rect.move(random.randint(-2, 3), random.randint(-2, 3))
                    break

    def move(self, mx, my):
        self.rect = self.rect.move(mx, my)
        if pos[0] <= 960:
            self.rect.centerx = player.rect.centerx + 50
            self.rect.centery = player.rect.centery
        else:
            self.rect.centerx = player.rect.centerx - 50
            self.rect.centery = player.rect.centery


class BarrelParticles(pygame.sprite.Sprite):
    pieces = [load_image(f"barrelParticl{i}.png") \
              for i in range(1, 6)]

    def __init__(self, pos, dx, dy):
        super().__init__(particles)
        self.image = random.choice(self.pieces)
        self.rect = self.image.get_rect()
        self.velocity = [dx, dy]
        self.rect.x, self.rect.y = pos
        if random.choice((0, 1)) == 1:
            self.gravity = graviti * -2
        else:
            self.gravity = graviti * 2
        self.live = 32

    def update(self):
        self.velocity[1] += self.gravity
        self.rect.x += self.velocity[0]
        self.rect.y += self.velocity[1]
        self.live -= 1
        if self.live <= 0:
            self.kill()


class Ammo(pygame.sprite.Sprite):
    image = pygame.transform.scale(load_image("ammo.png"), (150, 150))

    def __init__(self, x=None, y=None, chunk=None):
        super().__init__(ammoGr)
        self.image = Ammo.image
        self.rect = self.image.get_rect()
        self.mask = pygame.mask.from_surface(self.image)
        if x and y:
            self.rect.x, self.rect.y = x, y
        self.chunk = chunk

    def update(self):
        global ammo
        if pygame.sprite.collide_mask(player, self):
            ammo += 30
            player.score += 20
            self.kill()


class Adrinaline(pygame.sprite.Sprite):
    image = pygame.transform.scale(load_image('adr.png'), (100, 100))

    def __init__(self, x=None, y=None):
        super().__init__(adrLineGr)
        self.image = Adrinaline.image
        self.rect = self.image.get_rect()
        self.mask = pygame.mask.from_surface(self.image)
        if x and y:
            self.rect.x, self.rect.y = x, y

    def update(self):
        global movesCoords, movesCoordsMoreSpeed
        if pygame.sprite.collide_mask(self, player):
            player.health = 120
            player.adr_timer = 600
            player.speed = 15
            player.accuracy = 0
            movesCoords = movesCoordsMoreSpeed.copy()
            player.score += 20
            self.kill()


class AKM(pygame.sprite.Sprite):  # класс валыны
    image = pygame.transform.scale(load_image('ak.png'), (200, 200))

    def __init__(self, x, y, guy):
        super().__init__(AKS)
        self.image = AKM.image
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y
        self.guy = guy

    def update(self):
        self.player = player.rect.center
        self.player_x = self.player[0]
        self.player_y = self.player[1]
        self.self_x = self.rect.center[0]
        self.self_y = self.rect.center[1]
        self.sight_x = self.self_x - self.player_x
        self.sight_y = self.player_y - self.self_y
        if self.sight_x == 0:
            self.sight_x = 0.001
        self.tg = self.sight_y / self.sight_x

        self.angle = math.degrees(math.atan(self.tg))
        if self.sight_x > 0:
            self.image = pygame.transform.flip(AKM.image, True, False)
            self.image = rot_center(self.image, self.angle)
            self.rect = self.image.get_rect()
        else:
            self.image = rot_center(AKM.image, self.angle)
            self.rect = self.image.get_rect()
        self.rect.centerx = self.guy.rect.centerx + 10
        self.rect.centery = self.guy.rect.centery + 10

    def move(self, mx, my):
        self.rect = self.rect.move(mx, my)


class Enemy(pygame.sprite.Sprite):
    speed = 4
    pos1 = pygame.transform.scale(load_image('enemy1.png'), (200, 200))
    pos2 = pygame.transform.scale(load_image('enemy2.png'), (200, 200))
    walking = 0

    def __init__(self, x=None, y=None, chunk=None):
        super().__init__()
        self.say_bb = True
        self.say_hi = True
        self.hp = 100
        self.kd = 0
        self.image = self.pos1
        self.rect = self.image.get_rect()
        self.mask = pygame.mask.from_surface(self.image)
        self.chunk = chunk
        if x and y:
            self.rect.x, self.rect.y = x, y
        self.ak = AKM(self.rect.x, self.rect.y, self)

    def update(self):
        self.kd += 1
        if self.kd % 20 == 0:
            E_Bullet(self.rect.center)
        if pygame.sprite.spritecollide(self, player_bullets, False):
            for blt in player_bullets:
                if pygame.sprite.collide_mask(self, blt):
                    blt.kill()
                    self.hp -= 20
        if self.hp <= 0:
            self.voise = pygame.mixer.Sound(os.path.join('rip', random.choice(os.listdir('rip'))))
            self.voise.play()
            self.kill()
            AKS.remove(self.ak)
            self.ak.kill()
            player.score += 100
        if world_pos == 1:
            self.image = self.pos1
            self.mask = pygame.mask.from_surface(self.image)
        else:
            self.image = self.pos2
            self.mask = pygame.mask.from_surface(self.image)
        self.center = self.rect.center
        self.player = player.rect.center
        self.mx, self.my = self.center[0], self.center[1]
        self.px, self.py = self.player[0], self.player[1]
        self.dx = self.px - self.mx
        self.dy = self.py - self.my
        self.dr = ((self.dx ** 2) + (self.dy ** 2)) ** (1 / 2)
        if self.dr < 1000:

            if player.health <= 0 and self.say_bb:
                self.voise = pygame.mixer.Sound(os.path.join('killing', random.choice(os.listdir('killing'))))
                self.voise.play()
                self.say_bb = False
            if random.choice(range(2000)) == 1 or self.say_hi:
                self.say_hi = False
                self.voise = pygame.mixer.Sound(os.path.join('voises', random.choice(os.listdir('voises'))))
                self.voise.play()
        if 400 < self.dr < 1200 and self.walking == 0:
            self.move(self.speed * self.dx / self.dr, self.speed * self.dy / self.dr)
        elif self.walking != 0:
            self.walking -= 1
            if self.way == 'up':
                self.move(0, self.speed)
            if self.way == 'down':
                self.move(0, -self.speed)
            if self.way == 'right':
                self.move(self.speed, 0)
            if self.way == 'left':
                self.move(0 - self.speed, 0)
            if self.way == 'ur':
                self.move(self.speed * 0.75, self.speed * 0.75)
            if self.way == 'dr':
                self.move(self.speed * 0.75, -self.speed * 0.75)
            if self.way == 'dl':
                self.move(0 - self.speed * 0.75, -self.speed * 0.75)
            if self.way == 'ul':
                self.move(0 - self.speed * 0.75, self.speed * 0.75)
        else:
            self.walking = 25
            self.way = random.choice(('up', 'down', 'left', 'right', 'ur', 'dr', 'dl', 'ul'))
        if self.dx < 0:
            self.image = pygame.transform.flip(self.image, True, False)

    def move(self, x, y):
        self.rect = self.rect.move(x, y)
        if self.chunk:
            if not pygame.sprite.collide_mask(self, self.chunk):
                for row in chunks:
                    for chunk in row:
                        if pygame.sprite.collide_mask(self, chunk):
                            self.chunk = chunk
                            break
                for chunk in chunks:
                    if pygame.sprite.collide_mask(self, chunk):
                        self.chunk = chunk
                        break

class E_Bullet(pygame.sprite.Sprite):  # класс пулaи
    image = load_image('bullet.png')
    kd = 10
    kdNow = 0
    kdLive = 90

    def __init__(self, pos):
        if P_Bullet.kdNow == 8:
            ak_shot.stop()
        if P_Bullet.kdNow >= P_Bullet.kd:
            super().__init__(enemy_bullets)
            ak_shot.play()
            self.image = P_Bullet.image
            self.rect = self.image.get_rect()
            self.rect.center = pos
            self.mask = pygame.mask.from_surface(self.image)
            self.player = player.rect.center
            self.player_x = self.player[0]
            self.player_y = self.player[1]
            self.self_x = self.rect.center[0]
            self.self_y = self.rect.center[1]
            self.sight_x = self.player_x - self.self_x
            self.sight_y = self.player_y - self.self_y
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
            try:
                self.vx += random.choice(range(0 - player.accuracy, player.accuracy))
                self.vy += random.choice(range(0 - player.accuracy, player.accuracy))
            except IndexError:  # При подборе аптечки
                pass
            P_Bullet.kdNow = 0
            self.kdLiveNow = 0
        else:
            P_Bullet.kdNow += 1

    def update(self):
        if pygame.sprite.collide_mask(self, player):
            self.kill()
            player.health -= 10
        self.rect = self.rect.move(self.vx, self.vy)
        if self.kdLiveNow < P_Bullet.kdLive:
            self.kdLiveNow += 1
        else:
            self.kill()


# class Car(pygame.sprite.Sprite):
#     image = pygame.transform.scale(load_image("car.png"), (300, 300))
#     imageMask = pygame.transform.scale(load_image("carMask.png"), (300, 300))
#     boom = load_image('boom.png')
#     timer = 50
#     k = 1
#
#     def __init__(self, x=None, y=None, chunk=None):
#         super().__init__()
#         self.image = Car.image
#         self.imageMask = Car.imageMask
#         if random.choice((1, 0)) == 1:
#             self.image = pygame.transform.flip(self.image, True, False)
#         self.rect = self.image.get_rect()
#         self.mask = pygame.mask.from_surface(self.imageMask)
#         self.hp = 20
#         self.timer = 50
#         if x and y:
#             self.rect.x, self.rect.y = x, y
#         self.chunk = chunk
#
#     def update(self):
#         if self.hp <= 0:
#             self.timer -= 1
#             if self.timer <= 80:
#                 self.center = self.rect.center
#                 self.image = pygame.transform.scale(self.boom, (round(800 * self.k ** 2), round(800 * self.k ** 2)))
#                 self.rect = self.image.get_rect()
#                 self.mask = pygame.mask.from_surface(self.image)
#                 self.rect.center = self.center
#                 self.k -= 0.02
#                 if self.timer == 48:
#                     for box in boxes:
#                         if pygame.sprite.collide_mask(box, self):
#                             box.hp = 0
#                 if self.timer == 40:
#                     for barrel in barrels:
#                         if pygame.sprite.collide_mask(barrel, self):
#                             barrel.hp = 0
#                 if self.timer == 41:
#                     for car in carsGr:
#                         if not car is self:
#                             if pygame.sprite.collide_mask(car, self):
#                                 car.hp = 0
#         if self.hp == 0 and pygame.sprite.collide_mask(self, player) and self.timer == 48:
#             player.health -= 90
#
#         if self.timer <= 0:
#             self.kill()
#             player.score += 75
#
#         if pygame.sprite.spritecollide(self, player_bullets, False):
#             for blt in player_bullets:
#                 if pygame.sprite.collide_mask(self, blt):
#                     blt.kill()
#                     if self.hp <= 0:
#                         pass
#                     else:
#                         self.hp -= 1
#                         self.rect = self.rect.move(random.randint(-2, 3), random.randint(-2, 3))
#                     break
#

class Chunk(pygame.sprite.Sprite):
    def __init__(self, poss, x, y, rectx=None, recty=None):
        super().__init__()
        self.image = pygame.transform.scale(load_image("flor.png"), (1080, 1080))
        self.mask = pygame.mask.from_surface(self.image)
        self.rect = self.image.get_rect()
        if rectx is None and recty is None:
            self.rect.x, self.rect.y = [(1080 * x) - 860, (1080 * y) - 440]
        if rectx is not None and recty is not None:
            self.rect.x, self.rect.y = rectx, recty
        self.boxesValue = random.randrange(2, 4)
        self.boxes = []
        for i in range(self.boxesValue):  # Спавн коробок
            box = Box(x=random.randrange(self.rect.x, self.rect.x + 1080 - 300),
                      y=random.randrange(self.rect.y, self.rect.y + 1080 - 300))
            while pygame.sprite.spritecollide(box, self.boxes, False):
                box.kill()
                box = Box(x=random.randrange(self.rect.x, self.rect.x + 1080 - 300),
                          y=random.randrange(self.rect.y, self.rect.y + 1080 - 300))
            self.boxes.append(box)
            boxes.add(box)

        self.barrelsValue = random.randrange(1, 3)
        self.barrels = []
        for i in range(self.barrelsValue):  # Спавн бочек
            barl = Barrel(x=random.randrange(self.rect.x, self.rect.x + 1080 - 300),
                          y=random.randrange(self.rect.y, self.rect.y + 1080 - 300),
                          chunk=self)
            while pygame.sprite.spritecollide(barl, self.boxes, False) or \
                    pygame.sprite.spritecollide(barl, self.barrels, False):
                barl.kill()
                barl = Barrel(x=random.randrange(self.rect.x, self.rect.x + 1080 - 300),
                              y=random.randrange(self.rect.y, self.rect.y + 1080 - 300),
                              chunk=self)
            self.barrels.append(barl)
            barrels.add(barl)

        self.guysValue = random.choice([0, 1])
        self.guys = []
        for i in range(self.guysValue):  # Спавн врагов
            guy = Enemy(x=random.randrange(self.rect.x, self.rect.x + 1080 - 300),
                          y=random.randrange(self.rect.y, self.rect.y + 1080 - 300),
                          chunk=self)
            while pygame.sprite.spritecollide(guy, self.boxes, False) or \
                    pygame.sprite.spritecollide(guy, self.barrels, False):
                guy.ak.kill()
                guy.kill()
                guy = Enemy(x=random.randrange(self.rect.x, self.rect.x + 1080 - 300),
                              y=random.randrange(self.rect.y, self.rect.y + 1080 - 300),
                              chunk=self)
            self.guys.append(guy)
            emenies.add(guy)

        self.ammoValue = random.choice([0, 1, 2])
        self.ammo = []
        for i in range(self.ammoValue):  # Спавн патронов
            ammo = Ammo(x=random.randrange(self.rect.x, self.rect.x + 1080 - 300),
                        y=random.randrange(self.rect.y, self.rect.y + 1080 - 300),
                        chunk=self)
            while pygame.sprite.spritecollide(ammo, self.boxes, False) or \
                    pygame.sprite.spritecollide(ammo, self.barrels, False):
                ammo.kill()
                ammo = Ammo(x=random.randrange(self.rect.x, self.rect.x + 1080 - 300),
                            y=random.randrange(self.rect.y, self.rect.y + 1080 - 300),
                            chunk=self)
            self.ammo.append(ammo)
            ammoGr.add(ammo)

        # self.carsValue = random.randrange(0, 12)
        # if self.carsValue >= 11:
        #     self.carsValue = 2
        # elif self.carsValue >= 7:
        #     self.carsValue = 1
        # else:
        #     self.carsValue = 0
        # self.cars = []
        # for i in range(self.carsValue):
        #     car = Car(x=random.randrange(self.rect.x, self.rect.x + 1080 - 500),
        #               y=random.randrange(self.rect.y, self.rect.y + 1080 - 500),
        #               chunk=self)
        #     while pygame.sprite.spritecollide(car, self.boxes, False) or \
        #             pygame.sprite.spritecollide(car, self.barrels, False) or \
        #             pygame.sprite.spritecollide(car, self.cars, False):
        #         car.kill()
        #         car = Car(x=random.randrange(self.rect.x, self.rect.x + 1080 - 500),
        #                   y=random.randrange(self.rect.y, self.rect.y + 1080 - 500),
        #                   chunk=self)
        #     self.cars.append(car)
        #     carsGr.add(car)

        self.pos = poss
        self.playerIsHere = False

    def update(self):
        if pygame.sprite.collide_mask(player, self):
            playerChunkPosNow[:] = self.pos.copy()
            self.playerIsHere = True
        else:
            self.playerIsHere = False


player = Player(player_group)  # спрайты
gun = M4(guns)
clock = pygame.time.Clock()
camera = Camera()
boardFlor = BoardFlor()
playerChunkPosOld = [0, 0]
playerChunkPosNow = [0, 0]
scope = load_image('scope.png')

chunks = [[0, 0, 0], [0, 0, 0], [0, 0, 0]]
for i in range(3):
    for j in range(3):
        chunks[i][j] = Chunk([j - 1, i - 1], j - 1, i - 1)

while True:
    if not (any((moving_up, moving_down, moving_left, moving_right))):
        moving = False
        walking.stop()
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            terminate()

        if player.health > 0:
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_w:
                    moving_up = True
                    if moving is False:
                        walking.play()
                    moving = True
                if event.key == pygame.K_s:
                    moving_down = True
                    if moving is False:
                        walking.play()
                    moving = True
                if event.key == pygame.K_a:
                    moving_left = True
                    if moving is False:
                        walking.play()
                    moving = True
                if event.key == pygame.K_d:
                    moving_right = True
                    if moving is False:
                        walking.play()
                    moving = True
                if event.key == pygame.K_f:
                    moving_barrel = True
                if event.key == pygame.K_ESCAPE:
                    pos = escMenu()
                    if pos == 'EXIT':
                        terminate()
                    else:
                        guns.update(pos)
                        moving_up, moving_down, moving_left, \
                        moving_right, shooting, moving_barrel, haveBarrelMoveMessage = False, False, False, \
                                                                                       False, False, False, False
                        barrelMoveMessage = None
                        pygame.mouse.set_visible(False)

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
                if event.key == pygame.K_f:
                    moving_barrel = False

            if event.type == pygame.MOUSEMOTION:
                pos = event.pos
                gun.update(pos)

            if event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:
                    shooting = True

            if event.type == pygame.MOUSEBUTTONUP:
                if event.button == 1:
                    shooting = False
        else:
            moving_up, moving_down, moving_left, \
            moving_right, shooting, moving_barrel, haveBarrelMoveMessage = False, False, False, \
                                                                           False, False, False, False
            if barrelMoveMessage:
                barrelMoveMessage.kill()
            barrelMoveMessage = None

    camera.update(player)
    for group in all_gropus:
        if not group is messages:
            for sprite in group:
                camera.apply(sprite)
    for row in chunks:
        for chunk in row:
            camera.apply(chunk)

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

    frames_count += 1  # счетчик, используется для цикличной смены анимаций, например ходьба
    if (frames_count // 5) % 2 == 1:
        world_pos = 1
    else:
        world_pos = 0

    screen.fill("Black")
    for group in all_gropus:
        if not group is guns:
            group.update()
    guns.update(pos)
    boardFlor.update()
    for row in chunks:
        for chunk in row:
            chunk.update()

    for group in all_gropus:
        group.draw(screen)
    if player.health > 0:
        screen.blit(scope, (pos[0] - 50, pos[1] - 50))
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

    if player.health > 30:
        hp_info = mag_font.render(str(player.health), True, (220, 220, 220))
    else:
        hp_info = mag_font.render(str(player.health), True, (220, 20, 20))
    screen.blit(hp_info, (60, 925))
    score_info = mag_font.render(str(player.score), True, (220, 220, 50))
    screen.blit(score_info, (60, 30))

    if playerChunkPosNow != playerChunkPosOld:
        move = (
            playerChunkPosNow[0] - playerChunkPosOld[0],
            playerChunkPosNow[1] - playerChunkPosOld[1]
        )
        if move[0] == 1:
            for r in range(len(chunks)):
                row = chunks[r]
                delChunk = row.pop(0)

                for box in delChunk.boxes:
                    boxes.remove(box)
                    box.kill()
                for barrel in delChunk.barrels:
                    barrels.remove(barrel)
                    barrel.kill()

                delChunk.kill()
                chunks[r].append(Chunk([row[-1].pos[0] + 1, row[-1].pos[1]], 2, row[-1].pos[1],
                                       chunks[r][-1].rect.x + 1080, chunks[r][-1].rect.y))
        elif move[0] == -1:
            for r in range(len(chunks)):
                row = chunks[r]
                delChunk = row.pop(-1)

                for box in delChunk.boxes:
                    boxes.remove(box)
                    box.kill()
                for barrel in delChunk.barrels:
                    barrels.remove(barrel)
                    barrel.kill()

                delChunk.kill()
                chunks[r].insert(0, Chunk([row[0].pos[0] - 1, row[0].pos[1]], -1, row[0].pos[1],
                                          chunks[r][0].rect.x - 1080, chunks[r][0].rect.y))
        if move[1] == 1:
            row = chunks.pop(0)
            newRow = []
            for i in range(len(row)):
                delChunk = row[i]

                for box in delChunk.boxes:
                    boxes.remove(box)
                    box.kill()
                for barrel in delChunk.barrels:
                    barrels.remove(barrel)
                    barrel.kill()

                newRow.append(Chunk([delChunk.pos[0], chunks[-1][0].pos[1] + 1], delChunk.pos[0], 2,
                                    delChunk.rect.x, chunks[-1][0].rect.y + 1080))
                delChunk.kill()
            chunks.append(newRow)
        elif move[1] == -1:
            row = chunks.pop(-1)
            newRow = []
            for i in range(len(row)):
                delChunk = row[i]

                for box in delChunk.boxes:
                    boxes.remove(box)
                    box.kill()
                for barrel in delChunk.barrels:
                    barrels.remove(barrel)
                    barrel.kill()

                newRow.append(Chunk([delChunk.pos[0], chunks[0][0].pos[1] - 1], delChunk.pos[0], -1,
                                    delChunk.rect.x, chunks[0][0].rect.y - 1080))
                delChunk.kill()
            chunks.insert(0, newRow)

        playerChunkPosOld = playerChunkPosNow.copy()

    if not pygame.sprite.spritecollideany(player, barrels) and haveBarrelMoveMessage or \
            haveBarrelMoveMessage and moving_barrel:
        messages.remove(barrelMoveMessage)
        barrelMoveMessage.kill()
        barrelMoveMessage = None
        haveBarrelMoveMessage = False

    pygame.display.flip()
    clock.tick(60)
