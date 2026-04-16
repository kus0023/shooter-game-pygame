import pygame, random
from constants import *
from sprite_group import *
from assets import player_shot_fx, enemy_shot_fx
from bullet import Bullet
from grenade import Grenade
from assets import get_animation_dict


class Soldier(pygame.sprite.Sprite):
    def __init__(self, char_type, x, y, scale, speed, ammo, grenade_count=5):
        pygame.sprite.Sprite.__init__(self)
        # character properties
        self.char_type = char_type
        self.is_alive = True

        # movement properties
        self.speed = speed
        self.direction = 1
        self.flip = False

        # jump propterties
        self.jump = False
        self.vel_y = 0
        self.in_air = True

        # bullet propeties
        self.shoot_cooldown = 0
        self.ammo = ammo
        self.max_ammo = ammo

        # health properties
        self.health = 100
        self.max_health = self.health

        # grenade properties
        self.grenades = grenade_count
        self.max_grenades = self.grenades

        # Bot movement
        self.start_pos = x
        self.is_idle = False
        self.rest_time = pygame.time.get_ticks()
        self.player_detection_distance = TILE_SIZE * 2
        self.dead_body_removal_time = 60

        # animation properties
        self.animation_dict = get_animation_dict(scale, char_type)
        self.action = "Idle"
        self.frame_index = 0
        self.update_time = pygame.time.get_ticks()

        # image properties
        self.image: pygame.Surface = self.animation_dict[self.action][self.frame_index]
        self.rect: pygame.Rect = self.image.get_rect()
        self.rect.center = (x, y)

    def update(self):
        self.update_animation()
        self.check_alive()
        # update shoot cooldown
        if self.shoot_cooldown > 0:
            self.shoot_cooldown -= 1

        # player die
        if not self.is_alive:
            # if dead animation is done then kill the object
            if self.frame_index >= len(self.animation_dict["Death"]) - 1:
                if self.dead_body_removal_time < 0:
                    self.kill()
                else:
                    self.dead_body_removal_time -= 1

    def move(self, moving_left, moving_right, world):
        screen_scroll = 0
        dx = 0
        dy = 0

        if moving_left:
            dx = -self.speed
            self.flip = True
            self.direction = -1
        if moving_right:
            dx = self.speed
            self.flip = False
            self.direction = 1
        if moving_left and moving_right:
            dx = 0

        # Jump
        if self.jump and not self.in_air:
            self.jump = False
            self.vel_y = -11
            self.in_air = True
        # gravity
        self.vel_y += GRAVITY
        if self.vel_y > 10:
            self.vel_y = 10
        dy += self.vel_y

        # collision on ground
        width = self.image.get_width()
        height = self.image.get_height()
        for tile in world.obstacle_list:
            # collision in horizontal direction
            if tile[1].colliderect(dx + self.rect.x, self.rect.y, width, height):
                dx = 0
                if self.char_type == "enemy":
                    self.direction *= -1
            # collision in vertical direction
            if tile[1].colliderect(self.rect.x, self.rect.y + dy, width, height):
                dy = 0
                # if jumping - below tile
                if self.vel_y < 0:
                    self.vel_y = 0
                    dy = tile[1].bottom - self.rect.top
                elif self.vel_y >= 0:  # falling - above ground
                    self.vel_y = 0
                    dy = tile[1].top - self.rect.bottom
                    self.in_air = False

        # update scroll as player move
        if self.char_type == "player":
            if (
                self.rect.right > SCREEN_WIDTH - SCROLL_THRESH
                and bg_scroll < world.level_length * TILE_SIZE - SCREEN_WIDTH
                or self.rect.left < SCROLL_THRESH
                and bg_scroll > abs(dx)
            ):
                self.rect.x -= dx
                screen_scroll = -dx

            # stop player if going outside screen
            if self.rect.left + dx < 0 or self.rect.right + dx > SCREEN_WIDTH:
                dx = 0

        # check for collision with water
        if pygame.sprite.spritecollide(self, water_group, False):
            self.health = 0

        # check for collision with exit
        level_complete = False
        if pygame.sprite.spritecollide(self, exit_group, False):
            level_complete = True

        # check if fallen off the map
        if self.rect.centery + dy > SCREEN_HEIGHT:
            self.health = 0

        self.rect.x += dx
        self.rect.y += dy
        return (screen_scroll, level_complete)

    def shoot(self):
        if self.shoot_cooldown == 0 and self.ammo > 0:
            self.shoot_cooldown = 20

            # this value because bullet should not hit shooter player itself when created
            self_harm_protection = 10

            # create bullet in right if player is facing right or moving right
            # else create bullete in left
            x = self.rect.right if self.direction == 1 else self.rect.left
            self_harm_protection = (
                self_harm_protection if self.direction == 1 else -self_harm_protection
            )
            bullet = Bullet(x + self_harm_protection, self.rect.centery, self.direction)
            bullet_group.add(bullet)
            self.ammo -= 1
            if self.char_type == "player":
                player_shot_fx.play()
            if self.char_type == "enemy":
                enemy_shot_fx.play()

    def throw_grenade(self):
        if self.grenades > 0:
            grenade = Grenade(self.rect.centerx, self.rect.centery, self.direction)
            grenade_group.add(grenade)
            self.grenades -= 1

    def bot_movement(self, player, world, screen_scroll):

        self.rect.x += screen_scroll
        if self.is_alive:
            self.start_pos += screen_scroll

            # check if player is in sight meaning in front of enemy at certain distance
            # if so, Stop the enemy and shoot in direction of player
            size = (self.player_detection_distance, 1)
            temp_rect = pygame.Rect((0, 0), size)
            if self.direction == 1:
                temp_rect.midleft = self.rect.midright
            else:
                temp_rect.midright = self.rect.midleft

            if player.rect.colliderect(temp_rect) and player.is_alive:
                self.move(False, False, world)
                self.shoot()
                self.update_action("Idle")
                return  # don't Run the below code Just stop and shoot

            # choose random time from 1 to 15 second
            # then either move the bot or stop the bot
            if pygame.time.get_ticks() - self.rest_time > random.randint(1000, 5000):
                self.rest_time = pygame.time.get_ticks()
                if not self.is_idle:  # if moving then stop the bot
                    self.is_idle = True
                else:  # if not moving then move the bot in random direction
                    self.direction = random.choice([1, -1])
                    self.is_idle = False

            # move to and fro in certain distance
            if self.direction == 1:  # moving Right
                if abs(self.rect.right - self.start_pos) >= TILE_SIZE * 3:
                    self.direction *= -1
            if self.direction == -1:  # moving Left
                if abs(self.rect.left - self.start_pos) >= TILE_SIZE * 3:
                    self.direction *= -1

            # control the animation
            if self.is_idle:
                self.move(False, False, world)
                self.update_action("Idle")
            elif self.direction == 1:
                self.move(False, True, world)
                self.update_action("Run")
            elif self.direction == -1:
                self.move(True, False, world)
                self.update_action("Run")

            self.rest_time += 1

    def update_action(self, new_action: str):
        if new_action not in self.animation_dict.keys():
            raise Exception(f"new_action={new_action} is not a valid action")
        if new_action != self.action:
            self.action = new_action
            self.frame_index = 0
            self.image = self.animation_dict[self.action][self.frame_index]

    def update_animation(self):
        ANIMATION_COOLDOWN = 100
        self.image = self.animation_dict[self.action][self.frame_index]
        if pygame.time.get_ticks() - self.update_time > ANIMATION_COOLDOWN:
            self.update_time = pygame.time.get_ticks()
            self.frame_index += 1
            length = len(self.animation_dict[self.action])
            if self.frame_index == length:
                if self.action == "Death":
                    self.frame_index = length - 1
                else:
                    self.frame_index %= length

    def check_alive(self):
        if self.health <= 0:
            self.health = 0
            self.speed = 0
            self.is_alive = False
            self.update_action("Death")

    def draw_health_bar(self, screen):
        # Health Bar
        border = pygame.Surface(((self.rect.width + 4), 14))
        border.fill(BLACK)
        health_bg_surf = pygame.Surface((self.rect.width, 10))
        health_bg_surf.fill(RED)
        ratio = self.health / self.max_health
        health_surf = pygame.Surface((self.rect.width * ratio, 10))
        health_surf.fill(GREEN)
        health_rect = health_bg_surf.get_rect()
        health_rect.bottomleft = self.rect.topleft
        x = health_rect.x - 2
        y = health_rect.y - 2
        screen.blit(border, (x, y))
        screen.blit(health_bg_surf, health_rect)
        screen.blit(health_surf, health_rect)

    def draw(self, screen):
        img = pygame.transform.flip(self.image, self.flip, False)
        screen.blit(img, self.rect)
        self.draw_health_bar(screen)
