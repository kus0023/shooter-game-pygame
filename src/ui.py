import pygame
from constants import DARK_GREEN, WHITE
from assets import FONT_FUTURA
from soldier import Soldier


class AmmoUI(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.image = pygame.Surface((100, 50))
        self.image.fill(DARK_GREEN)
        self.rect = self.image.get_rect()
        self.rect.topleft = (10, 10)

    def draw(self, screen, soldier: Soldier):
        self.image.fill(DARK_GREEN)
        padding = 5
        # create surface for bullets
        bullet_surf = FONT_FUTURA.render(f"Bullet: {soldier.ammo}", True, WHITE)

        # create surface for grenades
        grenade_surf = FONT_FUTURA.render(f"Grenades: {soldier.grenades}", True, WHITE)

        self.image.blits(
            [
                (bullet_surf, (padding, padding)),
                (grenade_surf, (padding, padding + bullet_surf.get_rect().bottom)),
            ]
        )
        screen.blit(self.image, self.rect)
