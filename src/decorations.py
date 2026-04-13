import pygame


class Decorations(pygame.sprite.Sprite):
    def __init__(self, image: pygame.Surface, *groups, **position):
        super().__init__(*groups)
        self.image = image
        self.rect = self.image.get_rect(**position)

    def update(self, screen_scroll):
        self.rect.x += screen_scroll


class Water(Decorations):
    def __init__(self, image, *groups, **position):
        super().__init__(image, *groups, **position)


class Exit(Decorations):
    def __init__(self, image, *groups, **position):
        super().__init__(image, *groups, **position)
