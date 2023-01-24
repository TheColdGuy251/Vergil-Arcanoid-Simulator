import sys
import pygame


class Button():
    def __init__(self, x, y, width, height, buttonText='Button', onclickFunction=None, onePress=False):
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.onclickFunction = onclickFunction
        self.onePress = onePress

        self.fillColors = {
            'normal': '#000000',
            'hover': '#009999',
            'pressed': '#333333',
        }

        self.buttonSurface = pygame.Surface((self.width, self.height))
        self.buttonRect = pygame.Rect(self.x, self.y, self.width, self.height)

        self.buttonSurf = font.render(buttonText, True, (255, 255, 255))

        self.alreadyPressed = False

        objects.append(self)

    def process(self):
        mousePos = pygame.mouse.get_pos()
        self.buttonSurface = self.buttonSurface.convert_alpha()
        if not self.buttonRect.collidepoint(mousePos):
            self.buttonSurface.fill((0, 0, 0, 0))
        if self.buttonRect.collidepoint(mousePos):
            self.buttonSurface.fill((0, 0, 255, 0))
            shape_surf = pygame.Surface(pygame.Rect(0, self.y, 1000, self.height).size, pygame.SRCALPHA)
            pygame.draw.rect(shape_surf, (0, 0, 255, 120), shape_surf.get_rect())
            screen.blit(shape_surf, (0, self.y, 1000, self.height))
            if pygame.mouse.get_pressed(num_buttons=3)[0]:
                self.buttonSurface.fill(self.fillColors['pressed'])

                if self.onePress:
                    self.onclickFunction()

                elif not self.alreadyPressed:
                    self.onclickFunction()
                    self.alreadyPressed = True

            else:
                self.alreadyPressed = False

        self.buttonSurface.blit(self.buttonSurf, [
            self.buttonRect.width / 2 - self.buttonSurf.get_rect().width / 2,
            self.buttonRect.height / 2 - self.buttonSurf.get_rect().height / 2
        ])
        screen.blit(self.buttonSurface, self.buttonRect)


def myFunction():
    print('Button Pressed')


pygame.init()
fps = 60
fpsClock = pygame.time.Clock()
width, height = 640, 480
screen = pygame.display.set_mode((width, height))

font = pygame.font.SysFont('Arial', 40)

objects = []
transparent = 0
customButton = Button(40, 30, 400, 50, 'Начать игру', myFunction)
customButton = Button(30, 140, 400, 50, 'Обучение', myFunction)
customButton = Button(30, 200, 400, 50, 'Выйти', myFunction)
running = True
while running:
    screen.fill((20, 20, 20))
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()

    for object in objects:
        object.process()

    pygame.display.flip()
    fpsClock.tick(fps)