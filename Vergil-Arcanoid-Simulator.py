import os
import pygame
import sys
import random
import moviepy.editor


def load_image(name, colorkey=None):
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


class BaseBox(pygame.sprite.Sprite):
    def __init__(self, pos):
        pass


class ButtonBox(BaseBox):
    pass


class Vergil(pygame.sprite.Sprite):
    def __init__(self, pos):
        super().__init__(all_sprites)
        self.image = load_image("IAMTHESTORM.png")
        self.rect = self.image.get_rect()
        self.mask = pygame.mask.from_surface(self.image)
        self.rect.x = pos[0]
        self.rect.y = pos[1]
        self.key = 0

    def update(self):
        keys = pygame.key.get_pressed()
        if keys[pygame.K_a]:
            self.rect.x -= 10
        elif keys[pygame.K_d]:
            self.rect.x += 10


if __name__ == "__main__":
    pygame.init()
    width, height = 800, 600
    screen = pygame.display.set_mode((width, height))
    pygame.display.set_caption("Vergil Arcanoid Simulator")
    all_sprites = pygame.sprite.Group()
    vergil = Vergil(((width / 2 ) - 100, height - 200))
    horizontal_borders = pygame.sprite.Group()
    vertical_borders = pygame.sprite.Group()
    fps = 50
    clock = pygame.time.Clock()
    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
        BaseBox((random.randint(10, width - 0.2 * width), -20))
        screen.fill((7, 0, 36))
        all_sprites.draw(screen)
        all_sprites.update()
        pygame.display.flip()
        clock.tick(fps)
    pygame.quit()