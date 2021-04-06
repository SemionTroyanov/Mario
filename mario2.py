import pygame
from functions import *


HEIGHT = 300
WIDTH = 480
TILE_SIZE = 20
MAP = "map.txt"
with open(MAP) as f:
    MAP_ROWS = f.read().split("\n")
SCREEN_WIDTH = get_max_len(MAP) * TILE_SIZE


class Camera:
    def __init__(self):
        self.pos_x = 0

    def update(self, hero):
        if WIDTH // 2 <= hero.rect.x <= SCREEN_WIDTH - WIDTH // 2:
            self.pos_x = WIDTH // 2 - hero.rect.x


class Mario(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.image = image_load("sprites/mario1.1..png")
        self.rect = self.image.get_rect()
        self.rect.midbottom = (100, HEIGHT - 50)
        self.dx = 2
        self.image_run = [
            image_load("sprites/mario1.2.1.png"),
            image_load("sprites/mario1.3..png")
        ]
        self.num_run = 0
        self.is_moving = False
        self.is_falling = True
        self.is_jumping = False
        self.jump_height = 31
        self.jump_current = 0
        self.can_jump = True

    def collide(self, cords=None):
        if cords is None:
            cords = (self.rect.top, self.rect.right, self.rect.bottom, self.rect.left)
        bottom = HEIGHT // TILE_SIZE - (cords[2] - 8) // TILE_SIZE - 1
        left = cords[3] // TILE_SIZE
        right = cords[1] // TILE_SIZE
        top = HEIGHT // TILE_SIZE - (cords[0] - 8) // TILE_SIZE - 1
        mid_x = (cords[1] + cords[3]) // 2 // TILE_SIZE
        mid_y = HEIGHT // TILE_SIZE - ((cords[0] + cords[2]) // 2 - 8) // TILE_SIZE - 1

        collide_bottom_left = ""
        collide_bottom_right = ""
        collide_top_left = ""
        collide_top_right = ""
        collide_mid_top = ""
        collide_mid_right = ""
        collide_mid_bottom = ""
        collide_mid_left = ""

        if len(MAP_ROWS[-(bottom + 1)]) > left:
            collide_bottom_left = MAP_ROWS[-(bottom + 1)][left].replace(" ", "")
        if len(MAP_ROWS[-(bottom + 1)]) > right:
            collide_bottom_right = MAP_ROWS[-(bottom + 1)][right].replace(" ", "")
        if len(MAP_ROWS[-(top + 1)]) > left:
            collide_top_left = MAP_ROWS[-(top + 1)][left].replace(" ", "")
        if len(MAP_ROWS[-(top + 1)]) > right:
            collide_top_right = MAP_ROWS[-(top + 1)][right].replace(" ", "")
        if len(MAP_ROWS[-(top + 1)]) > mid_x:
            collide_mid_top = MAP_ROWS[-(top + 1)][mid_x].replace(" ", "")
        if len(MAP_ROWS[-(mid_y + 1)]) > right:
            collide_mid_right = MAP_ROWS[-(mid_y + 1)][right].replace(" ", "")
        if len(MAP_ROWS[-(bottom + 1)]) > mid_x:
            collide_mid_bottom = MAP_ROWS[-(bottom + 1)][mid_x].replace(" ", "")
        if len(MAP_ROWS[-(mid_y + 1)]) > left:
            collide_mid_left = MAP_ROWS[-(mid_y + 1)][left].replace(" ", "")
        return collide_top_right, collide_bottom_right, collide_bottom_left, collide_top_left, \
               collide_mid_top, collide_mid_right, collide_mid_bottom, collide_mid_left

    def move(self):

        self.gravity()

        pressed = pygame.key.get_pressed()
        if pressed[pygame.K_RIGHT] and self.rect.x + 2 + self.dx <= SCREEN_WIDTH - self.rect.width:
            collides = self.collide((self.rect.top, self.rect.right + 2, self.rect.bottom, self.rect.left))
            if not collides[0] and not collides[1] and not collides[5]:
                self.rect.x += self.dx
                self.is_moving = True
            else:
                self.is_moving = False
        elif pressed[pygame.K_LEFT] and 0 <= self.rect.x - self.dx:
            collides = self.collide((self.rect.top, self.rect.right, self.rect.bottom, self.rect.left - 2))
            if not collides[2] and not collides[3] and not collides[7]:
                self.rect.x -= self.dx
                self.is_moving = True
            else:
                self.is_moving = False
        else:
            self.is_moving = False
        if pressed[pygame.K_UP] and self.can_jump:
            self.is_jumping = True
            self.can_jump = False
            self.is_falling = False
        self.jump()

        if self.is_moving:
            self.image = self.image_run[self.num_run]
            self.num_run = (self.num_run + 1) % 2

    def jump(self):
        if self.is_jumping and self.jump_current < self.jump_height:
            self.can_jump = False
            self.rect.y -= 2
            self.jump_current += 1
        elif self.jump_current == self.jump_height:
            self.is_jumping = False
            self.is_falling = True
            self.jump_current = 0
        collides = self.collide((self.rect.top - 2, self.rect.right, self.rect.bottom, self.rect.left))
        if collides[0] or collides[3]:
            self.jump_current = self.jump_height

    def gravity(self):
        if self.is_falling:
            collides = self.collide((self.rect.top, self.rect.right, self.rect.bottom + 2, self.rect.left))
            if not collides[1] and not collides[2]:
                self.rect.y += 2
            else:
                self.can_jump = True
        
        
class Background(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.image = pygame.image.load("sprites/BACKGROUND1.jpg")
        self.rect = self.image.get_rect()
        self.rect.topleft = (0, 0)


class BaseBlock(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.image = image_load("sprites/block2.1.png")
        self.rect = self.image.get_rect()


class BrickBlock(BaseBlock):
    def __init__(self):
        super().__init__()
        self.image = image_load("sprites/block1.1.png")


class QuestBlock(BaseBlock):
    def __init__(self):
        super().__init__()
        self.image = image_load("sprites/block3.1.png")
        self.image_coin = image_load("sprites/coin3.1.png")
        self.is_jumping = False
        self.time = 10
        self.countdown = self.time
        self.xp = 3

    def become_coin(self):
        if self.xp == 0:
            self.image = self.image_coin


if __name__ == "__main__":
    pygame.init()
    screen = pygame.Surface((SCREEN_WIDTH, HEIGHT))
    camera = Camera()
    display = pygame.display.set_mode((WIDTH, HEIGHT))

    freq = 10
    pygame.time.set_timer(pygame.USEREVENT, freq)

    mario = Mario()
    mario_group = pygame.sprite.GroupSingle(mario)

    background = Background()
    background_group = pygame.sprite.Group()
    background_group.add(background)

    block_group = pygame.sprite.Group()
    pos_x = 0
    for i, row in enumerate(MAP_ROWS[::-1]):
        for j, element in enumerate(row):
            block = None
            if element == ".":
                block = BaseBlock()
            elif element == ",":
                block = BrickBlock()
            elif element == "^":
                block = QuestBlock()
            if element != " " and block is not None:
                block_group.add(block)
                block.rect.x = j * TILE_SIZE
                block.rect.y = HEIGHT - (i + 1) * TILE_SIZE + 8

    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.USEREVENT:
                mario.move()
                camera.update(mario)

        if -camera.pos_x // WIDTH == len(background_group) - 1:
            background = Background()
            background.rect.x = len(background_group) * WIDTH
            background_group.add(background)

        background_group.draw(screen)
        block_group.draw(screen)
        mario_group.draw(screen)
        display.blit(screen, (camera.pos_x, 0))
        pygame.display.flip()
    pygame.quit()
