import pygame as pg
from pygame.locals import *
import os

SCREENRECT = pg.Rect(0, 0, 640, 480)
BACKGROUND_COLOR = (0, 0, 255)
FPS = 60
main_dir = os.path.split(os.path.abspath(__file__))[0]


def load_image(file):
    """ loads an image, prepares it for play
    """
    file = os.path.join(main_dir, "assets/sprites", file)
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

    def move_left_right(self, direction):
        self.rect.move_ip(direction * self.speed, 0)
        self.rect = self.rect.clamp(SCREENRECT)
        if self.foot == 0:
            print(self.foot)
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
        self.rect = self.rect.clamp(SCREENRECT)

        print(f"dir: {direction} - foot_index {self.foot_index}")

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
    _ = ["_" for _ in pg.event.get()]

    keystate = pg.key.get_pressed()
    dir_left_right = keystate[pg.K_RIGHT] - keystate[pg.K_LEFT]
    state.player.move_left_right(dir_left_right)
    updown = keystate[pg.K_DOWN] - keystate[pg.K_UP]
    state.player.move_up_down(updown)


def main():
    winstyle = 0  # TODO: Remove or explain why needed
    pg.init()

    bestdepth = pg.display.mode_ok(SCREENRECT.size, winstyle, 32)
    background = pg.Surface(SCREENRECT.size)
    screen = pg.display.set_mode(SCREENRECT.size, winstyle, bestdepth)
    screen.fill(BACKGROUND_COLOR)

    render_group = pg.sprite.RenderUpdates()

    for i in ["left", "right", "up", "down"]:
        setattr(
            Player,
            f"{i}_images",
            [load_image(name) for name in getattr(Player, f"{i}_names")],
        )
    Player.containers = render_group

    clock = pg.time.Clock()
    pg.display.update()
    player = Player()
    game_state = GameState(player)
    while player.alive():
        render_group.clear(screen, background)
        render_group.update()

        handle_keyboard(game_state)
        screen.fill(BACKGROUND_COLOR)
        dirty = render_group.draw(screen)
        pg.display.update(dirty)
        clock.tick(FPS)


if __name__ == "__main__":
    main()
