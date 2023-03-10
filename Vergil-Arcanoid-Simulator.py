import os
import pygame
import sys
import random
from PIL import Image, ImageSequence
import cv2

pygame.mixer.pre_init(44100, -16, 2, 512)


# ---------------Обработка изображений и gif'ок, разделение последних на отдельные изображения
def pil_image_to_surface(pil_image):
    mode, size, data = pil_image.mode, pil_image.size, pil_image.tobytes()
    return pygame.image.fromstring(data, size, mode).convert_alpha()


def load_image(name, width, height, colorkey=None):
    fullname = os.path.join('data', name)
    if not os.path.isfile(fullname):
        print(f"Файл с изображением '{fullname}' не найден")
        sys.exit()
    if not fullname.endswith('.gif'):
        image = pygame.image.load(fullname)
        if colorkey is not None:
            image = image.convert()
            if colorkey == -1:
                colorkey = image.get_at((0, 0))
            image.set_colorkey(colorkey)
        else:
            image = image.convert_alpha()
        image = pygame.transform.scale(image, (height, width))
        return image
    pil_image = Image.open(fullname)
    frames = []
    if pil_image.format == 'GIF' and pil_image.is_animated:
        for frame in ImageSequence.Iterator(pil_image):
            frame = frame.resize((width, height))
            pygame_image = pil_image_to_surface(frame.convert('RGBA'))
            frames.append(pygame_image)
    else:
        frames.append(pil_image_to_surface(pil_image))
    return frames


# ----------------------------
# Класс иконки первой способности
class AbilityBox(pygame.sprite.Sprite):
    def __init__(self, pos, sprites):
        super().__init__(all_sprites)
        pygame.time.set_timer(10081, 1000)
        self.sprites = sprites
        self.image = self.sprites[0]
        self.currentFrame = 0
        self.rect = (self.image[self.currentFrame]).get_rect()
        self.currentFrame = (self.currentFrame + 1) % len(self.image)
        self.mask = pygame.mask.from_surface(self.image[self.currentFrame])
        self.rect.x = pos[0]
        self.rect.y = pos[1]
        self.add(buttons)

    def update(self):
        screen.blit(self.image[self.currentFrame], self.rect)
        self.currentFrame = (self.currentFrame + 1) % len(self.image)


# Основной класс первой способности
class Ball(pygame.sprite.Sprite):
    def __init__(self, pos, sprites):
        super().__init__(all_sprites)
        pygame.time.set_timer(10081, 1000, 1)
        self.sprites = sprites
        self.image = self.sprites[0]
        self.currentFrame = 0
        self.rect = (self.image[self.currentFrame]).get_rect()
        self.currentFrame = (self.currentFrame + 1) % len(self.image)
        self.mask = pygame.mask.from_surface(self.image[self.currentFrame])
        self.rect.x = pos[0]
        self.rect.y = pos[1]
        self.add(balls)

    def update(self):
        screen.blit(self.image[self.currentFrame], self.rect)
        self.currentFrame = (self.currentFrame + 1) % len(self.image)


# Класс progress bar'а, показывающего, сколько осталось до следующего ранга
class RankBar:
    def __init__(self, pos):
        super().__init__()
        self.rank = 0
        self.percentage_of_rank = 0
        self.x = pos[0]
        self.y = pos[1]

    def update(self):
        if 1 < self.rank < 6:
            pygame.draw.rect(screen, (80, 80, 80), pygame.Rect(self.x, self.y, 200, 20))
            pygame.draw.rect(screen, (15, 141, 255), pygame.Rect(self.x, self.y, 200 * self.percentage_of_rank, 20))
            pygame.draw.rect(screen, (0, 0, 0), pygame.Rect(self.x, self.y, 200, 20), 2)
        elif self.rank >= 6:
            pygame.draw.rect(screen, (80, 80, 80), pygame.Rect(self.x, self.y, 200, 20))
            pygame.draw.rect(screen, (252, 204, 22), pygame.Rect(self.x, self.y, 200 * self.percentage_of_rank, 20))
            pygame.draw.rect(screen, (0, 0, 0), pygame.Rect(self.x, self.y, 200, 20), 2)


# Класс, показывающий текущий ранг. Использует разделённые ранее гифки
class RankVisualisation:
    def __init__(self, pos, sprites):
        super().__init__()
        self.sprites = sprites
        self.image = self.sprites[0]
        self.currentFrame = 0
        self.rect = (self.image[self.currentFrame]).get_rect()
        self.currentFrame = (self.currentFrame + 1) % len(self.image)
        self.mask = pygame.mask.from_surface(self.image[self.currentFrame])
        self.rect.x = pos[0]
        self.rect.y = pos[1]
        self.rank = -1

    def update(self):
        screen.blit(self.image[self.currentFrame], self.rect)
        self.currentFrame = (self.currentFrame + 1) % len(self.image)
        if self.rank == 2:
            self.image = self.sprites[0]
            self.currentFrame = 315
        elif self.rank == 3:
            self.image = self.sprites[2]
        elif self.rank == 4:
            self.image = self.sprites[4]
        elif self.rank == 5:
            self.image = self.sprites[6]
        elif self.rank == 6:
            self.image = self.sprites[8]
        elif self.rank == 7:
            self.image = self.sprites[10]
        elif self.rank == 8:
            self.image = self.sprites[12]


"""
Класс вертикальной и горизонтальной границы (плитки от горизонтальной границы пропадают,
а от вертикальной отталкиваются).
Вергилий при прохождении через вертикальную границу телепортируется на другую сторону.
"""


class Border(pygame.sprite.Sprite):
    def __init__(self, x1, y1, x2, y2):
        super().__init__(all_sprites)
        if x1 == x2:
            self.add(vertical_borders)
            self.image = pygame.Surface([500, y2 - y1])
            self.rect = pygame.Rect(x1, y1, x2, y2 - y1)
        else:
            self.add(horizontal_borders)
            self.image = pygame.Surface([x2 - x1, 1])
            self.rect = pygame.Rect(x1, y1, x2 - x1, 1)


"""
Основной класс плиток. Имеет в себе несколько эффектов (ускорение, кручение, отталкивание)
"""


