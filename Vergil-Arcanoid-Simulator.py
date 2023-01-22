import os
import pygame
import sys
import random


pygame.mixer.pre_init(44100, -16, 1, 512)


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
    pass


class ButtonBox(BaseBox):
    pass


class Vergil(pygame.sprite.Sprite):
    pass


def main_menu_music_player():
    pygame.mixer.Music.play("data/music/main_menu.ogg")


def music_player(style_rank):
    if style_rank == 0:
        pygame.mixer.music.load("data/music/bury_the_light_intro.ogg")
        pygame.mixer.music.play()
    elif style_rank == 1:
        pygame.mixer.music.load("data/music/bury_the_light_no_rank.ogg")
        pygame.mixer.music.play()
    elif style_rank == 2:
        pygame.mixer.music.load('data/music/bury_the_light_dismal.ogg')
        pygame.mixer.music.play()
    elif style_rank == 3:
        pygame.mixer.music.load("data/music/bury_the_light_crazy.ogg")
        pygame.mixer.music.play()
    elif style_rank == 4:
        pygame.mixer.music.load("data/music/bury_the_light_badass.ogg")
        pygame.mixer.music.play()
    elif style_rank == 5:
        pygame.mixer.music.load("data/music/bury_the_light_apocalyptic.ogg")
        pygame.mixer.music.play()
    elif style_rank == 6:
        pygame.mixer.music.load("data/music/bury_the_light_s.ogg")
        pygame.mixer.music.play()



def judgement_cut(times):
    pygame.mixer.Sound.play("data/sound/judgement_cut.ogg")
    if times == 3:
        pygame.mixer.Sound.play("data/dialogues/jackpot.ogg")


def doppleganger():
    pygame.mixer.Sound.play("data/sound/doppleganger_spawn.ogg")


def judgement_cut_end(style_rank):
    if style_rank == 5:
        pass
    else:
        pygame.mixer.Sound.play("data/sound/judgement_cut_end_main.ogg")
        if random.randint(0, 1) == 0:
            pygame.mixer.Sound.play("data/dialogues/slay_all.ogg")
        else:
            pygame.mixer.Sound.play("data/dialogues/you_shall_die.ogg")


def sin_devil_trigger():
    pygame.mixer.Sound.play("data/sound/sdt_transformation.ogg")
    if random.randint(0, 1) == 0:
        pygame.mixer.Sound.play("data/dialogues/nightmare_begins.ogg")
    else:
        pygame.mixer.Sound.play("data/dialogues/this_is_power.ogg")


def damage_taken(interval):
    a = random.randint(0, 2)
    if a == 0:
        pygame.mixer.Music.play("data/sound/hurt1.ogg")
    elif a == 1:
        pygame.mixer.Music.play("data/sound/hurt2.ogg")
    else:
        pygame.mixer.Music.play("data/sound/hurt3.ogg")

    if interval >= 5000:
        a = random.randint(0, 2)
        if a == 0:
            pygame.mixer.Music.play("data/dialogue/hurt1.ogg")
        elif a == 1:
            pygame.mixer.Music.play("data/dialogue/hurt2.ogg")
        else:
            pygame.mixer.Music.play("data/dialogue/hurt3.ogg")


def random_dialogues(interval):
    if interval >= 10000:
        a = random.randint(0, 5)
        if a == 0:
            pygame.mixer.Music.play("data/dialogue/show_me_your_motivation.ogg")
        elif a == 1:
            pygame.mixer.Music.play("data/dialogue/you_not_worthy_as_my_opponent.ogg")
        elif a == 2:
            pygame.mixer.Music.play("data/dialogue/scum.ogg")
        elif a == 3:
            pygame.mixer.Music.play("data/dialogue/how_boring.ogg")
        elif a == 4:
            pygame.mixer.Music.play("data/dialogue/your_wasting_my_time.ogg")
        elif a == 5:
            pygame.mixer.Music.play("data/dialogue/now_im_a_little_motivated.ogg")


if __name__ == "__main__":
    pygame.init()
    width, height = pygame.display.Info().current_w, pygame.display.Info().current_h
    screen = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
    pygame.display.set_caption("Vergil Arcanoid Simulator")
    all_sprites = pygame.sprite.Group()
    horizontal_borders = pygame.sprite.Group()
    vertical_borders = pygame.sprite.Group()
    fps = 50
    clock = pygame.time.Clock()
    running = True
    rank = -1
    MUSIC_END = pygame.USEREVENT + 1
    pygame.mixer.music.set_endevent(MUSIC_END)
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if event.type == pygame.MOUSEBUTTONDOWN:
                rank += 1
                if rank == 0:
                    music_player(rank)
            if event.type == MUSIC_END:
                if rank == 0:
                    rank = 1
                    music_player(rank)
                else:
                    music_player(rank)
        screen.fill((7, 0, 36))
        all_sprites.draw(screen)
        all_sprites.update()
        pygame.display.flip()
        clock.tick(fps)
    pygame.quit()