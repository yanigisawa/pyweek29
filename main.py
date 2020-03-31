import pygame as pg
from pygame.locals import *
import os
from datetime import datetime


SCREENRECT = pg.Rect(0, 0, 640, 480)
BACKGROUND_COLOR = (0, 0, 0)
FPS = 60
main_dir = os.path.split(os.path.abspath(__file__))[0]


def load_image(file, scene=False, scale_tuple=None):
    """ loads an image, prepares it for play
    """
    path = "assets/sprites"
    if scene:
        path = "assets/scenes"
    file = os.path.join(main_dir, path, file)
    try:
        surface = pg.image.load(file)
        if scale_tuple is not None and len(scale_tuple) == 2:
            surface = pg.transform.scale(surface, scale_tuple)
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
        if self.foot == 0:
            self.foot_index *= -1
            self.foot = 10
            if self.take_step is not None:
                self.take_step()

        if direction < 0:
            if not self.can_move_left():
                return
            self.image = self.left_images[self.foot_index]
            self.foot -= 1
        elif direction > 0:
            if not self.can_move_right():
                return
            self.image = self.right_images[self.foot_index]
            self.foot -= 1

        self.rect.move_ip(direction * self.speed, 0)
        self.rect = self.rect.clamp(self.room_rect)
        self.door_collision()

    def move_up_down(self, direction):
        if self.foot == 0:
            self.foot_index *= -1
            self.foot = 10
            if self.take_step is not None:
                self.take_step()

        if direction < 0:
            if not self.can_move_up():
                return
            self.image = self.up_images[self.foot_index]
            self.foot -= 1
        elif direction > 0:
            if not self.can_move_down():
                return
            self.image = self.down_images[self.foot_index]
            self.foot -= 1

        self.rect.move_ip(0, direction * self.speed)
        self.rect = self.rect.clamp(self.room_rect)
        self.door_collision()