class BaseBox(pygame.sprite.Sprite):
    def __init__(self, pos):
        super().__init__(all_sprites)
        self.index = 1
        self.add(boxes)
        self.pos = pos
        self.image = load_image("gek.png", 100, 300)
        self.effect = random.randint(1, 5)
        self.touched = 0
        self.angle = 0
        self.speed = 3
        self.imagea = 0
        self.sidemovem = 0
        if self.effect == 1:
            self.imagec = self.image.copy()
            self.image.set_alpha(0)
        elif self.effect == 2:
            self.speed = 5
        elif self.effect == 3:
            self.sidemove = -1
        if self.effect == 1:
            self.rect = self.imagec.get_rect()
            self.mask = pygame.mask.from_surface(self.imagec)
        else:
            self.rect = self.image.get_rect()
            self.mask = pygame.mask.from_surface(self.image)
        self.rect.x = self.pos[0]
        self.rect.y = self.pos[1]
        self.buttonbox_create = random.randint(1, 6)
        if self.buttonbox_create == 1:
            global spawnbox_ready
            spawnbox_ready = True
            self.kill()

    def update(self):
        if self.effect == 1:
            self.imagea = pygame.transform.rotate(self.imagec, self.angle)
            self.angle += 1
            self.angle = self.angle % 360
            x, y = self.rect.center
            self.rect = self.imagea.get_rect()
            self.rect.center = (x, y)
            screen.blit(self.imagea, self.rect)
        if self.effect == 3:
            if self.sidemove < 0:
                self.sidemovem = 3
            elif self.sidemove > 200:
                self.sidemovem = -3
            if self.sidemovem == 3:
                self.sidemove += 1
            elif self.sidemovem == -3:
                self.sidemove -= 1
        if not pygame.sprite.collide_mask(self, vergil):
            self.rect = self.rect.move(self.sidemovem, self.speed * worlds)
        else:
            self.touched = 1
        if not pygame.sprite.collide_mask(self, vc):
            self.rect = self.rect.move(self.sidemovem, self.speed * worlds)
        else:
            self.touched = 1
        if pygame.sprite.spritecollideany(self, vertical_borders):
            self.sidemovem = -self.sidemovem
        if pygame.sprite.spritecollideany(self, horizontal_borders):
            global rank_score
            if rank_score > 1 and can_shrink:
                rank_score -= 1
            self.kill()

    def touch(self):
        return self.touched

    def spawn_check(self):
        for elem in boxes:
            if elem is self:
                continue
            elif pygame.sprite.collide_mask(self, elem):
                self.kill()
                global spawnwait
                spawnwait = 40


"""
Класс плитки с кнопокой
"""


class ButtonBox(pygame.sprite.Sprite):
    def __init__(self, pos):
        super().__init__(all_sprites)
        self.index = 2
        self.add(boxes)
        self.pos = pos
        self.image = load_image("gek.png", 100, 300)
        self.speed = 3
        self.rect = self.image.get_rect()
        self.mask = pygame.mask.from_surface(self.image)
        self.imagebb = pygame.Surface((160, 60))
        self.imagebb.fill((0, 0, 0))
        self.rectbb = self.imagebb.get_rect()
        self.maskbb = pygame.mask.from_surface(self.image)
        self.imageb = pygame.Surface((150, 50))
        self.imageb.fill((170, 170, 170))
        self.rectb = self.imageb.get_rect()
        self.maskb = pygame.mask.from_surface(self.image)
        self.rect.x = self.pos[0]
        self.rect.y = self.pos[1]
        self.rectb.x = self.pos[0] + 75
        self.rectb.y = self.pos[1] + 25
        self.rectbb.x = self.rectb.x - 5
        self.rectbb.y = self.rectb.y - 5
        self.readytotouch = False
        self.touched = 0

    def update(self):
        if pygame.sprite.spritecollideany(self, horizontal_borders):
            global rank_score
            if rank_score > 2 and can_shrink:
                rank_score -= 2
            self.kill()
        mouse_pos = pygame.mouse.get_pos()
        self.image.blit(self.imagebb, (70, 20))
        self.imagebb.blit(self.imageb, (5, 5))
        if self.rectb.collidepoint(mouse_pos):
            if pygame.mouse.get_pressed(num_buttons=3)[0]:
                self.readytotouch = True
        if self.readytotouch and pygame.sprite.collide_mask(self, vergil):
            self.touched = 2
        elif self.readytotouch and pygame.sprite.collide_mask(self, vc):
            self.touched = 2
        else:
            self.rect = self.rect.move(0, self.speed * worlds)
            self.rectb = self.rectb.move(0, self.speed * worlds)
            self.rectbb = self.rectb.move(0, self.speed * worlds)

    def touch(self):
        return self.touched

    def spawn_check(self):
        for elem in boxes:
            if elem is self:
                continue
            elif pygame.sprite.collide_mask(self, elem):
                self.kill()
                global spawnbox_ready
                spawnbox_ready = True


"""
Класс самого Вергилия (главного персонажа). Имеет несколько анимаций также подгружаемых из гифок. При движении в одну
из сторон, он набирает ускорение.
"""


class Vergil(pygame.sprite.Sprite):
    def __init__(self, pos, sprites):
        super().__init__(main_char)
        self.action = "standing"
        self.sprites = sprites
        self.image = self.sprites[0]
        self.currentFrame = 0
        self.rect = (self.image[self.currentFrame]).get_rect()
        self.currentFrame = (self.currentFrame + 1) % len(self.image)
        self.mask = pygame.mask.from_surface(self.image[self.currentFrame])
        self.rect.x = pos[0]
        self.rect.y = pos[1]
        self.acceleration = 0
        self.rank = -1

    def update(self):
        screen.blit(self.image[self.currentFrame], self.rect)
        self.currentFrame = (self.currentFrame + 1) % len(self.image)
        keys = pygame.key.get_pressed()
        if tpstun:
            pos = (self.rect.x, self.rect.y)
            self.rect = (self.image[self.currentFrame]).get_rect()
            self.rect.x = pos[0]
            self.rect.y = pos[1]
            self.action = "after tp"
        if not tpstun:
            if keys[pygame.K_a]:
                if self.acceleration > 0:
                    self.acceleration -= 0.8
                elif self.acceleration >= -15:
                    self.acceleration -= 0.4
                if rank == 0:
                    self.rect.x -= 15 - self.acceleration
                elif self.rank <= 2:
                    self.rect.x -= 5 - self.acceleration
                elif 2 < self.rank < 5:
                    self.rect.x -= 10 - self.acceleration
                elif self.rank == 5:
                    self.rect.x -= 15 - self.acceleration
                else:
                    self.rect.x -= 30 - self.acceleration
                if self.action != "running left":
                    self.image = self.sprites[1]
                    self.currentFrame = 0
                    pos = (self.rect.x, self.rect.y)
                    self.rect = (self.image[self.currentFrame]).get_rect()
                    self.rect.x = pos[0]
                    self.rect.y = pos[1]
                    self.action = "running left"
            elif keys[pygame.K_d]:
                if self.acceleration < 0:
                    self.acceleration += 0.8
                if self.acceleration <= 15:
                    self.acceleration += 0.4
                if self.rank == 0:
                    self.rect.x += 15 + self.acceleration
                elif self.rank <= 2:
                    self.rect.x += 5 + self.acceleration
                elif 2 < self.rank < 5:
                    self.rect.x += 10 + self.acceleration
                elif self.rank == 5:
                    self.rect.x += 15 + self.acceleration
                else:
                    self.rect.x += 30 + self.acceleration
                if self.action != "running right":
                    self.image = self.sprites[2]
                    self.currentFrame = 0
                    pos = (self.rect.x, self.rect.y)
                    self.rect = (self.image[self.currentFrame]).get_rect()
                    self.rect.x = pos[0]
                    self.rect.y = pos[1]
                    self.action = "running right"
            else:
                if -0.4 <= self.acceleration <= 0.4:
                    self.acceleration = 0
                elif self.acceleration < 0:
                    self.acceleration += 0.6
                    self.rect.x += self.acceleration
                elif self.acceleration > 0:
                    self.acceleration -= 0.6
                    self.rect.x += self.acceleration
                if self.action != "standing":
                    self.image = self.sprites[0]
                    self.currentFrame = 0
                    pos = (self.rect.x, self.rect.y)
                    self.rect = (self.image[self.currentFrame]).get_rect()
                    self.rect.x = pos[0]
                    self.rect.y = pos[1]
                    self.action = "standing"
        if pygame.sprite.spritecollideany(self, vertical_borders):
            if self.rect.x < width // 2:
                self.rect.x = width - 300
            else:
                self.rect.x = 100


