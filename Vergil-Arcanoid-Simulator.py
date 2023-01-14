import pygame


class BaseBox:
    pass


class Buttonbox(BaseBox):
    pass


if __name__ == '__main__':
    pygame.init()
    pygame.display.set_caption('Vergil Arcanoid Simulator')
    screen = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
    running = True
    drawing = False
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
        pygame.display.flip()
    pygame.quit()