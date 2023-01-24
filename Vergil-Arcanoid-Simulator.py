import sys
import pygame

pygame.mixer.init()


class Button():
    def __init__(self, x, y, width, height, buttonText='Button', onclickFunction=None, onePress=False):
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.onclickFunction = onclickFunction
        self.onePress = onePress
        self.buttonText = buttonText
        self.flicked = False

        self.buttonSurface = pygame.Surface((self.width, self.height))
        self.buttonRect = pygame.Rect(self.x, self.y, self.width, self.height)

        self.alreadyPressed = False

        objects.append(self)

    def process(self):
        mousePos = pygame.mouse.get_pos()
        self.buttonSurface = self.buttonSurface.convert_alpha()
        if not self.buttonRect.collidepoint(mousePos):
            self.buttonSurface.fill((0, 0, 0, 0))
            font = pygame.font.Font('data/font/DMC5Font.otf', 40)
            self.buttonSurf = font.render(self.buttonText, True, (255, 255, 255))
            self.flicked = False
        if self.buttonRect.collidepoint(mousePos):
            self.buttonSurface.fill((0, 39, 62, 0))
            shape_surf = pygame.Surface(pygame.Rect(0, self.y, pygame.display.Info().current_w, self.height).size,
                                        pygame.SRCALPHA)
            pygame.draw.rect(shape_surf, (0, 39, 62, 230), shape_surf.get_rect())
            screen.blit(shape_surf, (0, self.y, pygame.display.Info().current_w, self.height))
            font = pygame.font.Font('data/font/DMC5Font.otf', 55)
            if not self.flicked:
                pygame.mixer.Sound('data/sounds/flicking sound.ogg').play()
                self.flicked = True
            self.buttonSurf = font.render(self.buttonText, True, (124, 255, 255))
            if pygame.mouse.get_pressed(num_buttons=3)[0]:
                pygame.mixer.Sound('data/sounds/enter sound.ogg').play()

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

def main_menu_music():
    pygame.mixer.music.load("data/music/Wake your fury and wait in hell.ogg")
    pygame.mixer.music.set_volume(0.3)
    pygame.mixer.music.play(-1)


pygame.init()
fps = 60
fpsClock = pygame.time.Clock()
width, height = pygame.display.Info().current_w, pygame.display.Info().current_h
screen = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)

objects = []
customButton = Button(width / 2 - 200, height * 0.65, 400, 60, 'Begin', myFunction)
customButton = Button(width / 2 - 200, height * 0.78, 400, 60, 'Tutorial', myFunction)
customButton = Button(width / 2 - 200, height * 0.85, 400, 60, 'Exit', myFunction)
bg = pygame.image.load("data/vergil background.png")
main_menu_music()
running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()
    screen.blit(bg, (0, 0))
    for object in objects:
        object.process()

    pygame.display.flip()
    fpsClock.tick(fps)