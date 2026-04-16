import pygame, csv, button
from pygame import mixer
from constants import *

mixer.init()
pygame.init()

screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Shooter Game")

from decorations import Decorations, Water, Exit
from item_box import ItemBox
from assets import *
from world import World
from sprite_group import *
from ui import AmmoUI
from transition import *

# Frame rate
clock = pygame.time.Clock()


def draw_bg():
    screen.fill(BG)
    width = sky_img.get_width()
    for x in range(5):
        pos_x = (x * width) - bg_scroll * 0.5
        screen.blit(sky_img, (pos_x, 0))
        pos_x = (x * width) - bg_scroll * 0.6
        screen.blit(
            mountain_img, (pos_x, SCREEN_HEIGHT - mountain_img.get_height() - 300)
        )
        pos_x = (x * width) - bg_scroll * 0.7
        screen.blit(pine1_img, (pos_x, SCREEN_HEIGHT - pine1_img.get_height() - 150))
        pos_x = (x * width) - bg_scroll * 0.8
        screen.blit(pine2_img, (pos_x, SCREEN_HEIGHT - pine2_img.get_height()))


def reset_level():
    enemy_group.empty()
    bullet_group.empty()
    grenade_group.empty()
    explosion_group.empty()
    item_box_group.empty()
    decoration_group.empty()
    water_group.empty()
    exit_group.empty()


def load_level(level):
    world_data = []
    with open(level_path(level), mode="r", newline="") as csvfile:
        reader = csv.reader(csvfile, delimiter=",")
        prev = reader.line_num
        # copy all rows list
        for row in reader:
            world_data.append(row)
        # conver string data into int
        world_data = [[int(c) for c in r] for r in world_data]

        world = World()
        player = world.process_data(world_data)
    return world, player


# create button
start_btn = button.Button(
    SCREEN_WIDTH // 2 - 130, SCREEN_HEIGHT // 2 - 150, start_btn_img, 1
)
exit_btn = button.Button(
    SCREEN_WIDTH // 2 - 110, SCREEN_HEIGHT // 2 + 50, exit_btn_img, 1
)
restart_btn = button.Button(
    SCREEN_WIDTH // 2 - 100, SCREEN_HEIGHT // 2 - 50, restart_btn_img, 2
)

ammo_ui = AmmoUI()

# Load level
world, player = load_level(level)


death_fade = ScreenFade(ScreenFadeType.TOP_TO_DOWN_CLOSE, "pink", 15)
intro_transition = ScreenFade(ScreenFadeType.MIDDLE_SQUARE_OPEN, "black", 10)
run = True
while run:
    clock.tick(45)

    if start_game == False:
        # main menu
        screen.fill(BG)
        if start_btn.draw(screen):
            start_game = True
            start_intro_transition = True

        if exit_btn.draw(screen):
            run = False

    else:
        draw_bg()
        world.draw(screen, screen_scroll)
        decoration_group.update(screen_scroll)
        decoration_group.draw(screen)

        enemy_group.update()
        for enemy in enemy_group:
            enemy.bot_movement(player, world, screen_scroll)
            enemy.draw(screen)

        bullet_group.update(world, screen_scroll, player)
        bullet_group.draw(screen)

        grenade_group.update(world, player, screen_scroll)
        grenade_group.draw(screen)

        explosion_group.update(screen_scroll)
        explosion_group.draw(screen)
        item_box_group.update(player, screen_scroll)
        item_box_group.draw(screen)

        ammo_ui.draw(screen, player)
        player.update()
        player.draw(screen)
        if player.is_alive:
            # shoot bullets
            if shoot:
                player.shoot()
            elif grenade:
                player.throw_grenade()
                grenade = False
            if player.in_air:
                player.update_action("Jump")
            elif moving_left and moving_right:
                player.update_action("Idle")
            elif (moving_left or moving_right) and not player.in_air:
                player.update_action("Run")
            else:
                player.update_action("Idle")

            screen_scroll, level_complete = player.move(
                moving_left, moving_right, world
            )
            bg_scroll -= screen_scroll

            # check if player has completed the level
            if level_complete:
                start_intro_transition = True
                level += 1
                if level > MAX_LEVEL:
                    print("All level completed.")
                    run = False
                bg_scroll = 0
                reset_level()
                world, player = load_level(level)
        else:  # player is not alive show restart button
            screen_scroll = 0

            if death_fade.fade(screen):
                reset = restart_btn.draw(screen)

                if reset == True:
                    death_fade.fade_counter = 0
                    start_intro_transition = True
                    bg_scroll = 0
                    world_data = []
                    reset_level()
                    world, player = load_level(level)

    if start_intro_transition:
        if intro_transition.fade(screen):
            start_intro_transition = False
            intro_transition.fade_counter = 0

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            run = False

        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_a:
                moving_left = True
            if event.key == pygame.K_d:
                moving_right = True
            if event.key == pygame.K_SPACE:
                shoot = True
            if event.key == pygame.K_f:
                grenade = True
            if event.key == pygame.K_w and player.is_alive:
                player.jump = True
                jump_fx.play()
        if event.type == pygame.KEYUP:
            if event.key == pygame.K_a:
                moving_left = False
            if event.key == pygame.K_d:
                moving_right = False
            if event.key == pygame.K_SPACE:
                shoot = False

    pygame.display.update()

pygame.quit()
