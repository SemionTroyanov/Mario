import pygame


def get_max_len(file):
    max_len = 0
    with open(file) as f:
        mario_map = f.read().split("\n")
    for row in mario_map:
        max_len = max(max_len, len(row))
    return max_len


def image_load(file):
    image = pygame.image.load(file)
    image = image.convert_alpha()
    image.set_colorkey(-1)
    return image