"""
Класс двойника Вергилия. Он появляется недалеко от Вергилия и охотится за самыми нижними плитками. Тажкже имеет 
несколько анимаций.
"""


class VergilClone(pygame.sprite.Sprite):
    def __init__(self, pos, sprites):
        super().__init__(vcg)
        self.action = "standing"
        self.sprites = sprites
        self.image = self.sprites[0]
        self.currentFrame = 0
        self.rect = (self.image[self.currentFrame]).get_rect()
        self.currentFrame = (self.currentFrame + 1) % len(self.image)
        self.mask = pygame.mask.from_surface(self.image[self.currentFrame])
        self.rect.x = pos[0]
        self.rect.y = pos[1]
        pygame.time.set_timer(10091, 20000, 1)
        self.point = -1000
        self.rank = -1

    def update(self):
        screen.blit(self.image[self.currentFrame], self.rect)
        self.currentFrame = (self.currentFrame + 1) % len(self.image)
        if sabilityready:
            max_y = []
            for box in boxes:
                max_y.append(box.rect.y)
            if max_y:
                for box in boxes:
                    if box.rect.y == max(max_y):
                        self.point = box.rect.x
        else:
            self.point = -1000
            self.rect.x = -1000
        if sabilityalive:
            if self.point + 100 > self.rect.x > self.point:
                if self.action != "standing":
                    self.image = self.sprites[2]
                    self.currentFrame = 0
                    pos = (self.rect.x, self.rect.y)
                    self.rect = (self.image[self.currentFrame]).get_rect()
                    self.rect.x = pos[0]
                    self.rect.y = pos[1]
                    self.action = "standing"
            elif self.rect.x > self.point:
                if self.action != "running left":
                    self.image = self.sprites[1]
                    self.currentFrame = 0
                    pos = (self.rect.x, self.rect.y)
                    self.rect = (self.image[self.currentFrame]).get_rect()
                    self.rect.x = pos[0]
                    self.rect.y = pos[1]
                    self.action = "running left"
                if rank == 0:
                    self.rect.x -= 15
                if rank <= 2:
                    self.rect.x -= 10
                elif 2 < rank < 5:
                    self.rect.x -= 13
                elif rank == 5:
                    self.rect.x -= 15
                else:
                    self.rect.x -= 20
            elif self.rect.x < self.point:
                if self.action != "running right":
                    self.image = self.sprites[0]
                    self.currentFrame = 0
                    pos = (self.rect.x, self.rect.y)
                    self.rect = (self.image[self.currentFrame]).get_rect()
                    self.rect.x = pos[0]
                    self.rect.y = pos[1]
                    self.action = "running right"
                if rank == 0:
                    self.rect.x += 15
                elif rank <= 2:
                    self.rect.x += 10
                elif 2 < rank < 5:
                    self.rect.x += 13
                elif rank == 5:
                    self.rect.x += 15
                else:
                    self.rect.x += 20
            else:
                if self.action != "standing":
                    self.image = self.sprites[0]
                    self.currentFrame = 0
                    pos = (self.rect.x, self.rect.y)
                    self.rect = (self.image[self.currentFrame]).get_rect()
                    self.rect.x = pos[0]
                    self.rect.y = pos[1]
                    self.action = "standing"


"""
Класс кнопки. Имеет два типа: 0 - для главного меню, 1 - для паузы
"""


class Button():
    def __init__(self, x, y, width, height, buttonText, onclickFunction, type=0):
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.type = type
        self.onclickFunction = onclickFunction
        self.buttonText = buttonText
        self.flicked = False
        self.buttonSurface = pygame.Surface((self.width, self.height))
        self.buttonRect = pygame.Rect(self.x, self.y, self.width, self.height)
        self.alreadyPressed = False
        self.buttonSurf = None
        objects.append(self)

    def process(self):
        mouse_pos = pygame.mouse.get_pos()
        self.buttonSurface = self.buttonSurface.convert_alpha()
        if not self.buttonRect.collidepoint(mouse_pos):
            self.buttonSurface.fill((0, 0, 0, 0))
            font = pygame.font.Font('data/font/DMC5Font.otf', 45)
            self.buttonSurf = font.render(self.buttonText, True, (255, 255, 255))
            self.flicked = False
        if self.buttonRect.collidepoint(mouse_pos):
            self.buttonSurface.fill((0, 39, 62, 0))
            if self.type == 0:
                shape_surf = pygame.Surface(pygame.Rect(0, self.y, pygame.display.Info().current_w, self.height).size,
                                            pygame.SRCALPHA)
            else:
                shape_surf = pygame.Surface(
                    pygame.Rect(0, self.y, pygame.display.Info().current_w / 3.912, self.height).size,
                    pygame.SRCALPHA)
            pygame.draw.rect(shape_surf, (0, 39, 62, 230), shape_surf.get_rect())
            if self.type == 0:
                screen.blit(shape_surf, (0, self.y, pygame.display.Info().current_w, self.height))
            else:
                screen.blit(shape_surf, (self.x - 25, self.y, pygame.display.Info().current_w, self.height))
            font = pygame.font.Font('data/font/DMC5Font.otf', 55)
            if not self.flicked:
                pygame.mixer.Sound('data/sounds/flicking sound.ogg').play()
                self.flicked = True
            self.buttonSurf = font.render(self.buttonText, True, (124, 255, 255))
            if pygame.mouse.get_pressed(num_buttons=3)[0]:
                if not self.alreadyPressed:
                    self.onclickFunction()
                    if self.type == 0:
                        pygame.mixer.Sound('data/sounds/enter sound.ogg').play()
                    else:
                        pygame.mixer.Sound('data/sounds/enter sound(alt).ogg').play()
                    self.alreadyPressed = True
            else:
                self.alreadyPressed = False
        self.buttonSurface.blit(self.buttonSurf, [
            self.buttonRect.width / 2 - self.buttonSurf.get_rect().width / 2,
            self.buttonRect.height / 2 - self.buttonSurf.get_rect().height / 2])
        screen.blit(self.buttonSurface, self.buttonRect)


"""
Функция музыки. Вызывется из ивента либо принудительно (в зависимости от ранга). Имеет несколько вариаций
"""


