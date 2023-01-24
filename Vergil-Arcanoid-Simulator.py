import sys
import pygame
import cv2


pygame.mixer.pre_init(44100, -16, 1, 512)


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
video = cv2.VideoCapture("data\intro.mp4")
pygame.mixer.music.load("data\music\intro.ogg")
success, video_image = video.read()
fps = video.get(cv2.CAP_PROP_FPS)
fpsClock = pygame.time.Clock()
window = pygame.display.set_mode(video_image.shape[1::-1])
pygame.mixer.music.play()
clock = pygame.time.Clock()
width, height = pygame.display.Info().current_w, pygame.display.Info().current_h
screen = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)

objects = []
customButton = Button(width / 2 - 200, height * 0.65, 400, 60, 'Begin', myFunction)
customButton = Button(width / 2 - 200, height * 0.78, 400, 60, 'Tutorial', myFunction)
customButton = Button(width / 2 - 200, height * 0.85, 400, 60, 'Exit', myFunction)
bg = pygame.image.load("data/vergil background.png")
MUSIC_END = pygame.USEREVENT + 1
pygame.mixer.music.set_endevent(MUSIC_END)
stop_intro = False
running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()
        if event.type == pygame.KEYDOWN:
            video.release()
            success = False
        if event.type == MUSIC_END:
            main_menu_music()
    success, video_image = video.read()
    if success:
        video_surf = pygame.image.frombuffer(
            video_image.tobytes(), video_image.shape[1::-1], "BGR")
        window.blit(video_surf, (0, 0))
    else:
        if not stop_intro:
            pygame.mixer.music.stop()
            stop_intro = True
        pygame.display.flip()
        screen.blit(bg, (0, 0))
        for object in objects:
            object.process()

    pygame.display.flip()
    fpsClock.tick(fps)
pygame.quit()