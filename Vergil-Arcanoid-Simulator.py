import os
import pygame
import sys
import random


def load_image(name, width, height, colorkey=None):
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
    image = pygame.transform.scale(image, (height, width))
    return image


class Border(pygame.sprite.Sprite):
    def __init__(self, x1, y1, x2, y2):
        super().__init__(all_sprites)
        if x1 == x2:
            self.add(vertical_borders)
            self.image = pygame.Surface([1, y2 - y1])
            self.rect = pygame.Rect(x1, y1, 1, y2 - y1)
        else:
            self.add(horizontal_borders)
            self.image = pygame.Surface([x2 - x1, 1])
            self.rect = pygame.Rect(x1, y1, x2 - x1, 1)


class BaseBox(pygame.sprite.Sprite):
    def __init__(self, pos):
        super().__init__(all_sprites)
        self.add(boxes)
        self.pos = pos
        self.image = load_image("gek.png", 100, 300)
        self.effect = random.randint(1, 5)
        self.touched = 0
        self.angle = 0
        self.speed = 1
        self.sidemovem = 0
        if self.effect == 1:
            self.imagec = self.image.copy()
            self.image.set_alpha(0)
        elif self.effect == 2:
            self.speed = 3
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
            self.rect = self.rect.move(self.sidemovem, self.speed * 2)
        else:
            self.touched = 1
        if pygame.sprite.spritecollideany(self, vertical_borders):
            self.sidemovem = -self.sidemovem
        if pygame.sprite.spritecollideany(self, horizontal_borders):
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



class ButtonBox(pygame.sprite.Sprite):
    def __init__(self, pos):
        super().__init__(all_sprites)
        self.add(boxes)
        self.pos = pos
        self.image = load_image("gek.png", 100, 300)
        self.speed = 1
        self.rect = self.image.get_rect()
        self.mask = pygame.mask.from_surface(self.image)
        self.imagebb = pygame.Surface((160, 60))
        self.imagebb.fill((0, 0, 0))
        self.rectbb = self.imagebb.get_rect()
        self.rectbb.x = self.pos[0] + 75
        self.rectbb.y = self.pos[1] + 25
        self.maskbb = pygame.mask.from_surface(self.image)
        self.imageb = pygame.Surface((150, 50))
        self.imageb.fill((170, 170, 170))
        self.rectb = self.imageb.get_rect()
        self.maskb = pygame.mask.from_surface(self.image)
        self.rect.x = self.pos[0]
        self.rect.y = self.pos[1]
        self.rectb.x = self.pos[0] + 75
        self.rectb.y = self.pos[1] + 25
        self.readytotouch = False
        self.touched = 0

    def update(self):
        if pygame.sprite.spritecollideany(self, horizontal_borders):
            self.kill()
        mousePos = pygame.mouse.get_pos()
        screen.blit(self.imagebb, self.rectbb)
        screen.blit(self.imageb, self.rectb)
        if self.rectb.collidepoint(mousePos):
            if pygame.mouse.get_pressed(num_buttons=3)[0]:
                self.readytotouch = True
        if self.readytotouch and pygame.sprite.collide_mask(self, vergil):
            self.touched = 2
        else:
            self.rect = self.rect.move(0, self.speed * 2)
            self.rectb = self.rectb.move(0, self.speed * 2)
            self.rectbb = self.rectb.move(0, self.speed * 2)

    def touch(self):
        return self.touched

    def spawn_check(self):
        for elem in boxes:
            if elem is self:
                continue
            elif pygame.sprite.collide_mask(self, elem):
                self.kill()
                global spawnwaitb
                spawnwaitb = 200


class Vergil(pygame.sprite.Sprite):
    def __init__(self, pos):
        super().__init__(main_char)
        self.image = load_image("stand.png", 300, 200, (0, 0, 0))
        self.rect = self.image.get_rect()
        self.mask = pygame.mask.from_surface(self.image)
        self.rect.x = pos[0]
        self.rect.y = pos[1]
        self.key = 0

    def update(self):
        keys = pygame.key.get_pressed()
        if keys[pygame.K_a]:
            self.image = load_image("left.png", 300, 200, (0, 0, 0))
            self.rect.x -= 10
        elif keys[pygame.K_d]:
            self.image = load_image("right.png", 300, 200, (0, 0, 0))
            self.rect.x += 10
        else:
            self.image = load_image("stand.png", 300, 200, (0, 0, 0))
        if pygame.sprite.spritecollideany(self, vertical_borders):
            if self.rect.x < width // 2:
                self.rect.x = width - 300
            else:
                self.rect.x = 100


if __name__ == "__main__":
    pygame.init()
    width, height = pygame.display.Info().current_w, pygame.display.Info().current_h
    screen = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
    pygame.display.set_caption("Vergil Arcanoid Simulator")
    all_sprites = pygame.sprite.Group()
    boxes = pygame.sprite.Group()
    main_char = pygame.sprite.Group()
    vergil = Vergil(((width / 2) - 100, height - 300))
    horizontal_borders = pygame.sprite.Group()
    vertical_borders = pygame.sprite.Group()
    Border(0, height + 200, width, height + 200)
    Border(-100, 0, -100, height)
    Border(width + 50, 0, width + 50, height)
    fps = 50
    clock = pygame.time.Clock()
    running = True
    spawnwait = 0
    spawnlim = 40
    spawnbox_ready = False
    rank_score = 0
    pygame.time.set_timer(993, 2000)
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if event.type == 993:
                rank_score -= 1
        if spawnbox_ready:
            boxb = ButtonBox((random.randint(10, width - 0.2 * width), -20))
            spawnbox_ready = False
            boxb.spawn_check()
        if spawnwait >= spawnlim:
            boxa = BaseBox((random.randint(10, width - 0.2 * width), -20))
            spawnwait = 0
            boxa.spawn_check()
        for box in boxes:
            if box.touch() > 0:
                all_sprites.remove(box)
                boxes.remove(box)
                box.kill()
                rank_score += box.touch()
                print(rank_score)
        spawnwait += 1
        screen.fill((7, 0, 36))
        all_sprites.draw(screen)
        all_sprites.update()
        main_char.draw(screen)
        main_char.update()
        pygame.display.flip()
        clock.tick(fps)
    pygame.quit()