def music_player(style_rank, badass_progress, lst_rank, s_progress, tutorial=False):
    a = random.randint(0, 1)
    b = random.randint(0, 2)
    if tutorial and rank == 0:
        pygame.mixer.music.load("data/music/bury_the_light_intro.ogg")
        pygame.mixer.music.play(1)
    elif not tutorial and rank == -1:
        pygame.mixer.music.load("data/music/bury_the_light_no_damage.ogg")
        pygame.mixer.music.play(1)
    elif not tutorial and rank == 0:
        pygame.mixer.music.load("data/music/bury_the_light_intro.ogg")
        pygame.mixer.music.play(1, 82)
    elif style_rank == 1:
        pygame.mixer.music.load("data/music/bury_the_light_no_rank.ogg")
        pygame.mixer.music.play(1)
    elif style_rank == 2 and lst_rank == 1:
        skip = pygame.mixer.music.get_pos()
        try:
            if a == 0:
                pygame.mixer.music.load('data/music/bury_the_light_dismal_1.ogg')
                pygame.mixer.music.play(1, skip / 1000)
            elif a == 1:
                pygame.mixer.music.load('data/music/bury_the_light_dismal_2.ogg')
                pygame.mixer.music.play(1, skip / 1000)
        except ValueError:
            if a == 0:
                pygame.mixer.music.load('data/music/bury_the_light_dismal_1.ogg')
                pygame.mixer.music.play(1)
            elif a == 1:
                pygame.mixer.music.load('data/music/bury_the_light_dismal_2.ogg')
                pygame.mixer.music.play(1)
    elif style_rank == 2 and lst_rank != 1:
        if a == 0:
            pygame.mixer.music.load('data/music/bury_the_light_dismal_1.ogg')
            pygame.mixer.music.play(1)
        elif a == 1:
            pygame.mixer.music.load('data/music/bury_the_light_dismal_2.ogg')
            pygame.mixer.music.play(1)
    elif style_rank == 3 and b == 0:
        pygame.mixer.music.load("data/music/bury_the_light_crazy_1.ogg")
        pygame.mixer.music.play(1)
    elif style_rank == 3 and b == 1:
        pygame.mixer.music.load("data/music/bury_the_light_crazy_2.ogg")
        pygame.mixer.music.play(1)
    elif style_rank == 3 and b == 2:
        pygame.mixer.music.load("data/music/bury_the_light_crazy_3.ogg")
        pygame.mixer.music.play(1)
    elif style_rank == 4 and badass_progress == 0:
        pygame.mixer.music.load("data/music/bury_the_light_badass_1.ogg")
        pygame.mixer.music.play(1)
    elif style_rank == 4 and badass_progress == 1:
        pygame.mixer.music.load("data/music/bury_the_light_badass_2.ogg")
        pygame.mixer.music.play(1)
    elif style_rank == 4 and badass_progress == 2:
        pygame.mixer.music.load("data/music/bury_the_light_badass_3.ogg")
        pygame.mixer.music.play(1)
    elif style_rank == 5:
        pygame.mixer.music.load("data/music/bury_the_light_apocalyptic.ogg")
        pygame.mixer.music.play(1)
    elif style_rank >= 6 and s_progress == 0:
        pygame.mixer.music.load("data/music/bury_the_light_s1.ogg")
        pygame.mixer.music.play(1)
    elif style_rank >= 6 and s_progress == 1:
        pygame.mixer.music.load("data/music/bury_the_light_s2.ogg")
        pygame.mixer.music.play(1)
    elif style_rank >= 6 and s_progress == 2:
        pygame.mixer.music.load("data/music/bury_the_light_s3.ogg")
        pygame.mixer.music.play(1)
    elif style_rank >= 6 and s_progress == 3:
        pygame.mixer.music.load("data/music/bury_the_light_s4.ogg")
        pygame.mixer.music.play(1)
    elif style_rank >= 6 and s_progress == 4:
        pygame.mixer.music.load("data/music/bury_the_light_s5.ogg")
        pygame.mixer.music.play(1)
    elif style_rank >= 6 and s_progress == 5:
        pygame.mixer.music.load("data/music/bury_the_light_s6.ogg")
        pygame.mixer.music.play(1)
    elif style_rank >= 6 and s_progress == 6:
        pygame.mixer.music.load("data/music/bury_the_light_s7.ogg")
        pygame.mixer.music.play(1)


"""
Звук для первой способности
"""


def judgement_cut():
    c = pygame.mixer.Sound("data/sounds/judgement_cut_sound.ogg")
    c.play()
    if fabilityused % 3 == 0:
        a = pygame.mixer.Sound("data/sounds/jackpot.ogg")
        a.play()

"""
Звук для второй способности
"""


def doppleganger():
    c = pygame.mixer.Sound("data/sounds/doppleganger_spawn.ogg")
    c.play()

"""
Звук для третьей способности
"""


def judgement_cut_end():
    pygame.mixer.Sound("data/sounds/judgement_cut_end_1.ogg").play()
    pygame.mixer.Sound("data/sounds/you_shall_die.ogg").play()


"""
Случайные диалоги, который Вергилий произносит с некоторым интервалом
"""


def random_dialogues():
    a = random.randint(0, 5)
    if a == 0:
        s = pygame.mixer.Sound("data/sounds/show_me_your_motivation.ogg")
        s.play()
    elif a == 1:
        s = pygame.mixer.Sound("data/sounds/out_of_my_way.ogg")
        s.play()
    elif a == 2:
        s = pygame.mixer.Sound("data/sounds/scum.ogg")
        s.play()
    elif a == 3:
        s = pygame.mixer.Sound("data/sounds/how_boring.ogg")
        s.play()
    elif a == 4:
        s = pygame.mixer.Sound("data/sounds/your_wasting_my_time.ogg")
        s.play()
    elif a == 5:
        s = pygame.mixer.Sound("data/sounds/now_im_a_little_motivated.ogg")
        s.play()


"""
При переходе на следующий ранг, будет вызываться звук ранга (Dismal, Crazy...). Имеет по две вариации
"""


def rank_announcer(style_rank, visualisation_sprites):
    a = random.randint(0, 1)
    visualisator.rank = -1
    visualisator.currentFrame = 0
    if a == 0:
        if style_rank == 2:
            visualisator.image = visualisation_sprites[0]
            pygame.mixer.Sound('data/sounds/dismal1.ogg').play()
        elif style_rank == 3:
            visualisator.image = visualisation_sprites[1]
            pygame.mixer.Sound('data/sounds/crazy1.ogg').play()
        elif style_rank == 4:
            visualisator.image = visualisation_sprites[3]
            pygame.mixer.Sound('data/sounds/badass1.ogg').play()
        elif style_rank == 5:
            visualisator.image = visualisation_sprites[5]
            pygame.mixer.Sound('data/sounds/apocalyptic1.ogg').play()
        elif style_rank == 6:
            visualisator.image = visualisation_sprites[7]
            pygame.mixer.Sound('data/sounds/savage1.ogg').play()
        elif style_rank == 7:
            visualisator.image = visualisation_sprites[9]
            pygame.mixer.Sound('data/sounds/sick_skills1.ogg').play()
        elif style_rank == 8:
            visualisator.image = visualisation_sprites[11]
            pygame.mixer.Sound('data/sounds/smokin_sexy_style1.ogg').play()
    else:
        if style_rank == 2:
            visualisator.image = visualisation_sprites[0]
            pygame.mixer.Sound('data/sounds/dismal2.ogg').play()
        elif style_rank == 3:
            visualisator.image = visualisation_sprites[1]
            pygame.mixer.Sound('data/sounds/crazy2.ogg').play()
        elif style_rank == 4:
            visualisator.image = visualisation_sprites[3]
            pygame.mixer.Sound('data/sounds/badass2.ogg').play()
        elif style_rank == 5:
            visualisator.image = visualisation_sprites[5]
            pygame.mixer.Sound('data/sounds/apocalyptic2.ogg').play()
        elif style_rank == 6:
            visualisator.image = visualisation_sprites[7]
            pygame.mixer.Sound('data/sounds/savage2.ogg').play()
        elif style_rank == 7:
            visualisator.image = visualisation_sprites[9]
            pygame.mixer.Sound('data/sounds/sick_skills2.ogg').play()
        elif style_rank == 8:
            visualisator.image = visualisation_sprites[11]
            pygame.mixer.Sound('data/sounds/smokin_sexy_style2.ogg').play()


