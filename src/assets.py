import pygame
from constants import TILE_SIZE, TILE_TYPES
from pathlib import Path

base = Path("assets")
img_path = base.joinpath("img")
audio_path = base.joinpath("audio")
# images
start_btn_img = pygame.image.load(img_path.joinpath("start_btn.png")).convert_alpha()
exit_btn_img = pygame.image.load(img_path.joinpath("exit_btn.png")).convert_alpha()
restart_btn_img = pygame.image.load(
    img_path.joinpath("restart_btn.png")
).convert_alpha()


bullet_img = pygame.image.load(img_path.joinpath("icons", "bullet.png")).convert_alpha()
grenade_img = pygame.image.load(
    img_path.joinpath("icons", "grenade.png")
).convert_alpha()
health_box_img = pygame.image.load(
    img_path.joinpath("icons", "health_box.png")
).convert_alpha()
ammo_box_img = pygame.image.load(
    img_path.joinpath("icons", "ammo_box.png")
).convert_alpha()
grenade_box_img = pygame.image.load(
    img_path.joinpath("icons", "grenade_box.png")
).convert_alpha()

item_boxes = {
    "Health": health_box_img,
    "Ammo": ammo_box_img,
    "Grenade": grenade_box_img,
}

# Tiles
tile_img_list = []
for i in range(TILE_TYPES):
    img = pygame.image.load(img_path.joinpath("tile", f"{i}.png")).convert_alpha()
    img = pygame.transform.scale(img, (TILE_SIZE, TILE_SIZE))
    tile_img_list.append(img)
pine1_img = pygame.image.load(
    img_path.joinpath("background", "pine1.png")
).convert_alpha()
pine2_img = pygame.image.load(
    img_path.joinpath("background", "pine2.png")
).convert_alpha()
mountain_img = pygame.image.load(
    img_path.joinpath("background", "mountain.png")
).convert_alpha()
sky_img = pygame.image.load(
    img_path.joinpath("background", "sky_cloud.png")
).convert_alpha()

# Font
FONT_FUTURA = pygame.font.SysFont("futurawindows", 16)


# load music and sound
pygame.mixer.music.load(audio_path.joinpath("music2.mp3"))
pygame.mixer.music.set_volume(0.3)
pygame.mixer.music.play(-1, 0.0, 5000)

jump_fx = pygame.mixer.Sound(audio_path.joinpath("jump.wav"))
jump_fx.set_volume(0.5)
grenade_fx = pygame.mixer.Sound(audio_path.joinpath("grenade.wav"))
grenade_fx.set_volume(0.5)
player_shot_fx = pygame.mixer.Sound(audio_path.joinpath("shot.wav"))
player_shot_fx.set_volume(0.6)
enemy_shot_fx = pygame.mixer.Sound(audio_path.joinpath("shot.wav"))
enemy_shot_fx.set_volume(0.3)


# level path
def level_path(level):
    return base.joinpath(f"level{level}_data.csv")


animations = {}


# get animations
def get_animation_dict(scale: int, char_type):
    global animations
    if animations.get(char_type, None):
        return animations[char_type]
    # It will create a dictionary of all images I have for all the actions
    # for example
    # animation_dict = { "idle": [images...], "run": [images..], ...so on}
    animation_dict = {}

    # generic function to load all images of action and add it to dictionary
    def load_image_from_asset(name, size, scale=scale):
        animation_dict[name] = list()
        for i in range(size):
            path = img_path.joinpath(char_type, name, f"{i}.png")
            img = pygame.image.load(path).convert_alpha()
            # scale up the image
            width = int(img.get_width() * scale)
            height = int(img.get_height() * scale)
            img = pygame.transform.scale(img, (width, height))
            # add to dictionary
            animation_dict[name].append(img)

    load_image_from_asset("Idle", 5)
    load_image_from_asset("Death", 8)
    load_image_from_asset("Jump", 1)
    load_image_from_asset("Run", 6)

    animations[char_type] = animation_dict

    return animation_dict


explosion_list = None


def explosion_animation_list():
    global explosion_list
    if explosion_list != None:
        return explosion_list
    list = []
    for i in range(1, 6):
        path = img_path.joinpath("explosion", f"exp{i}.png")
        img = pygame.image.load(path).convert_alpha()
        list.append(img)
    explosion_list = list
    return explosion_list
