import pygame
from assets import bullet_img
from constants import SCREEN_WIDTH
from sprite_group import bullet_group, enemy_group


class Bullet(pygame.sprite.Sprite):
    def __init__(self, x, y, direction):
        pygame.sprite.Sprite.__init__(self)
        self.speed = 10
        self.image = bullet_img
        self.rect = self.image.get_rect()
        self.rect.center = (x, y)
        self.direction = direction

    def update(self, world, screen_scroll, player):
        self.rect.x += self.speed * self.direction + screen_scroll
        # check if bullet is off the screen then destory it
        if self.rect.right < 0 or self.rect.left > SCREEN_WIDTH:
            self.kill()

        # collision with obstacle tiles
        for tile in world.obstacle_list:
            # collision in horizontal direction
            if tile[1].colliderect(self.rect):
                self.kill()

        # collision with characters
        if pygame.sprite.spritecollide(player, bullet_group, False):
            if player.is_alive:
                player.health -= 5
                self.kill()

        for enemy in enemy_group:
            if pygame.sprite.spritecollide(enemy, bullet_group, False):
                if enemy.is_alive:
                    enemy.health -= 25
                    self.kill()