"""
Катсцена и звуки для третьей способности
"""


def third_ability(rank, times_played, last_rs, s_progress, intro_playing):
    video = cv2.VideoCapture("data/storm that is approaching.mp4")
    fps = video.get(cv2.CAP_PROP_FPS)
    fpsClock = pygame.time.Clock()
    clock = pygame.time.Clock()
    MUSIC_END = pygame.USEREVENT + 1
    pygame.mixer.music.set_endevent(MUSIC_END)
    pygame.mixer.music.set_volume(0.5)
    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == MUSIC_END:
                intro_playing = False
                if rank == -1:
                    rank = 0
                    music_player(rank, times_played, last_rs, s_progress)
                    intro_playing = True
                elif rank == 0:
                    rank = 1
                    music_player(rank, times_played, last_rs, s_progress)
                if rank == 4:
                    times_played += 1
                    music_player(rank, times_played, last_rs, s_progress)
                    if times_played == 3:
                        times_played = 0
                        music_player(rank, times_played, last_rs, s_progress)
                if rank >= 6:
                    s_progress += 1
                    music_player(rank, times_played, last_rs, s_progress)
                    if s_progress == 7:
                        s_progress = 0
                        music_player(rank, times_played, last_rs, s_progress)
                else:
                    music_player(rank, times_played, last_rs, s_progress)
        success, video_image = video.read()
        if success:
            video_surf = pygame.image.frombuffer(
                video_image.tobytes(), video_image.shape[1::-1], "BGR")
            screen.blit(video_surf, (0, 0))
        else:
            break
        fpsClock.tick(fps)
        pygame.display.flip()


"""
Функция паузы на esc. Заглушает музыку, приостанавливает основной цикл другим циклом.
"""


def pause(objects, rank, times_played, last_rs, s_progress, intro_playing):
    def game_continue():
        ev = pygame.event.Event(1001)
        pygame.event.post(ev)

    def exit_to_menu():
        ev = pygame.event.Event(1002)
        pygame.event.post(ev)

    def exit():
        pygame.quit()
        sys.exit()

    Button(width / 8 - 200, height * 0.2, 400, 60, 'Continue', game_continue, 1)
    Button(width / 8 - 200, height * 0.4, 400, 60, 'Main menu', exit_to_menu, 1)
    Button(width / 8 - 200, height * 0.5, 400, 60, 'Exit to desktop', exit, 1)
    begin = False
    running = True
    s = pygame.Surface((width, height))
    s.fill((80, 80, 80))
    transparency = 0
    MUSIC_END = pygame.USEREVENT + 1
    pygame.mixer.music.set_endevent(MUSIC_END)
    pygame.mixer.music.set_volume(0.5)
    slide = 0
    while running:
        if begin:
            pygame.mixer.music.set_volume(1)
            break
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == 1001:
                begin = True
            if event.type == 1002:
                return 1
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    pygame.mixer.Sound("data/sounds/escape sound.ogg").play()
                    begin = True
            if event.type == MUSIC_END:
                if rank == -1:
                    rank = 0
                    music_player(rank, times_played, last_rs, s_progress)
                elif rank == 0:
                    rank = 1
                    music_player(rank, times_played, last_rs, s_progress)
                if rank == 4:
                    times_played += 1
                    music_player(rank, times_played, last_rs, s_progress)
                    if times_played == 3:
                        times_played = 0
                        music_player(rank, times_played, last_rs, s_progress)
                if rank >= 6:
                    s_progress += 1
                    music_player(rank, times_played, last_rs, s_progress)
                    if s_progress == 7:
                        s_progress = 0
                        music_player(rank, times_played, last_rs, s_progress)
                else:
                    music_player(rank, times_played, last_rs, s_progress)
        s = pygame.Surface((width, height))
        s.fill((80, 80, 80))
        if transparency <= 3:
            transparency += 1.5
        if slide <= width / 4:
            slide += 40
        s.set_alpha(transparency)
        screen.blit(s, (0, 0))
        pygame.draw.rect(screen, (80, 80, 80), pygame.Rect(0, 0, slide, height))
        pygame.draw.rect(screen, (20, 20, 20), pygame.Rect(0, 0, slide, height), 15)
        for object in objects:
            object.process()

        pygame.display.flip()
        clock.tick(fps)


"""
Функция главного меню. Вначале прогружает катсцену (можно пропустить на esc), а затем само главное меню.
"""


def main_menu(objects):
    def game_begin():
        ev = pygame.event.Event(1001)
        pygame.event.post(ev)

    def exit():
        pygame.quit()
        sys.exit()

    def main_menu_music():
        pygame.mixer.music.load("data/music/Wake your fury and wait in hell.ogg")
        pygame.mixer.music.set_volume(0.3)
        pygame.mixer.music.play(-1)

    video = cv2.VideoCapture("data/intro.mp4")
    pygame.mixer.music.load("data/music/intro.ogg")
    fps = video.get(cv2.CAP_PROP_FPS)
    fpsClock = pygame.time.Clock()
    pygame.mixer.music.play()
    pygame.mixer.music.set_volume(1)
    pygame.time.Clock()
    Button(width / 2 - 200, height * 0.65, 400, 60, 'Begin', game_begin)
    Button(width / 2 - 200, height * 0.85, 400, 60, 'Exit', exit)
    main_menu_bg = cv2.VideoCapture("data/main_menu_background.mp4")
    MUSIC_END = pygame.USEREVENT + 1
    pygame.mixer.music.set_endevent(MUSIC_END)
    stop_intro = False
    running = True
    begin = False
    frame_counter = 0
    while running:
        screen.fill((0, 0, 0))
        if begin:
            break
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    video.release()
            if event.type == MUSIC_END:
                main_menu_music()
            if event.type == 1001:
                begin = True
        success, video_image = video.read()
        if success:
            video_surf = pygame.image.frombuffer(
                video_image.tobytes(), video_image.shape[1::-1], "BGR")
            screen.blit(video_surf, (0, 0))
        else:
            if not stop_intro:
                pygame.mixer.music.stop()
                stop_intro = True
            success, video_image = main_menu_bg.read()
            if success:
                frame_counter += 1
                video_surf = pygame.image.frombuffer(
                    video_image.tobytes(), video_image.shape[1::-1], "BGR")
                screen.blit(video_surf, (0, 0))
                if frame_counter == main_menu_bg.get(cv2.CAP_PROP_FRAME_COUNT):
                    frame_counter = 0
                    main_menu_bg.set(cv2.CAP_PROP_POS_FRAMES, 0)
                for object in objects:
                    object.process()
        pygame.display.flip()
        fpsClock.tick(fps)