class GameState:
    player = None
    noise_level = 0
    last_step_taken = datetime.now()
    furniture = {}
    doors = {}

    def __init__(self):
        self.preload_images()
        self.player = Player()
        self.player.can_move_left = self.can_move_left
        self.player.can_move_right = self.can_move_right
        self.player.can_move_up = self.can_move_up
        self.player.can_move_down = self.can_move_down
        self.player.door_collision = self.door_collision
        self.player.take_step = self.step_taken
        self.font = pg.font.SysFont(None, 30)
        self.avoid_rects = []

    def door_collision(self):
        rect_tuples = [d for _, d in self.doors.items()]
        collide_index = self.player.rect.collidelist([r[0] for r in rect_tuples])
        if collide_index != -1:
            rect_tuples[collide_index][1]()

    def can_move_left(self):
        p_rect = pg.Rect(self.player.rect)
        p_rect.left -= self.player.speed
        rects = [s.rect for _, s in self.furniture.items()]
        if p_rect.collidelist(rects) != -1:
            return False
        return True

    def can_move_right(self):
        p_rect = pg.Rect(self.player.rect)
        p_rect.left += self.player.speed
        rects = [s.rect for _, s in self.furniture.items()]
        if p_rect.collidelist(rects) != -1:
            return False
        return True

    def can_move_up(self):
        p_rect = pg.Rect(self.player.rect)
        p_rect.top -= self.player.speed
        rects = [s.rect for _, s in self.furniture.items()]
        if p_rect.collidelist(rects) != -1:
            return False
        return True

    def can_move_down(self):
        p_rect = pg.Rect(self.player.rect)
        p_rect.top += self.player.speed
        rects = [s.rect for _, s in self.furniture.items()]
        if p_rect.collidelist(rects) != -1:
            return False
        return True

    def step_taken(self):
        self.last_step_taken = datetime.now()
        if self.noise_level >= 100:
            return
        self.noise_level += 10

    def preload_images(self):
        self.load_bedroom_images()
        self.load_player_images()

    def load_player_images(self):
        for i in ["left", "right", "up", "down"]:
            setattr(
                Player,
                f"{i}_images",
                [
                    load_image(name, scale_tuple=(30, 30))
                    for name in getattr(Player, f"{i}_names")
                ],
            )

    def load_bedroom_images(self):
        self.bedroom_images = {}
        carpet_tile = load_image("floor_green.png", scene=True)
        carpet_tile = pg.transform.scale(carpet_tile, (8, 5))
        self.bedroom_images["carpet_tile"] = carpet_tile
        width, height = int(SCREENRECT.width / 1.5), int(SCREENRECT.height / 1.5)
        self.bedroom = {
            "width": width,
            "height": height,
            "top_left": (int(width / 6), int(height / 6),),
        }
        bed = Furniture("bed.png", room_top_left=self.bedroom["top_left"])
        desk = Furniture("desk.png", room_top_left=self.bedroom["top_left"])
        desk.rect.left = self.bedroom["top_left"][0] + 100
        desk.rect.top = self.bedroom["top_left"][1] + 10
        self.furniture["bed"] = bed
        self.furniture["desk"] = desk

    def reduce_noise_level(self):
        now = datetime.now()
        if (now - self.last_step_taken).total_seconds() > 2 and self.noise_level > 0:
            self.noise_level -= 10
            self.last_step_taken = now

    def render(self, screen, background):
        self.reduce_noise_level()
        self.render_noise(screen)
        return self.render_bedroom(screen, background)

    def render_noise(self, screen):
        t = self.font.render("Noise: ", 1, (255, 255, 255))
        t_rect = t.get_rect()
        t_rect.topleft = (10, 10)
        screen.blit(t, t_rect)
        score_box = pg.Surface((100, 20))
        current_noise = score_box.get_rect()
        current_noise.width = self.noise_level
        score_box.fill((255, 255, 255), rect=current_noise)
        pg.draw.rect(score_box, pg.Color(255, 0, 0), (0, 0, 100, 20), 2)
        screen.blit(score_box, (t_rect.width + 20, 10))

    def move_to_hallway(self):

        print("render hallway")

    def render_bedroom(self, screen, floor):
        carpet_tile = self.bedroom_images["carpet_tile"]
        width, height = self.bedroom["width"], self.bedroom["height"]
        top_left = self.bedroom["top_left"]

        room_surface = pg.Surface((width, height))
        for x in range(SCREENRECT.left, width, carpet_tile.get_width()):
            for y in range(SCREENRECT.top, height, carpet_tile.get_height()):
                room_surface.blit(carpet_tile, (x, y))

        room_rect = room_surface.get_rect()
        # room_rect.top, room_rect.left = top_left[0], top_left[1]
        door = pg.Rect(0, 0, 45, 10)
        door.midbottom = room_rect.midbottom
        pg.draw.rect(room_surface, pg.Color(101, 67, 33), door)
        # door.fill((101, 67, 33))
        # room_surface.blit(door, door)
        room_rect = screen.blit(room_surface, top_left)
        self.doors["bottom"] = (door, self.move_to_hallway)
        return room_surface, room_rect


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
    def __init__(self, image_name, room_top_left=None, scale=None):
        pg.sprite.Sprite.__init__(self, self.containers)
        img = load_image(image_name, scene=True)
        self.image = img
        if scale is not None:
            self.image = pg.transform.scale(img, scale)

        if room_top_left is None:
            room_top_left = (0, 0)
        x = room_top_left[0] + 50
        self.rect = self.image.get_rect(centery=x, centerx=x)
        # self.rect = self.image.get_rect(midbottom=50)


def main():
    pg.init()

    winstyle = pg.SCALED
    bestdepth = pg.display.mode_ok(SCREENRECT.size, winstyle, 32)
    screen = pg.display.set_mode(SCREENRECT.size, winstyle, bestdepth)
    background = pg.Surface(SCREENRECT.size)

    render_group = pg.sprite.RenderUpdates()

    Player.containers = render_group
    Furniture.containers = render_group

    clock = pg.time.Clock()
    pg.display.update()

    game_state = GameState()
    game_state.render(screen, background)
    screen.fill(BACKGROUND_COLOR)
    # room_surface = render_bedroom(screen, background)
    # player.room_rect = room_surface.get_rect()
    should_continue = True

    while game_state.player.alive() and should_continue:
        room_surface, game_state.player.room_rect = game_state.render(
            screen, background
        )

        # render_group.clear(screen, background)
        render_group.clear(room_surface, screen)
        render_group.update()

        should_continue = handle_keyboard(game_state)
        dirty = render_group.draw(screen)
        pg.display.update(dirty)
        clock.tick(FPS)


if __name__ == "__main__":
    main()
