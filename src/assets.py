import pygame
from constants import TILE_SIZE, TILE_TYPES

# images
start_btn_img = pygame.image.load("src/assets/img/start_btn.png").convert_alpha()
exit_btn_img = pygame.image.load("src/assets/img/exit_btn.png").convert_alpha()
restart_btn_img = pygame.image.load("src/assets/img/restart_btn.png").convert_alpha()


bullet_img = pygame.image.load("src/assets/img/icons/bullet.png").convert_alpha()
grenade_img = pygame.image.load("src/assets/img/icons/grenade.png").convert_alpha()
health_box_img = pygame.image.load(
    "src/assets/img/icons/health_box.png"
).convert_alpha()
ammo_box_img = pygame.image.load("src/assets/img/icons/ammo_box.png").convert_alpha()
grenade_box_img = pygame.image.load(
    "src/assets/img/icons/grenade_box.png"
).convert_alpha()

item_boxes = {
    "Health": health_box_img,
    "Ammo": ammo_box_img,
    "Grenade": grenade_box_img,
}

# Tiles
tile_img_list = []
for i in range(TILE_TYPES):
    img = pygame.image.load(f"src/assets/img/tile/{i}.png").convert_alpha()
    img = pygame.transform.scale(img, (TILE_SIZE, TILE_SIZE))
    tile_img_list.append(img)
pine1_img = pygame.image.load("src/assets/img/background/pine1.png").convert_alpha()
pine2_img = pygame.image.load("src/assets/img/background/pine2.png").convert_alpha()
mountain_img = pygame.image.load(
    "src/assets/img/background/mountain.png"
).convert_alpha()
sky_img = pygame.image.load("src/assets/img/background/sky_cloud.png").convert_alpha()

# Font
FONT_FUTURA = pygame.font.SysFont("futurawindows", 16)


# load music and sound
pygame.mixer.music.load("src/assets/audio/music2.mp3")
pygame.mixer.music.set_volume(0.3)
pygame.mixer.music.play(-1, 0.0, 5000)

jump_fx = pygame.mixer.Sound("src/assets/audio/jump.wav")
jump_fx.set_volume(0.5)
grenade_fx = pygame.mixer.Sound("src/assets/audio/grenade.wav")
grenade_fx.set_volume(0.5)
player_shot_fx = pygame.mixer.Sound("src/assets/audio/shot.wav")
player_shot_fx.set_volume(0.6)
enemy_shot_fx = pygame.mixer.Sound("src/assets/audio/shot.wav")
enemy_shot_fx.set_volume(0.3)