"""
По отдельности загружает каждую гифку и присваивает изображения из них в отдельные списки.
"""


def sprite_append():
    vergil_sprites.append(load_image(r"standing animation.gif", 150, 300, (0, 0, 0)))
    vergil_sprites.append(load_image(r"running left.gif", 225, 300, (0, 0, 0)))
    vergil_sprites.append(load_image(r"running right.gif", 225, 300, (0, 0, 0)))

    ability_sprites.append(load_image(r"judgement cut (ability).gif", 200, 200, (0, 0, 0)))
    ability_sprites.append(load_image(r"tp left.gif", 350, 300, (0, 0, 0)))
    ability_sprites.append(load_image(r"tp right.gif", 350, 300, (0, 0, 0)))
    ability_sprites.append(load_image(r"judgement cut verg.gif", 350, 300, (0, 0, 0)))
    ability_sprites.append(load_image(r"doppleganger summon.gif", 150, 300, (0, 0, 0)))
    ability_sprites.append(load_image(r"judgement cut end.gif", 150, 300, (0, 0, 0)))

    doppleganger_sprites.append(load_image(r"doppleganger running right.gif", 250, 340, (0, 0, 0)))
    doppleganger_sprites.append(load_image(r"doppleganger running left.gif", 250, 340, (0, 0, 0)))
    doppleganger_sprites.append(load_image(r"doppleganger standing.gif", 260, 300, (0, 0, 0)))

    style.append(load_image(r"dismal.gif", 350, 284, (0, 0, 0)))
    style.append(load_image(r"crazy.gif", 350, 284, (0, 0, 0)))
    style.append(load_image(r"crazy_repeated.gif", 350, 284, (0, 0, 0)))
    style.append(load_image(r"badass.gif", 350, 284, (0, 0, 0)))
    style.append(load_image(r"badass_repeated.gif", 350, 284, (0, 0, 0)))
    style.append(load_image(r"apocalyptic.gif", 350, 284, (0, 0, 0)))
    style.append(load_image(r"apocalyptic_repeated.gif", 350, 284, (0, 0, 0)))
    style.append(load_image(r"savage.gif", 350, 284, (0, 0, 0)))
    style.append(load_image(r"savage_repeated.gif", 350, 284, (0, 0, 0)))
    style.append(load_image(r"sick_skills.gif", 350, 284, (0, 0, 0)))
    style.append(load_image(r"sick_skills_repeated.gif", 350, 284, (0, 0, 0)))
    style.append(load_image(r"smokin_sexy_style.gif", 350, 284, (0, 0, 0)))
    style.append(load_image(r"smokin_sexy_style_repeated.gif", 350, 284, (0, 0, 0)))


