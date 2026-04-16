import pygame
from constants import GRAVITY, TILE_SIZE
from assets import grenade_fx, grenade_img, explosion_animation_list
from sprite_group import explosion_group, enemy_group


class Grenade(pygame.sprite.Sprite):
    def __init__(self, x, y, direction):
        pygame.sprite.Sprite.__init__(self)
        self.speed = 7
        self.vel_y = -11
        self.explode_timer = 100
        self.image = grenade_img
        self.rect = self.image.get_rect()
        self.rect.center = (x, y)
        self.direction = direction

    def update(self, world, player, screen_scroll):
        self.vel_y += GRAVITY
        dx = self.direction * self.speed + screen_scroll
        dy = self.vel_y

        # check collision with ground
        width = self.image.get_width()
        height = self.image.get_height()
        for tile in world.obstacle_list:
            # collision in horizontal direction
            if tile[1].colliderect(dx + self.rect.x, self.rect.y, width, height):
                self.direction *= -1
                dx = self.direction * self.speed
            # collision in vertical direction
            if tile[1].colliderect(self.rect.x, self.rect.y + dy, width, height):
                self.speed = 0
                # if throwing - means below tile
                if self.vel_y < 0:
                    self.vel_y = 0
                    dy = tile[1].bottom - self.rect.top
                elif self.vel_y >= 0:  # falling - above ground
                    self.vel_y = 0
                    dy = tile[1].top - self.rect.bottom

        self.rect.x += dx
        self.rect.y += dy

        # explode grenade
        self.explode_timer -= 1
        if self.explode_timer <= 0:
            grenade_fx.play()
            self.kill()
            explosion = Explosion(self.rect.centerx, self.rect.centery)
            explosion_group.add(explosion)
            # do damage to player if nearby
            max_distance = TILE_SIZE * 2
            distance_x = abs(self.rect.centerx - player.rect.centerx)
            distance_y = abs(self.rect.centery - player.rect.centery)
            if distance_x < max_distance and distance_y < max_distance:
                player.health -= 30

            # do damage to enemies if nearby
            for enemy in enemy_group:
                distance_x = abs(self.rect.centerx - enemy.rect.centerx)
                distance_y = abs(self.rect.centery - enemy.rect.centery)
                if distance_x < max_distance and distance_y < max_distance:
                    enemy.health -= 50


class Explosion(pygame.sprite.Sprite):
    def __init__(self, x, y):
        pygame.sprite.Sprite.__init__(self)
        self.frame_index = 0
        self.animation_update_time = pygame.time.get_ticks()
        self.images = explosion_animation_list()
        self.image = self.images[self.frame_index]
        self.rect = self.image.get_rect()
        self.rect.center = (x, y)

    def animation_update(self):
        ANIMATION_COOLDOWN = 50
        if pygame.time.get_ticks() - self.animation_update_time > ANIMATION_COOLDOWN:
            self.animation_update_time = pygame.time.get_ticks()
            self.image = self.images[self.frame_index]
            self.frame_index += 1
            self.frame_index %= len(self.images)

    def update(self, screen_scroll):
        self.rect.x += screen_scroll
        self.animation_update()
        if self.frame_index >= len(self.images) - 1:
            self.kill()
