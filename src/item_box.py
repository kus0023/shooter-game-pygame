import pygame
from constants import TILE_SIZE
from assets import item_boxes


class ItemBox(pygame.sprite.Sprite):
    def __init__(self, item_type, x, y):
        pygame.sprite.Sprite.__init__(self)
        self.item_type = item_type
        self.image: pygame.Surface = item_boxes[self.item_type]
        self.rect = self.image.get_rect()
        self.rect.midtop = (x + TILE_SIZE // 2, y + (TILE_SIZE - self.image.height))

    def update(self, player, screen_scroll):
        if pygame.sprite.collide_rect(self, player):
            if self.item_type == "Health":
                player.health = min(player.health + 25, player.max_health)
            if self.item_type == "Ammo":
                player.ammo = min(player.ammo + 15, player.max_ammo)
            if self.item_type == "Grenade":
                player.grenades = min(player.grenades + 5, player.max_grenades)

            self.kill()
        self.rect.x += screen_scroll