"""
Основной цикл и переменные. При завершении музыки вызывает ивент для запуска следующей (в соответствии с рангом).
При зажатии 1 или нажатии 2 вызывает выполнение способностей персонажа (1 - быстрые разрезы, 2 - двойник)
Для использования третьей способности на 3, нужно вначале добраться до ранга А. Только после этого её можно
будет использовать.
После третьей способности будет эффект "флешки".
При нажатии shift + A или D, Вергилий телепортируется на некоторое расстояние (зависит от набранного ускорения)
"""
if __name__ == "__main__":
    pygame.init()
    pygame.mixer.quit()
    pygame.mixer.init(44100, -16, 2, 512)
    width, height = pygame.display.Info().current_w, pygame.display.Info().current_h
    screen = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
    pygame.display.set_caption("Vergil Arcanoid Simulator")
    objects = []
    main_menu(objects)
    objects = []
    all_sprites = pygame.sprite.Group()
    boxes = pygame.sprite.Group()
    main_char = pygame.sprite.Group()
    vcg = pygame.sprite.Group()
    buttons = pygame.sprite.Group()
    acceleration = 0
    rank = -1
    rank_score = 0
    can_shrink = True
    screen.blit(load_image("vergil loading background.jpeg", width / 1.5, height * 2), (0, 0))
    pygame.display.flip()
    vergil_sprites = []
    ability_sprites = []
    doppleganger_sprites = []
    style = []
    sprite_append()
    vergil = Vergil(((width / 2) - 100, height - 300), vergil_sprites)
    rank_progress = RankBar((0.89 * width, 0.583 * height))
    fabox = AbilityBox((width * 0.75, height * 0.8), ability_sprites)
    vc = VergilClone((-300, vergil.rect.y), doppleganger_sprites)
    visualisator = RankVisualisation((width * 0.85, height * 0.32), style)
    horizontal_borders = pygame.sprite.Group()
    vertical_borders = pygame.sprite.Group()
    balls = pygame.sprite.Group()
    Border(0, height + 50, width, height + 50)
    Border(-100, 0, -100, height)
    Border(width + 100, 0, width + 100, height)
    fps = 50
    clock = pygame.time.Clock()
    running = True
    spawnwait = 0
    spawnlim = 40
    spawnbox_ready = False
    pygame.time.set_timer(995, 10000)
    last_rs = -1
    fabilitycd = True
    fabilitybox = False
    fabilityused = 0
    sabilitycd = True
    sabilityalive = False
    tpabilitycd = True
    tpstun = False
    thabilitycd = False
    thabilityavtivated = False
    background_color = (7, 0, 36)
    worlds = 1
    percentage_of_rank = 0
    times_played = -1
    s_progress = -1
    music_player(rank, times_played, last_rs, s_progress)
    intro_playing = True
    MUSIC_END = pygame.USEREVENT + 1
    pygame.mixer.music.set_endevent(MUSIC_END)
    flash = False
    i = 255
    sabilityready = False
    while running:
        pygame.mixer.music.set_volume(1)
        if spawnbox_ready:
            boxb = ButtonBox((random.randint(10, width - 0.2 * width), -20))
            spawnbox_ready = False
            boxb.spawn_check()
        if spawnwait >= spawnlim:
            boxa = BaseBox((random.randint(10, width - 0.2 * width), -20))
            spawnwait = 0
            boxa.spawn_check()
        max_y = []
        for box in boxes:
            max_y.append(box.rect.y)
            if box.touch() > 0:
                all_sprites.remove(box)
                boxes.remove(box)
                box.kill()
                if rank_score <= 270 and rank != 0:
                    rank_score += 2 * box.touch()
                elif rank_score > 270:
                    rank_score = 270
                if rank == 0:
                    rank_score += 4 * box.touch()
                if rank == -1:
                    rank = 0
                    music_player(rank, times_played, last_rs, s_progress)
        keys = pygame.key.get_pressed()
        if sabilitycd:
            if keys[pygame.K_2]:
                vergil.currentFrame = 0
                vergil.image = ability_sprites[4]
                vergil.acceleration = 0
                tpstun = True
                tpabilitycd = False
                pygame.time.set_timer(1011, 1550, 1)
                pygame.time.set_timer(10111, 1550, 1)
                doppleganger()
                sabilitycd = False
                pygame.time.set_timer(10091, 20000, 1)
                pygame.time.set_timer(1009, 40000, 1)
                pygame.time.set_timer(10092, 830, 1)
                sabilityready = True
        if tpabilitycd:
            if keys[pygame.K_LSHIFT]:
                if keys[pygame.K_a]:
                    if vergil.rect.x > width // 5 + vergil.acceleration * 20:
                        vergil.currentFrame = 0
                        vergil.image = ability_sprites[1]
                        vergil.rect.x -= width // 5 - vergil.acceleration * 15
                        pygame.mixer.Sound('data/sounds/tp_sound.ogg').play()
                        tpabilitycd = False
                        pygame.time.set_timer(1011, 650, 1)
                        pygame.time.set_timer(10111, 450, 1)
                        tpstun = True
                elif keys[pygame.K_d]:
                    if vergil.rect.x < width - width // 5 + vergil.acceleration * 15:
                        vergil.currentFrame = 0
                        vergil.image = ability_sprites[2]
                        vergil.rect.x += width // 5 + vergil.acceleration * 20
                        pygame.mixer.Sound('data/sounds/tp_sound.ogg').play()
                        tpabilitycd = False
                        pygame.time.set_timer(1011, 650, 1)
                        pygame.time.set_timer(10111, 450, 1)
                        tpstun = True
                vergil.acceleration = 0
        if thabilitycd:
            if keys[pygame.K_3]:
                fps = 29
                can_shrink = False
                vergil.currentFrame = 0
                vergil.image = ability_sprites[5]
                judgement_cut_end()
                if rank <= 5:
                    if s_progress == -1:
                        s_progress = 0
                    pygame.mixer.music.load("data/music/bury_the_light_s1(alt).ogg")
                    pygame.mixer.music.play(1)
                pygame.time.set_timer(10101, 2950, 1)
                pygame.time.set_timer(1010, 60000, 1)
                thabilitycd = False
                tpstun = True
                tpabilitycd = False
                fabilitycd = False
                sabilitycd = False
                pygame.time.set_timer(1011, 2950, 1)
                pygame.time.set_timer(10111, 2950, 1)
                vergil.acceleration = 0
        for event in pygame.event.get():
            if event.type == MUSIC_END:
                intro_playing = False
                if rank == -1:
                    rank = 0
                    music_player(rank, times_played, last_rs, s_progress)
                    intro_playing = True
                elif rank == 0:
                    rank = 1
                    music_player(rank, times_played, last_rs, s_progress)
                if rank == 4:
                    times_played += 1
                    music_player(rank, times_played, last_rs, s_progress)
                    if times_played == 3:
                        times_played = 0
                        music_player(rank, times_played, last_rs, s_progress)
                if rank >= 6:
                    s_progress += 1
                    music_player(rank, times_played, last_rs, s_progress)
                    if s_progress == 7:
                        s_progress = 0
                        music_player(rank, times_played, last_rs, s_progress)
                else:
                    music_player(rank, times_played, last_rs, s_progress)
            if event.type == pygame.QUIT:
                running = False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    if not tpstun:
                        if pause(objects, rank, times_played, last_rs, s_progress, intro_playing) == 1:
                            objects = []
                            main_menu(objects)
                            objects = []
                            all_sprites = pygame.sprite.Group()
                            boxes = pygame.sprite.Group()
                            main_char = pygame.sprite.Group()
                            vcg = pygame.sprite.Group()
                            buttons = pygame.sprite.Group()
                            acceleration = 0
                            rank = -1
                            rank_score = 0
                            can_shrink = True
                            screen.blit(load_image("vergil loading background.jpeg", width / 1.5, height * 2), (0, 0))
                            pygame.display.flip()
                            vergil = Vergil(((width / 2) - 100, height - 300), vergil_sprites)
                            rank_progress = RankBar((0.89 * width, 0.583 * height))
                            fabox = AbilityBox((width * 0.75, height * 0.8), ability_sprites)
                            vc = VergilClone((-300, vergil.rect.y), doppleganger_sprites)
                            visualisator = RankVisualisation((width * 0.85, height * 0.32), style)
                            horizontal_borders = pygame.sprite.Group()
                            vertical_borders = pygame.sprite.Group()
                            balls = pygame.sprite.Group()
                            Border(0, height + 50, width, height + 50)
                            Border(-100, 0, -100, height)
                            Border(width + 100, 0, width + 100, height)
                            fps = 50
                            clock = pygame.time.Clock()
                            running = True
                            spawnwait = 0
                            spawnlim = 40
                            spawnbox_ready = False
                            pygame.time.set_timer(995, 10000)
                            last_rs = -1
                            fabilitycd = True
                            fabilitybox = False
                            fabilityused = 0
                            sabilitycd = True
                            sabilityalive = False
                            tpabilitycd = True
                            tpstun = False
                            thabilitycd = False
                            thabilityavtivated = False
                            background_color = (7, 0, 36)
                            worlds = 1
                            percentage_of_rank = 0
                            times_played = -1
                            s_progress = -1
                            music_player(rank, times_played, last_rs, s_progress)
                            intro_playing = True
                            flash = False
                            i = 255
                            sabilityready = False
                        else:
                            objects = []
            if event.type == 993:
                if rank_score > 1 and can_shrink:
                    rank_score -= 1
            if event.type == 995:
                random_dialogues()
                pass
            if event.type == 1008:
                fabilitycd = True
                fabilitybox = True
            if event.type == 1009:
                sabilitycd = True
            if event.type == 10081:
                for ball in balls:
                    ball.kill()
            if event.type == 10091:
                sabilityalive = False
                sabilityready = False
            if event.type == 10092:
                vc.rect.x = vergil.rect.x - 200
                vc.rect.y = vergil.rect.y - 30
                sabilityalive = True
            if event.type == 10111:
                tpstun = False
                vergil.acceleration = 0
            if event.type == 1011:
                tpabilitycd = True
            if event.type == 1010:
                thabilitycd = True
            if event.type == 10101:
                pygame.mixer.Sound("data/sounds/judgement_cut_end_2.ogg").play()
                fabox.kill()
                sabilityalive = False
                sabilityready = False
                third_ability(rank, times_played, last_rs, s_progress, intro_playing)
                fabox = AbilityBox((width * 0.75, height * 0.8), ability_sprites)
                pygame.mixer.Sound("data/sounds/judgement_cut_end_3.ogg").play()
                can_shrink = True
                for box in boxes:
                    box.kill()
                fabilitycd = True
                sabilitycd = True
                pygame.time.set_timer(1009, 10000)
                pygame.time.set_timer(1008, 10000)
                pygame.time.set_timer(1011, 100)
                flash = True
                fps = 50
                clock = pygame.time.Clock()
                rank_score += 40
            if event.type == 10118:
                if max_y:
                    for box in boxes:
                        if box.rect.y == max(max_y):
                            if fabilityused <= 3 and rank < 6:
                                if keys[pygame.K_1] and fabilityused >= 1:
                                    vergil.currentFrame = 20
                                    vergil.image = ability_sprites[3]
                                if rank < 6:
                                    pygame.time.set_timer(1011, 1400, 1)
                                    pygame.time.set_timer(10111, 1400, 1)
                                else:
                                    pygame.time.set_timer(1011, 900, 1)
                                    pygame.time.set_timer(10111, 900, 1)
                                vergil.acceleration = 0
                                judgement_cut()
                            if fabilityused <= 4 and rank < 6:
                                fabilityused += 1
                                Ball((box.rect.x, box.rect.y), ability_sprites)
                                box.touched = box.index
                                if keys[pygame.K_1]:
                                    pygame.time.set_timer(10118, 500, 1)
                            if fabilityused <= 6 <= rank:
                                if keys[pygame.K_1] and fabilityused >= 1:
                                    vergil.currentFrame = 20
                                    vergil.image = ability_sprites[3]
                                    pygame.time.set_timer(1011, 1400, 1)
                                    pygame.time.set_timer(10111, 1400, 1)
                                else:
                                    pygame.time.set_timer(1011, 800, 1)
                                    pygame.time.set_timer(10111, 800, 1)
                                vergil.acceleration = 0
                                judgement_cut()
                            if fabilityused <= 7 and rank >= 6:
                                fabilityused += 1
                                Ball((box.rect.x, box.rect.y), ability_sprites)
                                box.touched = box.index
                                if keys[pygame.K_1]:
                                    pygame.time.set_timer(10118, 400, 1)
                            pygame.time.set_timer(1008, 25000, 1)

        if fabilitybox:
            fabox = AbilityBox((width * 0.75, height * 0.8), ability_sprites)
            fabilitybox = False
        if fabilitycd:
            if max_y:
                for box in boxes:
                    if box.rect.y == max(max_y):
                        if keys[pygame.K_1]:
                            vergil.currentFrame = 0
                            vergil.image = ability_sprites[3]
                            vergil.acceleration = 0
                            fabilityused = 1
                            fabox.kill()
                            fabilitycd = False
                            tpstun = True
                            tpabilitycd = False
                            if rank < 6:
                                pygame.time.set_timer(10118, 800, 1)
                                pygame.time.set_timer(1011, 1200, 1)
                                pygame.time.set_timer(10111, 1200, 1)
                            elif rank >= 6:
                                pygame.time.set_timer(10118, 700, 1)
                                pygame.time.set_timer(1011, 1100, 1)
                                pygame.time.set_timer(10111, 1100, 1)

        if rank_score >= 250:
            rank = 8
            if rank_score <= 270:
                percentage_of_rank = (rank_score - 250) / 20
            else:
                percentage_of_rank = 1
            if last_rs != rank:
                rank_score = 260
                rank_announcer(rank, style)
                last_rs = 8
                spawnlim = 16
                worlds = 3.4
                pygame.time.set_timer(993, 230)
        elif rank_score >= 210:
            rank = 7
            percentage_of_rank = (rank_score - 210) / 40
            if last_rs != rank:
                rank_score = 220
                if last_rs > rank:
                    rank_score = 245
                rank_announcer(rank, style)
                last_rs = 7
                spawnlim = 18
                worlds = 3.2
                pygame.time.set_timer(993, 280)
        elif rank_score >= 170:
            rank = 6
            percentage_of_rank = (rank_score - 170) / 40
            if last_rs != rank:
                rank_score = 180
                if last_rs > rank:
                    rank_score = 205
                spawnlim = 20
                worlds = 3
                rank_announcer(rank, style)
                if thabilitycd and last_rs < 6:
                    if s_progress == -1:
                        s_progress = 0
                    music_player(rank, times_played, last_rs, s_progress)
                last_rs = 6
                pygame.time.set_timer(993, 300)
        elif rank_score >= 130:
            rank = 5
            spawnlim = 20
            worlds = 2
            percentage_of_rank = (rank_score - 130) / 40
            if last_rs != rank:
                rank_score = 140
                if last_rs > rank:
                    rank_score = 165
                if not thabilityavtivated:
                    thabilitycd = True
                    thabilityavtivated = True
                rank_announcer(5, style)
                last_rs = 5
                pygame.time.set_timer(993, 380)
        elif rank_score >= 90:
            percentage_of_rank = (rank_score - 90) / 40
            rank = 4
            worlds = 1.6
            spawnlim = 20
            if last_rs != rank:
                rank_score = 100
                if last_rs > rank:
                    rank_score = 125
                pygame.time.set_timer(993, 500)
                rank_announcer(4, style)
                last_rs = 4
                background_color = (45, 0, 15)
        elif rank_score >= 50:
            percentage_of_rank = (rank_score - 50) / 40
            rank = 3
            worlds = 1.8
            spawnlim = 25
            if last_rs != rank:
                rank_score = 60
                if last_rs > rank:
                    rank_score = 85
                pygame.time.set_timer(993, 480)
                rank_announcer(3, style)
                last_rs = 3
                background_color = (60, 0, 30)
        elif rank_score >= 20:
            rank = 2
            worlds = 1.3
            spawnlim = 28
            percentage_of_rank = (rank_score - 20) / 30
            if last_rs != rank:
                rank_score = 30
                if last_rs > rank:
                    rank_score = 45
                if last_rs == 1 and not intro_playing:
                    music_player(rank, times_played, last_rs, s_progress)
                rank_announcer(2, style)
                last_rs = 2
                pygame.time.set_timer(993, 550)
                background_color = (20, 0, 86)
        elif rank_score >= 1 and not rank == 0:
            rank = 1
            percentage_of_rank = 0
            if last_rs != rank:
                pygame.time.set_timer(993, 700)
                worlds = 1
                spawnlim = 30
                last_rs = 1
                background_color = (10, 0, 56)
        else:
            pygame.time.set_timer(993, 750)
            worlds = 2
            spawnlim = 20
            percentage_of_rank = 0
            background_color = (7, 0, 36)
        spawnwait += 1
        screen.fill(background_color)
        if rank >= 6:
            background = load_image("backgroundS.png", height, width)
            screen.blit(background, (0, 0))
        vergil.rank = rank
        vc.rank = rank
        rank_progress.rank = rank
        rank_progress.percentage_of_rank = percentage_of_rank
        balls.update()
        all_sprites.update()
        boxes.draw(screen)
        boxes.update()
        buttons.update()
        main_char.update()
        vcg.update()
        if rank_score >= 20:
            visualisator.update()
            if visualisator.currentFrame == len(visualisator.image) - 1:
                visualisator.currentFrame = 0
                visualisator.rank = rank
        rank_progress.update()
        if flash:
            tarect = pygame.Surface((width, height))
            i -= 2
            tarect.fill((255, 255, 255))
            tarect.set_alpha(i)
            screen.blit(tarect, (0, 0))
            if i <= 0:
                flash = False
                i = 255
        pygame.display.flip()
        clock.tick(fps)

    pygame.quit()
