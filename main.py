import pygame as pg
from pygame.locals import *
import os

SCREENRECT = pg.Rect(0, 0, 640, 480)
BACKGROUND_COLOR = (0, 0, 0)
FPS = 60
main_dir = os.path.split(os.path.abspath(__file__))[0]


def load_image(file, scene=False):
    """ loads an image, prepares it for play
    """
    path = "assets/sprites"
    if scene:
        path = "assets/scenes"
    file = os.path.join(main_dir, path, file)
    try:
        surface = pg.image.load(file)
    except pg.error:
        raise SystemExit('Could not load image "%s" %s' % (file, pg.get_error()))
    return surface.convert()


class Player(pg.sprite.Sprite):
    """
        Sprite character that walks around a house
    """

    speed = 3
    left_names = ["man4_lf1.gif", "man4_lf2.gif"]
    left_images = []
    right_names = ["man4_rt1.gif", "man4_rt2.gif"]
    right_images = []
    up_names = ["man4_bk1.gif", "man4_bk2.gif"]
    up_images = []
    down_names = ["man4_fr1.gif", "man4_fr2.gif"]
    down_images = []

    def __init__(self):
        pg.sprite.Sprite.__init__(self, self.containers)
        self.image = self.down_images[1]
        self.left_images = ["_"] + self.left_images
        self.right_images = ["_"] + self.right_images
        self.up_images = ["_"] + self.up_images
        self.down_images = ["_"] + self.down_images
        self.rect = self.image.get_rect(midbottom=SCREENRECT.center)
        self.origtop = self.rect.top
        self.foot = 10
        self.foot_index = 1
        self.room_rect = SCREENRECT

    def move_left_right(self, direction):
        self.rect.move_ip(direction * self.speed, 0)
        # print(self.rect)
        self.rect = self.rect.clamp(self.room_rect)
        if self.foot == 0:
            self.foot_index *= -1
            self.foot = 10

        if direction < 0:
            self.image = self.left_images[self.foot_index]
            self.foot -= 1
        elif direction > 0:
            self.image = self.right_images[self.foot_index]
            self.foot -= 1

    def move_up_down(self, direction):
        self.rect.move_ip(0, direction * self.speed)
        self.rect = self.rect.clamp(self.room_rect)

        if self.foot == 0:
            self.foot_index *= -1
            self.foot = 10

        if direction < 0:
            self.image = self.up_images[self.foot_index]
            self.foot -= 1
        elif direction > 0:
            self.image = self.down_images[self.foot_index]
            self.foot -= 1


class GameState:
    player = None

    def __init__(self, player):
        self.player = player


def handle_keyboard(state):
    for e in pg.event.get():
        if e.type == pg.QUIT:
            return False

    keystate = pg.key.get_pressed()
    dir_left_right = keystate[pg.K_RIGHT] - keystate[pg.K_LEFT]
    state.player.move_left_right(dir_left_right)
    updown = keystate[pg.K_DOWN] - keystate[pg.K_UP]
    state.player.move_up_down(updown)
    return True


class Furniture(pg.sprite.Sprite):
    def __init__(self, image_name, room_top_left=None):
        pg.sprite.Sprite.__init__(self, self.containers)
        img = load_image(image_name, scene=True)
        self.image = pg.transform.scale(img, (40, 40))

        if room_top_left is None:
            room_top_left = (0, 0)
        x = room_top_left[0] + 50
        self.rect = self.image.get_rect(centery=x, centerx=x)
        # self.rect = self.image.get_rect(midbottom=50)


def render_bedroom(screen, floor):
    carpet_tile = load_image("floor_green.png", scene=True)
    carpet_tile = pg.transform.scale(carpet_tile, (8, 5))
    width, height = int(SCREENRECT.width / 1.5), int(SCREENRECT.height / 1.5)
    top_left = (
        int(width / 6),
        int(height / 6),
    )  # (int(SCREENRECT.width / 4), int(SCREENRECT.height / 4))
    room_surface = pg.Surface((width, height))
    for x in range(0, width, carpet_tile.get_width()):
        for y in range(0, height, carpet_tile.get_height()):
            room_surface.blit(carpet_tile, (x, y))

    bed = Furniture("bed.png", room_top_left=top_left)
    room_rect = screen.blit(room_surface, top_left)
    return room_surface, room_rect


def main():
    pg.init()

    winstyle = pg.SCALED
    bestdepth = pg.display.mode_ok(SCREENRECT.size, winstyle, 32)
    screen = pg.display.set_mode(SCREENRECT.size, winstyle, bestdepth)
    background = pg.Surface(SCREENRECT.size)

    render_group = pg.sprite.RenderUpdates()

    for i in ["left", "right", "up", "down"]:
        setattr(
            Player,
            f"{i}_images",
            [load_image(name) for name in getattr(Player, f"{i}_names")],
        )
    Player.containers = render_group
    Furniture.containers = render_group

    clock = pg.time.Clock()
    pg.display.update()
    player = Player()
    game_state = GameState(player)
    screen.fill(BACKGROUND_COLOR)
    # room_surface = render_bedroom(screen, background)
    # player.room_rect = room_surface.get_rect()
    room_surface, player.room_rect = render_bedroom(screen, background)
    room_background = pg.Surface(player.room_rect.size)
    should_continue = True

    def clear_callback(surf, rect):
        carpet_tile = load_image("floor_green.png", scene=True)
        carpet_tile = pg.transform.scale(carpet_tile, (8, 5))
        for x in range(rect.width):
            for y in range(rect.height):
                surf.blit(carpet_tile(x, y))

    while player.alive() and should_continue:
        # render_group.clear = clear_callback
        room_surface, player.room_rect = render_bedroom(screen, background)

        # render_group.clear(screen, background)
        render_group.clear(room_surface, screen)
        render_group.update()

        should_continue = handle_keyboard(game_state)
        dirty = render_group.draw(screen)
        pg.display.update(dirty)
        clock.tick(FPS)


if __name__ == "__main__":
    main()
